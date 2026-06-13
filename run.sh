#!/bin/bash
# Launcher for TTS-Virtual-Mic AppImage (works without FUSE)
DIR="$(cd "$(dirname "$0")" && pwd)"
APPIMAGE="$DIR/TTS-Virtual-Mic-x86_64.AppImage"

if [ ! -f "$APPIMAGE" ]; then
    echo "Error: $APPIMAGE not found"
    exit 1
fi

# Extract and run if FUSE is unavailable
if ! command -v fusermount &>/dev/null && ! command -v fusermount3 &>/dev/null; then
    "$APPIMAGE" --appimage-extract-and-run "$@"
else
    "$APPIMAGE" "$@"
fi
