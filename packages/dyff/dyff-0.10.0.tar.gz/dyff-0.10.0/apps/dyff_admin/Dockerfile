FROM google/cloud-sdk:456.0.0

ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"

# hadolint ignore=DL3013
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
  vim \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /dyff/app/

COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r ./requirements.txt

COPY dyff/ ./dyff/
COPY scripts/ ./
# COPY accounts/ ./accounts/
