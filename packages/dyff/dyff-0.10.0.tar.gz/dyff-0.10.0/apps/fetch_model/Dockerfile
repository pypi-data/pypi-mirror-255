ARG CONTAINER_PROXY
FROM ${CONTAINER_PROXY}python:3.9-bullseye AS build

ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"

WORKDIR /build/

# hadolint ignore=DL3013
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

COPY apps/fetch_model/requirements.txt ./

RUN python3 -m pip install --no-cache-dir -r requirements.txt

ARG CONTAINER_PROXY
FROM ${CONTAINER_PROXY}python:3.9-slim-bullseye

COPY --from=build /usr/local/ /usr/local/

ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
  git \
  git-lfs \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /fetch-model/

COPY apps/fetch_model/ ./
COPY dyff/ ./dyff/

ENTRYPOINT [ "python3", "-m", "fetch_model" ]
