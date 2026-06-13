import os
import json
import threading
import tempfile
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QPushButton, QComboBox, QSlider,
    QLabel, QListWidget, QMessageBox,
    QFrame, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont

from core.tts_engine import TTSEngine
from core.virtual_mic import VirtualMic
from core.audio_player import AudioPlayer

HISTORY_FILE = os.path.join(
    os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")),
    "tts-virtual-mic", "history.json"
)


class Signals(QObject):
    speak_done = pyqtSignal()
    speak_error = pyqtSignal(str)
    status_update = pyqtSignal(str, bool)


class MainWindow(QMainWindow):
    def __init__(self, model_path: str):
        super().__init__()
        self._model_path = model_path
        self._engine: Optional[TTSEngine] = None
        self._mic = VirtualMic()
        self._player = AudioPlayer()
        self._signals = Signals()
        self._history: list[str] = []
        self._speaking = False

        self._init_ui()
        self._connect_signals()
        self._init_history()
        QTimer.singleShot(100, self._init_voice)
        QTimer.singleShot(200, self._init_mic)

    def _init_ui(self):
        self.setWindowTitle("TTS Virtual Microphone")
        self.setMinimumSize(520, 620)
        self.setMaximumWidth(700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("TTS Virtual Microphone")
        title.setObjectName("headerTitle")
        self._status_label = QLabel("Initializing...")
        self._status_label.setObjectName("statusLabel")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self._status_label)
        layout.addLayout(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separator")
        layout.addWidget(sep)

        self._text_input = QPlainTextEdit()
        self._text_input.setPlaceholderText(
            "Type text here and press Ctrl+Enter or click Speak..."
        )
        self._text_input.setMinimumHeight(140)
        self._text_input.setMaximumHeight(200)
        self._text_input.setFont(QFont("Sans Serif", 12))
        layout.addWidget(self._text_input)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        self._voice_combo = QComboBox()
        self._voice_combo.setMinimumWidth(180)
        controls.addWidget(self._voice_combo)
        controls.addWidget(QLabel("Speed:"))
        self._speed_slider = QSlider(Qt.Horizontal)
        self._speed_slider.setRange(50, 200)
        self._speed_slider.setValue(100)
        self._speed_slider.setFixedWidth(100)
        self._speed_label = QLabel("1.0x")
        self._speed_label.setFixedWidth(35)
        controls.addWidget(self._speed_slider)
        controls.addWidget(self._speed_label)
        controls.addStretch()
        layout.addLayout(controls)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self._speak_btn = QPushButton("Speak")
        self._speak_btn.setObjectName("speakBtn")
        self._speak_btn.setMinimumHeight(38)
        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setObjectName("stopBtn")
        self._stop_btn.setMinimumHeight(38)
        self._stop_btn.setEnabled(False)
        btn_layout.addStretch()
        btn_layout.addWidget(self._speak_btn)
        btn_layout.addWidget(self._stop_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setObjectName("separator")
        layout.addWidget(sep2)

        recent_header = QLabel("Recent")
        recent_header.setObjectName("recentHeader")
        layout.addWidget(recent_header)

        self._history_list = QListWidget()
        self._history_list.setMinimumHeight(100)
        self._history_list.setMaximumHeight(150)
        self._history_list.setAlternatingRowColors(True)
        layout.addWidget(self._history_list)

        self._speak_btn.clicked.connect(self._on_speak)
        self._stop_btn.clicked.connect(self._on_stop)
        self._speed_slider.valueChanged.connect(self._on_speed_changed)
        self._history_list.itemDoubleClicked.connect(self._on_history_click)
        self._text_input.installEventFilter(self)

    def _connect_signals(self):
        self._signals.speak_done.connect(self._on_speak_done)
        self._signals.speak_error.connect(self._on_speak_error)
        self._signals.status_update.connect(self._on_status_update)

    def _init_voice(self):
        try:
            self._engine = TTSEngine(self._model_path)
            name = Path(self._model_path).stem
            self._voice_combo.addItem(name)
            self._voice_combo.setEnabled(False)
            self._signals.status_update.emit("Ready", True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load voice:\n{e}")
            self._signals.status_update.emit("Voice load failed", False)

    def _init_mic(self):
        if self._mic.is_active():
            self._signals.status_update.emit("Virtual Mic Active", True)
        else:
            if self._mic.start():
                self._signals.status_update.emit("Virtual Mic Active", True)
            else:
                self._signals.status_update.emit("Virtual Mic: start failed", False)

    def _on_speak(self):
        text = self._text_input.toPlainText().strip()
        if not text or not self._engine or self._speaking:
            return

        if not self._mic.is_active():
            QMessageBox.warning(self, "Virtual Mic", "Virtual microphone is not active.")
            return

        self._speaking = True
        self._speak_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._status_label.setText("Generating speech...")
        speed = self._speed_slider.value() / 100.0

        def task():
            tmp_path = None
            try:
                self._signals.status_update.emit("Synthesizing...", True)
                wav_data = self._engine.synthesize(text, speed)
                tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                tmp_path = tmp.name
                tmp.close()
                with open(tmp_path, "wb") as f:
                    f.write(wav_data)
                self._signals.status_update.emit("Playing...", True)
                self._player.play_wav_file(tmp_path, self._mic.get_sink_name())
                self._player.wait()
                self._signals.speak_done.emit()
            except Exception as e:
                self._signals.speak_error.emit(str(e))
            finally:
                if tmp_path:
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass

        threading.Thread(target=task, daemon=True).start()

    def _on_stop(self):
        self._player.stop()
        if self._engine:
            self._engine.stop()
        self._speaking = False
        self._speak_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._status_label.setText("Stopped")

    def _on_speak_done(self):
        self._speaking = False
        self._speak_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        if self._player.is_playing():
            self._status_label.setText("Playing...")
        else:
            self._status_label.setText("Virtual Mic Active")
        self._add_history(self._text_input.toPlainText().strip())

    def _on_speak_error(self, msg):
        self._speaking = False
        self._speak_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._status_label.setText("Error")
        QMessageBox.warning(self, "Error", msg)

    def _on_status_update(self, msg, ok):
        self._status_label.setText(msg)

    def _on_speed_changed(self, val):
        self._speed_label.setText(f"{val / 100:.1f}x")

    def _on_history_click(self, item):
        self._text_input.setPlainText(item.text())

    def _add_history(self, text):
        if text in self._history:
            self._history.remove(text)
        self._history.insert(0, text)
        if len(self._history) > 20:
            self._history = self._history[:20]
        self._refresh_history()
        self._save_history()

    def _refresh_history(self):
        self._history_list.clear()
        for item in self._history:
            display = item[:80] + "..." if len(item) > 80 else item
            self._history_list.addItem(display)

    def _init_history(self):
        try:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r") as f:
                    self._history = json.load(f)
                self._refresh_history()
        except Exception:
            pass

    def _save_history(self):
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(self._history, f)
        except Exception:
            pass

    def eventFilter(self, obj, event):
        if obj is self._text_input:
            if event.type() == event.KeyPress and event.matches(Qt.CTRL | Qt.Key_Return):
                self._on_speak()
                return True
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        self._player.stop()
        self._mic.stop()
        super().closeEvent(event)
