#!/bin/bash
set -e

MODEL_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high"
VOICE_DIR="voices/en_US-lessac-high"

mkdir -p "$VOICE_DIR"

echo "Downloading voice model..."
wget -q --show-progress "$MODEL_URL/en_US-lessac-high.onnx" -P "$VOICE_DIR"
wget -q --show-progress "$MODEL_URL/en_US-lessac-high.onnx.json" -P "$VOICE_DIR"

echo "Done. Model saved to $VOICE_DIR"
