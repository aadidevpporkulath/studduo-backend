#!/usr/bin/env bash
set -euo pipefail

# Environment defaults for Render runtime
export TESSERACT_CMD="${TESSERACT_CMD:-/usr/bin/tesseract}"
export CHROMA_PERSIST_DIR="${CHROMA_PERSIST_DIR:-./chroma_db}"
export KNOWLEDGE_DIR="${KNOWLEDGE_DIR:-./knowledge}"
export PORT="${PORT:-8000}"

# Memory optimization for Render's 512MB limit
export PYTHONUNBUFFERED=1
export PYTHONOPTIMIZE=2  # Enable Python bytecode optimizations
export OMP_NUM_THREADS=1  # Limit OpenMP threads (numpy, scipy)
export MALLOC_TRIM_THRESHOLD_=256000  # Aggressive memory trimming

echo "=== StudduoAI API Startup ==="
echo "Port: $PORT"
echo "Vector DB: $CHROMA_PERSIST_DIR"
echo "Knowledge: $KNOWLEDGE_DIR"
echo "============================"
echo ""

# Run document ingestion
echo "Running document ingestion..."
python ingest_documents.py
echo "Document ingestion complete"
echo ""

# Start API server with memory-efficient configuration
# Using uvloop + httptools for ~15% faster event loop
echo "Starting API server..."
uvicorn main:app \
  --host 0.0.0.0 \
  --port "$PORT" \
  --workers 1 \
  --loop uvloop \
  --http httptools \
  --log-level info
