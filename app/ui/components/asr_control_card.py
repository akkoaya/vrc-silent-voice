"""ASR status and control card widget."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt

from qfluentwidgets import (
    CardWidget, StrongBodyLabel, BodyLabel, PushButton,
    ProgressRing, InfoBadge, FluentIcon, ToolButton,
)


class ASRControlCard(CardWidget):
    """Card showing ASR recording state and recognized text."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)

        # Left: status indicator + label
        left = QVBoxLayout()
        left.setSpacing(4)

        status_row = QHBoxLayout()
        self.status_badge = InfoBadge.warning("待机")
        self.status_label = StrongBodyLabel("语音识别")
        status_row.addWidget(self.status_badge)
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        left.addLayout(status_row)

        self.text_label = BodyLabel("等待语音输入...")
        self.text_label.setStyleSheet("color: gray;")
        self.text_label.setWordWrap(True)
        left.addWidget(self.text_label)

        layout.addLayout(left, stretch=1)

        # Right: progress ring (when recording)
        self.progress_ring = ProgressRing()
        self.progress_ring.setFixedSize(36, 36)
        self.progress_ring.setRange(0, 0)  # indeterminate
        self.progress_ring.hide()
        layout.addWidget(self.progress_ring)

    def set_recording(self, recording: bool):
        if recording:
            self.status_badge.deleteLater()
            self.status_badge = InfoBadge.error("录音中")
            h = self.layout().itemAt(0).layout().itemAt(0).layout()
            h.insertWidget(0, self.status_badge)
            self.progress_ring.show()
            self.text_label.setStyleSheet("color: inherit;")
        else:
            self.status_badge.deleteLater()
            self.status_badge = InfoBadge.warning("待机")
            h = self.layout().itemAt(0).layout().itemAt(0).layout()
            h.insertWidget(0, self.status_badge)
            self.progress_ring.hide()

    def set_text(self, text: str):
        self.text_label.setText(text if text else "等待语音输入...")
        if not text:
            self.text_label.setStyleSheet("color: gray;")
        else:
            self.text_label.setStyleSheet("")
