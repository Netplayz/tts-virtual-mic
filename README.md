# TTS Virtual Microphone

A desktop app that turns typed text into speech and pipes it through a virtual microphone, so it appears as audio input to apps like Discord, Zoom, or OBS.

Built with [Piper](https://github.com/rhasspy/piper) TTS, PyQt5, and PipeWire.

## Features

- Type text and hear it spoken through a virtual mic
- Adjustable speech speed (0.5x–2.0x)
- History of recent phrases (click to re-use)
- Runs as a standalone AppImage — no Python setup needed on target machines

## Requirements

- **Linux** with **PipeWire** (with PulseAudio compatibility — `pactl` and `pw-play`)
- A **Piper voice model** (`.onnx` + `.onnx.json`)

## Quick Start

```bash
# 1. Download a voice model
bash download-voice.sh

# 2. Run via venv
bash run.sh
```

Or build the AppImage:

```bash
bash build.sh
# Then run dist/TTS-Virtual-Mic
```

## Usage

1. Launch the app — status shows "Virtual Mic Active"
2. Select **Monitor of TTS-Virtual-Microphone** as your audio input in Discord/Zoom/etc.
3. Type text and click **Speak** (or Ctrl+Enter)
4. The audio plays through your speakers AND the virtual mic simultaneously

## Project Structure

```
main.py                  Entry point
core/
  tts_engine.py          Piper TTS wrapper
  virtual_mic.py         PipeWire null sink + loopback
  audio_player.py        WAV playback via pw-play
ui/
  main_window.py         PyQt5 GUI
resources/               Icons, stylesheet, desktop file
voices/                  Place voice models here
```

## License

MIT
