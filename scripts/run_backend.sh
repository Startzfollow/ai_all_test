#!/usr/bin/env bash
set -e
export CONFIG_PATH=${CONFIG_PATH:-configs/default.yaml}
export APP_HOST=${APP_HOST:-0.0.0.0}
export APP_PORT=${APP_PORT:-8000}
uvicorn backend.app.main:app --host "$APP_HOST" --port "$APP_PORT" --reload
