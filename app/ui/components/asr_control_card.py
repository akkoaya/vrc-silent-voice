"""ASR status and control card widget."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt

from qfluentwidgets import (
    CardWidget, StrongBodyLabel, BodyLabel, PushButton,
    ProgressRing, InfoBadge, FluentIcon, ToolButton,
)

from app.i18n import t


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
        self.status_badge = InfoBadge.warning(t("asr.standby"))
        self.status_label = StrongBodyLabel(t("asr.title"))
        status_row.addWidget(self.status_badge)
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        left.addLayout(status_row)

        self.text_label = BodyLabel(t("asr.waiting"))
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
            self.status_badge = InfoBadge.error(t("asr.recording"))
            h = self.layout().itemAt(0).layout().itemAt(0).layout()
            h.insertWidget(0, self.status_badge)
            self.progress_ring.show()
            self.text_label.setStyleSheet("color: inherit;")
        else:
            self.status_badge.deleteLater()
            self.status_badge = InfoBadge.warning(t("asr.standby"))
            h = self.layout().itemAt(0).layout().itemAt(0).layout()
            h.insertWidget(0, self.status_badge)
            self.progress_ring.hide()

    def set_text(self, text: str):
        self.text_label.setText(text if text else t("asr.waiting"))
        if not text:
            self.text_label.setStyleSheet("color: gray;")
        else:
            self.text_label.setStyleSheet("")
