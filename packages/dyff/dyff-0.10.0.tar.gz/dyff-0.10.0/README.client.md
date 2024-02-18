# Dyff client

[![pipeline status](https://gitlab.com/dyff/dyff/badges/main/pipeline.svg)](https://gitlab.com/dyff/dyff/-/commits/main)
[![coverage report](https://gitlab.com/dyff/dyff/badges/main/coverage.svg)](https://gitlab.com/dyff/dyff/-/commits/main)
[![Latest Release](https://gitlab.com/dyff/dyff/-/badges/release.svg)](https://gitlab.com/dyff/dyff/-/releases)

Python client for the Dyff AI auditing platform.

## Getting started

### Installation

The Dyff client requires Python 3.8+ and can be installed using pip:

```bash
python3 -m pip install dyff
```

### Setup

```python
from dyff.client import Client

client = Client(api_key="XXXXXX")
```

The API key must be provisioned by a Dyff administrator.

### Usage

```python
dataset = client.datasets.create_arrow_dataset(
    "/my/data", account="XXX", name="mydata"
)
```

For more examples, see the [client
examples](https://docs.dyff.io/examples/client/).

For the full API, see the [client API
reference](https://docs.dyff.io/api-reference/client/).
