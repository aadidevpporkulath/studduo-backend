#!/usr/bin/env bash
set -euo pipefail

# Defaults for Render runtime
export TESSERACT_CMD="${TESSERACT_CMD:-/usr/bin/tesseract}"
export CHROMA_PERSIST_DIR="${CHROMA_PERSIST_DIR:-./chroma_db}"
export KNOWLEDGE_DIR="${KNOWLEDGE_DIR:-./knowledge}"

uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
