# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# This code is based on code from the vLLM library,
#   https://github.com/vllm-project/vllm
# available under the following license (Note: there is no copyright date or
# copyright holder specified on the project website as of 2023/11/11):
#
# Copyright [yyyy] [name of copyright owner]
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import argparse
import json
import threading
from typing import AsyncGenerator

import fastapi
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.logger import init_logger
from vllm.sampling_params import SamplingParams
from vllm.utils import random_uuid

TIMEOUT_KEEP_ALIVE = 5  # seconds.
TIMEOUT_TO_PREVENT_DEADLOCK = 1  # seconds.
app = FastAPI()
_engine_ready = threading.Event()
engine = None
logger = init_logger(__name__)


@app.get("/health")
async def health() -> Response:
    """Health check."""
    return Response(status_code=fastapi.status.HTTP_200_OK)


@app.get("/ready")
async def ready() -> Response:
    if _engine_ready.is_set():
        return Response(status_code=fastapi.status.HTTP_200_OK)
    else:
        return Response(status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE)


@app.post("/generate")
async def generate(request: Request) -> Response:
    """Generate completion for the request.

    The request should be a JSON object with the following fields:
    - prompt: the prompt to use for the generation.
    - stream: whether to stream the results or not.
    - other fields: the sampling parameters (See `SamplingParams` for details).
    """
    if not _engine_ready.is_set():
        return Response(status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE)
    assert engine is not None

    request_dict = await request.json()
    prompt = request_dict.pop("prompt")
    stream = request_dict.pop("stream", False)
    sampling_params = SamplingParams(**request_dict)
    request_id = random_uuid()

    results_generator = engine.generate(prompt, sampling_params, request_id)

    # Streaming case
    async def stream_results() -> AsyncGenerator[bytes, None]:
        async for request_output in results_generator:
            prompt = request_output.prompt
            text_outputs = [prompt + output.text for output in request_output.outputs]
            ret = {"text": text_outputs}
            yield (json.dumps(ret) + "\0").encode("utf-8")

    if stream:
        return StreamingResponse(stream_results())

    # Non-streaming case
    final_output = None
    async for request_output in results_generator:
        if await request.is_disconnected():
            # Abort the request if the client disconnects.
            await engine.abort(request_id)
            return Response(status_code=499)
        final_output = request_output

    assert final_output is not None
    prompt = final_output.prompt
    text_outputs = [prompt + output.text for output in final_output.outputs]
    ret = {"text": text_outputs}
    return JSONResponse(ret)


def _load_engine(engine_args: AsyncEngineArgs):
    global engine, _engine_ready
    try:
        engine = AsyncLLMEngine.from_engine_args(engine_args)
        _engine_ready.set()
    except Exception:
        logger.exception("failed to create LLMEngine")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default=None)
    parser.add_argument("--port", type=int, default=8000)
    parser = AsyncEngineArgs.add_cli_args(parser)
    args = parser.parse_args()

    engine_args = AsyncEngineArgs.from_cli_args(args)
    loader_thread = threading.Thread(target=_load_engine, args=(engine_args,))
    loader_thread.start()

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="debug",
        timeout_keep_alive=TIMEOUT_KEEP_ALIVE,
    )


if __name__ == "__main__":
    main()
