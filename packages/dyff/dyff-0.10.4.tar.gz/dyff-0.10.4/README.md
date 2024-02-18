# Dyff

[![pipeline status](https://gitlab.com/ul-dsri/dyff/dyff/badges/main/pipeline.svg)](https://gitlab.com/ul-dsri/dyff/dyff/-/commits/main)
[![coverage report](https://gitlab.com/ul-dsri/dyff/dyff/badges/main/coverage.svg)](https://gitlab.com/ul-dsri/dyff/dyff/-/commits/main)
[![Latest Release](https://gitlab.com/ul-dsri/dyff/dyff/-/badges/release.svg)](https://gitlab.com/ul-dsri/dyff/dyff/-/releases)

## About

The dyff application has multiple moving parts:

- An API server (`dyff.api`).

- A job orchestrator (`dyff.orchestrator`).

- A Kubernetes operator ([dyff-operator](https://gitlab.com/ul-dsri/dyff/dyff-operator)).

- A number of jobs that implement the core dyff functionality.

- A Python client library for interacting with the dyff API.

## Installation

Note: If grpcio build fails on Mac M1, use this:

```bash
GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1 GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1 python -m pip install grpcio
```

Set up the virtual environment:

```bash
make setup
```

Start the application:

```bash
make serve
```

```console
$ make serve
venv/bin/uvicorn dyff.api.server:app
INFO:     Started server process [189616]
INFO:     Waiting for application startup.
Starting API server with configuration:
{
  "command_backend": "dyff.api.backend.kafka.KafkaCommandBackend",
  "query_backend": "dyff.api.backend.mongodb.MongoDBQueryBackend",
  "api_client": null,
  "auth": null,
  "kafka": null,
  "kafka_topics": null,
  "mongodb": null,
  "gitlab": null,
  "storage": null,
  "kubernetes": null
}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Documentation

Hosted API documentation is available at
<https://ul-dsri.gitlab.io/dyff/dyff/>.

To build the docs locally, first install the dependencies:

```bash
python3 -m pip install -r docs/requirements.txt
```

Build the docs:

```bash
make docs
```

A web server can be started:

```bash
make docs-serve
```

The docs can then be viewed locally at <http://localhost:8000>.

A live-reloading version of the docs is also available:

```bash
make docs-autobuild
```

## OpenAPI Spec

[`autorest`](https://github.com/Azure/autorest) is required to generate the
OpenAPI spec, and is installable with `npm`:

```bash
npm install
```

The following dependencies should be installed to style the output:

```bash
pip install black isort
```

`autorest` has its own virtualenv that was observed to be missing some
dependencies on a default install. Add them by changing to the parent directory
of the virtualenv and installing with pip:

```bash
cd ~/.autorest/@autorest_python@6.7.5/node_modules/@autorest/python/
venv/bin/python3 -m pip install pyyaml json-rpc m2r2 jinja2
```

Finally, update the OpenAPI spec:

```bash
make openapi
```

Only OpenAPI schema versions matchi `3.0.x` are supported.

## Troubleshooting

This error occurs when attempting to connect to a GCS bucket with invalid credentials:

```
google.auth.exceptions.DefaultCredentialsError: Your default credentials were not found. To set up Application Default Credentials, see https://cloud.google.com/docs/authentication/external/set-up-adc for more information.
```
