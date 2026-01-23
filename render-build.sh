#!/usr/bin/env bash
set -euo pipefail

# System dependencies for OCR and PDF utilities
apt-get update
apt-get install -y --no-install-recommends \
  tesseract-ocr \
  libtesseract-dev \
  poppler-utils
apt-get clean
rm -rf /var/lib/apt/lists/*

# Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
