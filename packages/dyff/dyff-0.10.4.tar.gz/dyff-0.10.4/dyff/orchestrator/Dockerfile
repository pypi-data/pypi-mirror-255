ARG CONTAINER_PROXY
FROM ${CONTAINER_PROXY}python:3.9-bullseye AS build

ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"

WORKDIR /build/

# hadolint ignore=DL3013
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements-orchestrator.txt ./

RUN python3 -m pip install --no-cache-dir -r requirements-orchestrator.txt

ARG CONTAINER_PROXY
FROM ${CONTAINER_PROXY}python:3.9-slim-bullseye

COPY --from=build /usr/local/ /usr/local/

ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"

WORKDIR /dyff-orchestrator/

COPY dyff/api/ ./dyff/api/
COPY dyff/core/ ./dyff/core/
COPY dyff/orchestrator/ ./dyff/orchestrator/
COPY dyff/schema/ ./dyff/schema/

ENTRYPOINT ["python3", "-m", "dyff.orchestrator"]
