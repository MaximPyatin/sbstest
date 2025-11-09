#!/usr/bin/env bash

set -euo pipefail

python /app/entrypoint.py

export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-sbs-api}"

exec opentelemetry-instrument uvicorn app.api.main:app --host 0.0.0.0 --port 8000

