"""Generation page - text input, ASR control, TTS parameters, and generation."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class GenerationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("generationPage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 20, 36, 20)

        title = QLabel("语音生成")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        placeholder = QLabel("生成页面 - 将在后续阶段完善")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
        layout.addStretch()
