# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from dyff.client import Client
from dyff.schema.platform import (
    Accelerator,
    AcceleratorGPU,
    DataSchema,
    DyffDataSchema,
    InferenceInterface,
    InferenceServiceRunner,
    InferenceServiceRunnerKind,
    ModelResources,
    SchemaAdapter,
)
from dyff.schema.requests import InferenceServiceCreateRequest

API_KEY: str = ...
ACCOUNT: str = ...

dyffapi = Client(api_key=API_KEY)

service_request = InferenceServiceCreateRequest(
    account=ACCOUNT,
    # ID of the databricks/dolly-v2-3b Model
    model="3be8292c1296402bae1981499f31c635",
    name="databricks/dolly-v2-3b",
    runner=InferenceServiceRunner(
        kind=InferenceServiceRunnerKind.VLLM,
        # T4 GPUs don't support bfloat format, so force standard float format
        args=["--dtype", "float16"],
        accelerator=Accelerator(
            kind="GPU",
            gpu=AcceleratorGPU(
                hardwareTypes=["nvidia.com/gpu-t4"],
                memory="10Gi",
            ),
        ),
        resources=ModelResources(
            storage="10Gi",
            memory="16Gi",
        ),
    ),
    interface=InferenceInterface(
        # This is the inference endpoint for the vLLM runner
        endpoint="generate",
        # The output records should look like: {"text": "To be, or not to be"}
        outputSchema=DataSchema.make_output_schema(
            DyffDataSchema(components=["text.Text"]),
        ),
        # How to convert the input dataset into the format the runner expects
        inputPipeline=[
            # {"text": "The question"} -> {"prompt": "The question"}
            SchemaAdapter(
                kind="TransformJSON",
                configuration={
                    # Map 'text' in the input data to 'prompt' in the request
                    # sent to the model
                    "prompt": "$.text",
                    # Use the constant '100' for 'max_tokens' in the request
                    "max_tokens": 100,
                },
            ),
        ],
        # How to convert the runner output to match outputSchema
        outputPipeline=[
            # {"text": ["The answer"]} -> {"text": "The answer"}
            SchemaAdapter(
                kind="ExplodeCollections",
                configuration={"collections": ["text"]},
            ),
        ],
    ),
)

service = dyffapi.inferenceservices.create(service_request)
print(f"created inferenceservice:\n{service}")
