"""Main application window with fluent navigation."""

from qfluentwidgets import FluentWindow, FluentIcon, NavigationItemPosition
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSize

from app.config import AppConfig
from app.ui.generation_page import GenerationPage
from app.ui.settings_page import SettingsPage


class MainWindow(FluentWindow):
    def __init__(self, config: AppConfig = None):
        super().__init__()
        self.config = config or AppConfig.load()

        self.generation_page = GenerationPage(self)
        self.settings_page = SettingsPage(self.config, self)

        self._init_navigation()
        self._init_window()

    def _init_navigation(self):
        self.addSubInterface(
            self.generation_page,
            FluentIcon.MICROPHONE,
            "生成",
        )
        self.addSubInterface(
            self.settings_page,
            FluentIcon.SETTING,
            "设置",
            position=NavigationItemPosition.BOTTOM,
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

    def closeEvent(self, event):
        self.settings_page.save_config()
        super().closeEvent(event)
