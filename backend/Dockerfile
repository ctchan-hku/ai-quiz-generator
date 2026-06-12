FROM python:3.13-slim-bookworm AS builder

WORKDIR /build
RUN pip install --no-cache-dir --upgrade pip
COPY pyproject.toml requirements.txt ./
COPY app ./app
RUN pip install --no-cache-dir .

FROM python:3.13-slim-bookworm

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app ./app
COPY data/static ./data/static
COPY uvicorn_log_config.json ./uvicorn_log_config.json
COPY scripts/docker-entrypoint.sh ./scripts/docker-entrypoint.sh

RUN chmod +x ./scripts/docker-entrypoint.sh

ENV APP_ENV=prod \
    PORT=8080 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/app/data/runtime \
    STATIC_DATA_DIR=/app/data/static

EXPOSE 8080

ENTRYPOINT ["./scripts/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--log-config", "uvicorn_log_config.json"]
