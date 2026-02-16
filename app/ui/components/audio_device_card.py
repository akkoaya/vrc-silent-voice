"""Audio device selector card widget."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from qfluentwidgets import (
    CardWidget, ComboBox, PushButton, StrongBodyLabel, BodyLabel, FluentIcon,
)

from app.common.audio_devices import get_input_devices, get_output_devices


class AudioDeviceCard(CardWidget):
    """Card with device ComboBox and refresh button."""

    def __init__(
        self,
        title: str,
        description: str,
        is_input: bool = False,
        current_device: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.is_input = is_input
        self.setFixedHeight(70)

        h_layout = QHBoxLayout(self)
        h_layout.setContentsMargins(20, 0, 20, 0)

        left = QVBoxLayout()
        left.setSpacing(2)
        left.addWidget(StrongBodyLabel(title))
        desc = BodyLabel(description)
        desc.setStyleSheet("color: gray; font-size: 12px;")
        left.addWidget(desc)
        h_layout.addLayout(left)
        h_layout.addStretch()

        self.combo = ComboBox()
        self.combo.setMinimumWidth(260)
        h_layout.addWidget(self.combo)

        self.refresh_btn = PushButton(FluentIcon.SYNC, "")
        self.refresh_btn.setFixedSize(36, 36)
        self.refresh_btn.clicked.connect(self.refresh_devices)
        h_layout.addWidget(self.refresh_btn)

        self._current_device = current_device
        self.refresh_devices()

    def refresh_devices(self):
        self.combo.clear()
        devices = get_input_devices() if self.is_input else get_output_devices()
        for idx, name in devices:
            self.combo.addItem(name)
        if self._current_device:
            self.combo.setCurrentText(self._current_device)

    def current_device_name(self) -> str:
        return self.combo.currentText()
