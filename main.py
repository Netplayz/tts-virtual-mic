import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from ui.main_window import MainWindow


def resource_dir() -> str:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def load_stylesheet() -> str:
    path = os.path.join(resource_dir(), "resources", "style.qss")
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def find_model() -> str:
    base = Path(resource_dir()) / "voices"
    for onnx_file in base.rglob("*.onnx"):
        return str(onnx_file)
    return ""


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TTS Virtual Microphone")
    app.setOrganizationName("TTS-VM")

    font = QFont("Sans Serif", 10)
    app.setFont(font)

    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    model_path = find_model()
    if not model_path:
        from PyQt5.QtWidgets import QMessageBox
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Critical)
        mb.setWindowTitle("Error")
        mb.setText("No voice model found in voices/ directory.")
        mb.setInformativeText("Please place .onnx and .onnx.json files in the voices/ folder.")
        mb.exec()
        sys.exit(1)

    window = MainWindow(model_path)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
