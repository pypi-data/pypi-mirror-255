# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime, timedelta

from dyff.client import Client
from dyff.schema.requests import (
    EvaluationCreateRequest,
    EvaluationInferenceSessionRequest,
)

API_KEY: str = ...
ACCOUNT: str = ...

dyffapi = Client(api_key=API_KEY)

# databricks/dolly-v2-3b
service_id = "de449a3995b54f13be8c64f876131032"
# linux-fortune
dataset_id = "0e702977e2864cbd8d99654c7a0d80a5"

evaluation_request = EvaluationCreateRequest(
    account=ACCOUNT,
    dataset=dataset_id,
    inferenceSession=EvaluationInferenceSessionRequest(
        inferenceService=service_id,
        expires=datetime.utcnow() + timedelta(days=1),
        replicas=1,
        useSpotPods=True,
    ),
    # There is a pool of replicas*workersPerReplia client connections that
    # send requests to the inference session. vLLM collects individual requests
    # into adaptively-sized batches. Generally, you would want to choose this
    # value by increasing it until you stop getting higher throughput.
    workersPerReplica=32,
)

evaluation = dyffapi.evaluations.create(evaluation_request)
print(evaluation)
