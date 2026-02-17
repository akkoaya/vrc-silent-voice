import sys
import platform

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from app.config import AppConfig
from app.i18n import set_language
from app.ui.main_window import MainWindow


def _default_font() -> QFont:
    """Return a CJK-friendly font for the current platform."""
    system = platform.system()
    if system == "Windows":
        return QFont("Microsoft YaHei UI", 9)
    elif system == "Darwin":
        return QFont("PingFang SC", 9)
    else:
        return QFont("Noto Sans CJK SC", 9)


def main():
    app = QApplication(sys.argv)
    app.setFont(_default_font())

    config = AppConfig.load()
    set_language(config.language)

    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
