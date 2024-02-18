# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import datetime
import time

from dyff.client import Client
from dyff.schema.requests import InferenceSessionCreateRequest

API_KEY: str = ...
ACCOUNT: str = ...

dyffapi = Client(api_key=API_KEY)

session_request = InferenceSessionCreateRequest(
    account=ACCOUNT,
    # databricks/dolly-v2-3b
    inferenceService="ba4ba5c26c9246ee88e127d37cdf548d",
    expires=datetime.datetime.utcnow() + datetime.timedelta(days=1),
    replicas=1,
    useSpotPods=True,
)

session_and_token = dyffapi.inferencesessions.create(session_request)
session = session_and_token.inferencesession
session_id = session.id
session_token = session_and_token.token
print(f"created session:\n{session_and_token.inferencesession}")

# Starting the session can take some time, especially if you requested a GPU
# You can poll the inferencesessions.ready() endpoint to find out if the
# session is ready to accept requests. It will return status 200 if the
# session is ready, and will raise an HttpResponseError with status 503
# (ServiceUnavailable) if the session is not ready. (It may also return 404
# if the session was created recently.)
while not dyffapi.inferencesessions.ready(session_id):
    print(f"[{datetime.datetime.utcnow()}]: not ready")
    # Always use a short sleep when polling in a loop. ready() will usually
    # block for some time as well, but it depends on the runner implementation
    time.sleep(1)
print("Ready")

# If you already have a running session:
# session = dyffapi.inferencesessions.get(session_id)

# Create an inference client using the default interface specified for the
# InferenceService that's being run in the session
interface = session.inferenceService.interface
inference_client = dyffapi.inferencesessions.client(
    session_id,
    session_token,
    # If you don't specify 'interface', the client will use the native JSON
    # interface of the model.
    interface=interface,
    # You can also set any of these separately; they will override the
    # corresponding setting in 'interface' if you specify both.
    # endpoint=interface.endpoint,
    # input_adapter=create_pipeline(interface.inputPipeline),
    # output_adapter=create_pipeline(interface.outputPipeline),
)

# The input is {"text": ...} because the default interface for the dolly-v2-3b
# service maps {"text": ...} -> {"prompt": ...}
y = inference_client.infer({"text": "Open the pod bay doors, Hal!"})
print(y)
