import sys

from PyQt6.QtWidgets import QApplication

from app.config import AppConfig
from app.i18n import set_language
from app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    config = AppConfig.load()
    set_language(config.language)

    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
