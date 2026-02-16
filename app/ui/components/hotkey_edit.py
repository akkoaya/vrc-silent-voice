"""Custom hotkey capture input widget."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QMetaObject, Q_ARG, pyqtSlot

from qfluentwidgets import LineEdit, PushButton

from pynput import keyboard


class HotkeyEdit(QWidget):
    """A widget that captures a single key press and displays it."""

    hotkey_changed = pyqtSignal(str)

    def __init__(self, current_hotkey: str = "Key.f2", parent=None):
        super().__init__(parent)
        self._capturing = False
        self._listener = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.display = LineEdit()
        self.display.setReadOnly(True)
        self.display.setText(current_hotkey)
        self.display.setMinimumWidth(140)
        layout.addWidget(self.display)

        self.capture_btn = PushButton("捕获按键")
        self.capture_btn.setFixedWidth(90)
        self.capture_btn.clicked.connect(self._toggle_capture)
        layout.addWidget(self.capture_btn)

    def _toggle_capture(self):
        if self._capturing:
            self._stop_capture()
        else:
            self._start_capture()

    def _start_capture(self):
        self._capturing = True
        self.capture_btn.setText("取消")
        self.display.setText("按下任意键...")
        self.display.setStyleSheet("color: orange;")

        self._listener = keyboard.Listener(on_press=self._on_key_press)
        self._listener.daemon = True
        self._listener.start()

    def _stop_capture(self):
        self._capturing = False
        self.capture_btn.setText("捕获按键")
        self.display.setStyleSheet("")
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _on_key_press(self, key):
        key_str = self._key_to_string(key)
        QMetaObject.invokeMethod(
            self, "_set_hotkey",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, key_str),
        )
        return False  # Stop listener after one key

    @staticmethod
    def _key_to_string(key) -> str:
        if isinstance(key, keyboard.Key):
            return f"Key.{key.name}"
        if isinstance(key, keyboard.KeyCode):
            if key.char:
                return key.char
            if key.vk:
                return str(key.vk)
        return str(key)

    @pyqtSlot(str)
    def _set_hotkey(self, key_str: str):
        self.display.setText(key_str)
        self._stop_capture()
        self.hotkey_changed.emit(key_str)

    def value(self) -> str:
        return self.display.text()
