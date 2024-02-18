FROM python:3.9-bullseye

ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"

# hadolint ignore=DL3013
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

WORKDIR /dyff/app/

COPY requirements.txt ./

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . ./

EXPOSE 8000

CMD ["uvicorn", "server:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
