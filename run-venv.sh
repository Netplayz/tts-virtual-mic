#!/bin/bash
# Run TTS Virtual Mic directly from the Python venv (no AppImage needed)
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
exec "$DIR/venv/bin/python" "$DIR/main.py" "$@"
