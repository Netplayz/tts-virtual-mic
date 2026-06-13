import subprocess
import time
import logging

logger = logging.getLogger(__name__)


class AudioPlayer:
    def __init__(self):
        self._processes: list[subprocess.Popen] = []

    def play_wav_file(self, wav_path: str, target: str):
        self.stop()
        p1 = subprocess.Popen(
            ["pw-play", "--target", target, wav_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        self._processes = [p1]
        time.sleep(0.15)
        p2 = subprocess.Popen(
            ["pw-play", wav_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        self._processes.append(p2)

    def stop(self):
        for p in self._processes:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    p.kill()
        self._processes = []

    def is_playing(self) -> bool:
        return any(p.poll() is None for p in self._processes)

    def wait(self):
        for p in self._processes:
            try:
                p.wait()
                if p.returncode != 0:
                    err = p.stderr.read() if p.stderr else b""
                    logger.warning("pw-play failed (exit %d): %s", p.returncode, err.decode(errors="replace"))
            except Exception:
                pass
        self._processes = []
