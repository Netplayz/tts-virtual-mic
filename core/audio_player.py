import subprocess
import logging

logger = logging.getLogger(__name__)


def _play(wav_path: str, target: str | None = None) -> subprocess.Popen:
    cmd = ["pw-play"]
    if target:
        cmd += ["--target", target]
    cmd.append(wav_path)
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


class AudioPlayer:
    def __init__(self):
        self._processes: list[subprocess.Popen] = []

    def play_wav_file(self, wav_path: str, target: str):
        self.stop()
        self._processes = [
            _play(wav_path),                 # speakers (default sink)
            _play(wav_path, target),          # virtual mic sink
        ]

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
