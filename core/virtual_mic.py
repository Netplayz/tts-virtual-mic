import subprocess
import time


SINK_NAME = "tts_virtual"
SINK_DESCRIPTION = "TTS-Virtual-Microphone"


class VirtualMic:
    def __init__(self):
        self._module_id: str | None = None

    def start(self) -> bool:
        self.stop()
        try:
            result = subprocess.run(
                [
                    "pactl", "load-module", "module-null-sink",
                    f"sink_name={SINK_NAME}",
                    f'sink_properties=device.description={SINK_DESCRIPTION}',
                ],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return False
            self._module_id = result.stdout.strip()
            time.sleep(0.3)
            return self.is_active()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def stop(self):
        if self._module_id:
            subprocess.run(
                ["pactl", "unload-module", self._module_id],
                capture_output=True, timeout=5
            )
            self._module_id = None
            time.sleep(0.3)

    def is_active(self) -> bool:
        result = subprocess.run(
            ["pactl", "list", "sinks", "short"],
            capture_output=True, text=True, timeout=5
        )
        return SINK_NAME in result.stdout

    def get_sink_name(self) -> str:
        return SINK_NAME
