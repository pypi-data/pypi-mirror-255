# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import random

import fastapi

app = fastapi.FastAPI(title="InferenceService Mock")


@app.get(f"/health")
async def health() -> int:
    return fastapi.status.HTTP_200_OK


@app.get(f"/ready")
async def ready() -> int:
    return fastapi.status.HTTP_200_OK


@app.post(
    f"/v1/generate",
    tags=["openllm"],
    summary="[BentoML/OpenLLM] Generate text in response to a prompt",
    response_description="The generated text",
)
async def openllm_v1_generate(request: fastapi.Request):
    body = await request.json()
    print(body)
    try:
        body["prompt"]
        return fastapi.responses.JSONResponse(
            content={
                "responses": [
                    "/v1/generate: All work and no play makes Jack a dull boy"
                ]
            }
        )
    except:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_400_BAD_REQUEST,
            detail="expected body like '{\"prompt\": <text>}'",
        )


@app.post(
    f"/generate",
    tags=["vllm"],
    summary="[VLLM] Generate text in response to a prompt",
    response_description="The generated text",
)
async def vllm_generate(request: fastapi.Request):
    body = await request.json()
    print(body)
    responses = [
        "/generate: it was the worst of times.",
        "/generate: it was the blurst of times.",
        "/generate: it was pretty OK, I guess.",
    ]
    try:
        body["prompt"]
        random.shuffle(responses)
        return fastapi.responses.JSONResponse(content={"text": list(responses[:2])})
    except:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_400_BAD_REQUEST,
            detail="expected body like '{\"prompt\": <text>}'",
        )
