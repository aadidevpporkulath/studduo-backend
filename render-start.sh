#!/usr/bin/env bash

# Defaults for Render runtime
export TESSERACT_CMD="${TESSERACT_CMD:-/usr/bin/tesseract}"
export CHROMA_PERSIST_DIR="${CHROMA_PERSIST_DIR:-./chroma_db}"
export KNOWLEDGE_DIR="${KNOWLEDGE_DIR:-./knowledge}"
export PORT="${PORT:-8000}"

echo "Starting StudduoAI API on port $PORT..."
echo "TESSERACT_CMD: $TESSERACT_CMD"
echo "CHROMA_PERSIST_DIR: $CHROMA_PERSIST_DIR"
echo "KNOWLEDGE_DIR: $KNOWLEDGE_DIR"

uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers 1
