# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
from __future__ import annotations

import threading
import traceback
import typing

import absl.app
import absl.flags
import fastapi
import torch
import transformers
import uvicorn
from absl import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

if typing.TYPE_CHECKING:
    from transformers import GenerationMixin, PreTrainedTokenizerBase


FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string("host", None, "Server host")

absl.flags.DEFINE_integer("port", 8000, "Server port")

absl.flags.DEFINE_string("model_name", None, "Name of HuggingFace model")

absl.flags.DEFINE_string(
    "model_revision", None, "Revision (commit hash) of HuggingFace model"
)

absl.flags.mark_flags_as_required(["model_name", "model_revision"])


class CausalLanguageModel:
    def __init__(
        self, device: str, tokenizer: PreTrainedTokenizerBase, model: GenerationMixin
    ):
        self._device = device
        self._tokenizer = tokenizer
        self._model = model

    def generate(self, prompt: str, **kwargs) -> list[dict]:
        # TODO: Support other tensor formats
        input_ids = self._tokenizer.encode(prompt, return_tensors="pt")
        input_tensor = input_ids.to(self._device)
        output_batch = self._model.generate(input_tensor, **kwargs)
        output_text = self._tokenizer.batch_decode(
            output_batch, skip_special_tokens=True
        )
        return [{"text": text} for text in output_text]


TIMEOUT_KEEP_ALIVE = 5  # seconds.
TIMEOUT_TO_PREVENT_DEADLOCK = 1  # seconds.
app = FastAPI()
event_ready = threading.Event()
event_error = threading.Event()
error_message: str | None = None
model: CausalLanguageModel | None = None


@app.get("/health")
async def health() -> Response:
    """Health check."""
    if event_error.is_set():
        return Response(
            error_message, status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    else:
        return Response(status_code=fastapi.status.HTTP_200_OK)


@app.get("/ready")
async def ready() -> Response:
    if event_ready.is_set():
        return Response(status_code=fastapi.status.HTTP_200_OK)
    elif event_error.is_set():
        return Response(
            error_message, status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    else:
        return Response(status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE)


async def get_request_json(request: Request) -> dict:
    return await request.json()


@app.post("/generate")
def generate(request_json: dict = fastapi.Depends(get_request_json)) -> Response:
    """Generate completion for the request.

    The request should be a JSON object with the following fields:
    - prompt: the prompt to use for the generation.
    - stream: whether to stream the results or not.
    - other fields: the sampling parameters (See `SamplingParams` for details).
    """
    if not event_ready.is_set():
        return Response(status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE)
    assert model is not None

    prompt = request_json.pop("prompt")

    responses = model.generate(prompt, **request_json)
    return JSONResponse(responses)


def load_model(model_name: str, model_revision: str) -> None:
    global model, event_error, event_ready, error_message
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        llm = transformers.AutoModelForCausalLM.from_pretrained(
            model_name,
            revision=model_revision,
            trust_remote_code=True,
        ).to(device)
        tokenizer = transformers.AutoTokenizer.from_pretrained(
            model_name,
            revision=model_revision,
            trust_remote_code=True,
        )
        model = CausalLanguageModel(device, tokenizer, llm)
        event_ready.set()
    except Exception:
        logging.exception("failed to create inference model")
        error_message = traceback.format_exc()
        event_error.set()


def main(_argv: list[str]) -> None:
    loader_thread = threading.Thread(
        target=load_model, args=(FLAGS.model_name, FLAGS.model_revision)
    )
    loader_thread.start()

    uvicorn.run(
        app,
        host=FLAGS.host,
        port=FLAGS.port,
        log_level="debug",
        timeout_keep_alive=TIMEOUT_KEEP_ALIVE,
    )


if __name__ == "__main__":
    absl.app.run(main)
