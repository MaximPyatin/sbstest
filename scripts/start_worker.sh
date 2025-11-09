#!/usr/bin/env bash

set -euo pipefail

python /app/entrypoint.py

exec python /app/run_worker.py

