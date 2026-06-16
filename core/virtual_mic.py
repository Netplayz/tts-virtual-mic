import subprocess
import time
import logging

logger = logging.getLogger(__name__)

SINK_NAME = "tts_virtual"
SINK_DESCRIPTION = "TTS Virtual Sink"
SOURCE_NAME = "tts_mic"
SOURCE_DESCRIPTION = "TTS Virtual Microphone"


class VirtualMic:
    def __init__(self):
        self._sink_module_id: str | None = None
        self._source_module_id: str | None = None

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
                logger.error("null-sink creation failed: %s", result.stderr.strip())
                return False
            self._sink_module_id = result.stdout.strip()
            time.sleep(0.3)

            result = subprocess.run(
                [
                    "pactl", "load-module", "module-remap-source",
                    f"master={SINK_NAME}.monitor",
                    f"source_name={SOURCE_NAME}",
                    f'source_properties=device.description={SOURCE_DESCRIPTION}',
                ],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                logger.error("remap-source creation failed: %s", result.stderr.strip())
                return False
            self._source_module_id = result.stdout.strip()
            time.sleep(0.3)

            return self.is_active()
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error("virtual mic start failed: %s", e)
            return False

    def stop(self):
        if self._source_module_id:
            subprocess.run(
                ["pactl", "unload-module", self._source_module_id],
                capture_output=True, timeout=5
            )
            self._source_module_id = None
        if self._sink_module_id:
            subprocess.run(
                ["pactl", "unload-module", self._sink_module_id],
                capture_output=True, timeout=5
            )
            self._sink_module_id = None
        time.sleep(0.3)

    def is_active(self) -> bool:
        result = subprocess.run(
            ["pactl", "list", "sources", "short"],
            capture_output=True, text=True, timeout=5
        )
        return SOURCE_NAME in result.stdout

    def get_sink_name(self) -> str:
        return SINK_NAME

    def get_source_name(self) -> str:
        return SOURCE_NAME
