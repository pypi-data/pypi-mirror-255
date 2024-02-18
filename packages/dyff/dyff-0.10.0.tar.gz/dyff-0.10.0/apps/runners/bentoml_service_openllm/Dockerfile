FROM python:3.9-bullseye

ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"

# hadolint ignore=DL3013
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

WORKDIR /dyff/app/

COPY requirements.txt ./

RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Block SETUP_BENTO_ENTRYPOINT
# Default port for BentoServer
EXPOSE 3000

# Expose Prometheus port
EXPOSE 3001

ENTRYPOINT [ "bentoml", "serve" ]
