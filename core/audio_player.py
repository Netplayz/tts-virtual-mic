import subprocess
import logging

logger = logging.getLogger(__name__)


class AudioPlayer:
    def __init__(self):
        self._process: subprocess.Popen | None = None

    def play_wav_file(self, wav_path: str, target: str):
        self.stop()
        self._process = subprocess.Popen(
            ["pw-play", "--target", target, wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

    def stop(self):
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    def is_playing(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def wait(self):
        if self._process:
            try:
                self._process.wait()
                if self._process.returncode != 0:
                    err = self._process.stderr.read() if self._process.stderr else b""
                    logger.warning("pw-play failed (exit %d): %s", self._process.returncode, err.decode(errors="replace"))
            except Exception:
                pass
            self._process = None
