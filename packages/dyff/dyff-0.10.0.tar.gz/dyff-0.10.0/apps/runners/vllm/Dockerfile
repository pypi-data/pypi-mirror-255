# Can't find where the tags of GCR images are published; ignore warning
# hadolint ignore=DL3006
FROM gcr.io/deeplearning-platform-release/base-cu113.py310

# RUN apt-get update && apt-get install -y --no-install-recommends \
    # git \
    # kmod \
    # python3 \
    # python3-pip \
    # wget \
    # && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"

# hadolint ignore=DL3013
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# RUN git clone https://github.com/vllm-project/vllm.git \
#     && cd vllm \
#     && python3 -m pip install -e .

WORKDIR /dyff/app/

COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r ./requirements.txt

COPY __init__.py ./
COPY main.py ./

# RUN python3 -m pip install --no-cache-dir vllm

# Default server port
EXPOSE 8000

ENTRYPOINT [ "python3", "-m", "main", "--host", "0.0.0.0" ]
