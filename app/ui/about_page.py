"""About page - project information."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from qfluentwidgets import (
    ScrollArea, StrongBodyLabel, BodyLabel, HyperlinkLabel, CardWidget,
)

from app.i18n import t


VERSION = "1.1.0"


class AboutPage(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("aboutPage")

        self.scroll_widget = QWidget()
        self.v_layout = QVBoxLayout(self.scroll_widget)
        self.v_layout.setContentsMargins(36, 20, 36, 20)
        self.v_layout.setSpacing(16)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._init_content()

        self.setWidget(self.scroll_widget)
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_widget.setStyleSheet("background: transparent;")

    def _init_content(self):
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = StrongBodyLabel("VRC Silent Voice")
        title.setStyleSheet("font-size: 22px;")
        layout.addWidget(title)

        layout.addWidget(BodyLabel(t("about.version", version=VERSION)))
        layout.addWidget(BodyLabel(t("about.description")))
        layout.addWidget(BodyLabel(""))

        layout.addWidget(StrongBodyLabel(t("about.author")))
        layout.addWidget(BodyLabel("淡奶猫眠包"))

        layout.addWidget(BodyLabel(""))
        layout.addWidget(StrongBodyLabel(t("about.repo")))
        link = HyperlinkLabel("https://github.com/akkoaya/vrc-silent-voice")
        link.setUrl("https://github.com/akkoaya/vrc-silent-voice")
        layout.addWidget(link)

        layout.addWidget(BodyLabel(""))
        layout.addWidget(StrongBodyLabel(t("about.tech_stack")))
        layout.addWidget(BodyLabel("Python 3.12 / PyQt6 / PyQt-Fluent-Widgets / GPT-SoVITS / Sherpa-ONNX"))

        self.v_layout.addWidget(card)
