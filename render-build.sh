#!/usr/bin/env bash
set -euo pipefail

# Optimize pip for memory efficiency
export PIP_NO_CACHE_DIR=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

# Build dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel

# Install requirements with no cache to save space
pip install --no-cache-dir -r requirements.txt

echo "Build complete - dependencies installed successfully"
