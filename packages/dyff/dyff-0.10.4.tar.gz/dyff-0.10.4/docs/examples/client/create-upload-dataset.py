# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from dyff.client import Client

API_KEY: str = ...
ACCOUNT: str = ...
ARROW_DATASET_ROOT_DIRECTORY: str = ...
DATASET_NAME: str = ...

dyffapi = Client(api_key=API_KEY)

dataset = dyffapi.datasets.create_arrow_dataset(
    ARROW_DATASET_ROOT_DIRECTORY, account=ACCOUNT, name=DATASET_NAME
)
print(f"created dataset:\n{dataset}")

# If you created the dataset but couldn't complete the upload, you can
# fetch the dataset record and re-try the upload:
# dataset = dyffapi.datasets.get(<dataset.id>)

dyffapi.datasets.upload_arrow_dataset(dataset, ARROW_DATASET_ROOT_DIRECTORY)
