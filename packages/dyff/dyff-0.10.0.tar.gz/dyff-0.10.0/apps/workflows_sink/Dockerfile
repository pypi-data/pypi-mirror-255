ARG CONTAINER_PROXY
FROM ${CONTAINER_PROXY}python:3.9-bullseye AS build

ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"

WORKDIR /build/

# hadolint ignore=DL3013
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

COPY apps/workflows_sink/requirements.txt ./

RUN python3 -m pip install --no-cache-dir -r requirements.txt

ARG CONTAINER_PROXY
FROM ${CONTAINER_PROXY}python:3.9-slim-bullseye

COPY --from=build /usr/local/ /usr/local/

ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"

WORKDIR /workflows-sink/

COPY apps/workflows_sink/workflows_sink/ ./workflows_sink/

COPY dyff/api/ ./dyff/api/
COPY dyff/core/ ./dyff/core/
COPY dyff/schema/ ./dyff/schema/

ENTRYPOINT ["python3", "-m", "workflows_sink"]
