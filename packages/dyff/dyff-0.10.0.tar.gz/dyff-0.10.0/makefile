VENV ?= venv
PYTHON ?= $(VENV)/bin/python3
UVICORN ?= $(VENV)/bin/uvicorn
DOCKER ?= docker
PIP ?= $(PYTHON) -m pip
PIP_COMPILE ?= $(VENV)/bin/pip-compile
IMAGE ?= dyff

BASE_DIR = $(shell pwd)
PYTHONPATH = $(BASE_DIR)
OPENAPI_DIR = $(BASE_DIR)/openapi
OPENAPI_JSON = $(OPENAPI_DIR)/dyff.json
OPENAPI_CLIENT_DIR = $(BASE_DIR)/dyff/client
OPENAPI_NAMESPACE = _generated
OPENAPI_GENERATED_DIR = $(OPENAPI_CLIENT_DIR)/$(OPENAPI_NAMESPACE)

.PHONY: all
all: serve

.PHONY: setup
setup: $(VENV)/requirements.txt

requirements.txt: requirements.in | $(VENV)
	$(PIP_COMPILE) --no-emit-index-url --upgrade

$(VENV)/requirements.txt: requirements.txt | $(VENV)
	$(PYTHON) -m pip install -r requirements.txt
	cp -f requirements.txt $(VENV)/requirements.txt

$(VENV):
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip setuptools wheel pip-tools

.PHONY: openapi
openapi: $(OPENAPI_GENERATED_DIR)

$(OPENAPI_DIR):
	mkdir -p $(OPENAPI_DIR)

$(OPENAPI_JSON): | $(OPENAPI_DIR)
	PYTHONPATH=$(shell pwd) $(PYTHON) ./scripts/generate-openapi-definitions.py $(OPENAPI_JSON)
	$(PYTHON) ./scripts/fix-openapi.py $(OPENAPI_JSON)

$(OPENAPI_GENERATED_DIR): $(OPENAPI_JSON)
	npx autorest --v3 --input-file=$(OPENAPI_JSON) --python --python3-only --output-folder=$(OPENAPI_CLIENT_DIR) --namespace=$(OPENAPI_NAMESPACE)
	isort $(OPENAPI_GENERATED_DIR)
	black $(OPENAPI_GENERATED_DIR)

.PHONY: clean
clean:
	rm -f $(OPENAPI_JSON)
	rm -rf $(OPENAPI_DIR)

.PHONY: distclean
distclean:
	rm -rf node_modules/ $(VENV)
	find -name __pycache__ -type d -exec rm -rf '{}' \;
	find -name \*.pyc -type f -exec rm -f '{}' \;

.PHONY: serve
serve:
	$(UVICORN) dyff.api.server:app

.PHONY: docs
docs:
	$(MAKE) -C docs dirhtml

.PHONY: docs-production
docs-production:
	SPHINXOPTS=-W $(MAKE) -C docs dirhtml

.PHONY: docs-clean
docs-clean:
	rm -rf docs/_build

.PHONY: docs-serve
docs-serve:
	$(PYTHON) -m http.server --directory docs/_build/dirhtml

.PHONY: docs-autobuild
docs-autobuild:
	sphinx-autobuild -j auto -b dirhtml docs docs/_build/dirhtml

.PHONY: docker-build
docker-build:
	$(DOCKER) build -t $(IMAGE) .

.PHONY: docker-run
docker-run:
	$(DOCKER) run --rm -it $(IMAGE)

.PHONY: docker-run-bash
docker-run-bash:
	$(DOCKER) run --rm -it $(IMAGE) bash

ORCHESTRATOR_IMAGE = dyff-orchestrator

.PHONY: orchestrator-dev
orchestrator-dev: orchestrator-build orchestrator-run

.PHONY: orchestrator-build
orchestrator-build:
	$(DOCKER) build -f dyff/orchestrator/Dockerfile -t $(ORCHESTRATOR_IMAGE) .

.PHONY: orchestrator-run
orchestrator-run:
	$(DOCKER) run --rm -it -t $(ORCHESTRATOR_IMAGE) .

.PHONY: config-listing
config-listing:
	PYTHONPATH=$(shell pwd) $(PYTHON) ./scripts/generate-config-listing.py > docs/deployment/configuration.rst

.PHONY: local-server-insecure-build
local-server-insecure-build:
	$(DOCKER) build -f Dockerfile-api-server-insecure -t dyff/api-server-insecure:local .

.PHONY: local-server-insecure-run
local-server-insecure-run:
	$(DOCKER) run -p 8000:8000 -e DYFF_API_KEY dyff/api-server-insecure:local
