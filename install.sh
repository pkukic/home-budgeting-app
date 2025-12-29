#!/bin/bash
set -e

echo "=== Home Budget Setup ==="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv first."
    exit 1
fi

uv sync

echo
echo "Setup complete! Run with: export JWT_SECRET_KEY='your_key' && uv run python main.py"
