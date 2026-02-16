"""Main application window with fluent navigation."""

from qfluentwidgets import FluentWindow, FluentIcon, NavigationItemPosition
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSize

from app.ui.generation_page import GenerationPage


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()

        self.generation_page = GenerationPage(self)

        self._init_navigation()
        self._init_window()

    def _init_navigation(self):
        self.addSubInterface(
            self.generation_page,
            FluentIcon.MICROPHONE,
            "生成",
        )

    def _init_window(self):
        self.resize(960, 700)
        self.setMinimumSize(QSize(760, 500))
        self.setWindowTitle("VRC Silent Voice")

        # Center on screen
        desktop = QApplication.primaryScreen()
        if desktop:
            geo = desktop.availableGeometry()
            self.move(
                (geo.width() - self.width()) // 2,
                (geo.height() - self.height()) // 2,
            )
