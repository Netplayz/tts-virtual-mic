import wave
import tempfile
import os
import logging
from pathlib import Path
from typing import Optional

import piper
from piper import PiperVoice, SynthesisConfig

logger = logging.getLogger(__name__)


class TTSEngine:
    def __init__(self, model_path: str):
        self._model_path = Path(model_path)
        self._voice: Optional[PiperVoice] = None
        self._stop_requested = False
        self._load_voice()

    def _load_voice(self):
        logger.info("Loading voice model: %s", self._model_path)
        self._voice = PiperVoice.load(self._model_path)
        logger.info("Voice loaded (sample rate: %d)", self._voice.config.sample_rate)

    @property
    def sample_rate(self) -> int:
        if self._voice:
            return self._voice.config.sample_rate
        return 22050

    def synthesize(self, text: str, speed: float = 1.0) -> bytes:
        if not self._voice:
            raise RuntimeError("Voice not loaded")

        self._stop_requested = False
        syn_config = SynthesisConfig(
            length_scale=1.0 / speed if speed > 0 else 1.0,
            noise_scale=0.667,
            noise_w_scale=0.8,
        )

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        try:
            with wave.open(tmp.name, "wb") as wf:
                self._voice.synthesize_wav(text, wf, syn_config)
            tmp.close()
            with open(tmp.name, "rb") as f:
                wav_data = f.read()
            return wav_data
        finally:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass

    def synthesize_to_wav(self, text: str, output_path: str, speed: float = 1.0):
        if not self._voice:
            raise RuntimeError("Voice not loaded")

        syn_config = SynthesisConfig(
            length_scale=1.0 / speed if speed > 0 else 1.0,
            noise_scale=0.667,
            noise_w_scale=0.8,
        )

        with wave.open(output_path, "wb") as wf:
            self._voice.synthesize_wav(text, wf, syn_config)

    def stop(self):
        self._stop_requested = True

    @property
    def voice(self) -> Optional[PiperVoice]:
        return self._voice
