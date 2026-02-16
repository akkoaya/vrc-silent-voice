"""Main application window with fluent navigation."""

from qfluentwidgets import FluentWindow, FluentIcon, NavigationItemPosition, InfoBar, InfoBarPosition
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSize

from app.config import AppConfig
from app.core.pipeline import Pipeline
from app.signals import signal_bus
from app.ui.generation_page import GenerationPage
from app.ui.settings_page import SettingsPage


class MainWindow(FluentWindow):
    def __init__(self, config: AppConfig = None):
        super().__init__()
        self.config = config or AppConfig.load()

        # Create pipeline
        self.pipeline = Pipeline(self.config, parent=self)

        # Create pages
        self.generation_page = GenerationPage(self)
        self.settings_page = SettingsPage(self.config, self)

        self._init_navigation()
        self._init_window()
        self._connect_signals()

        # Initialize ASR if enabled
        if self.config.asr.enabled:
            self.pipeline.initialize_asr()

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

    def _connect_signals(self):
        # Generation page → pipeline
        self.generation_page.generate_btn.clicked.connect(self._on_generate)
        self.generation_page.stop_btn.clicked.connect(self._on_stop)

        # Pipeline → generation page
        signal_bus.pipeline_busy.connect(self.generation_page.set_busy)
        signal_bus.asr_text_recognized.connect(self.generation_page.asr_card.set_text)
        signal_bus.asr_final_result.connect(self._on_asr_final)
        signal_bus.asr_state_changed.connect(self.generation_page.asr_card.set_recording)

        # Error handling
        signal_bus.tts_error.connect(self._show_error)

        # Settings → pipeline updates
        signal_bus.config_changed.connect(self._on_config_changed)

    def _on_generate(self):
        text = self.generation_page.text_edit.toPlainText().strip()
        if not text:
            self._show_error("请输入要合成的文本")
            return
        params = self.generation_page.get_tts_params()
        self.pipeline.synthesize(text, **params)

    def _on_stop(self):
        self.pipeline.audio_player.stop()
        self.generation_page.set_busy(False)

    def _on_asr_final(self, text: str):
        # Set recognized text in text edit
        self.generation_page.text_edit.setPlainText(text)

    def _on_config_changed(self):
        self.pipeline.update_audio_devices()
        self.pipeline.update_asr_settings()

    def _show_error(self, message: str):
        InfoBar.error(
            title="错误",
            content=message,
            parent=self,
            position=InfoBarPosition.TOP,
            duration=5000,
        )

    def closeEvent(self, event):
        self.settings_page.save_config()
        self.pipeline.shutdown()
        super().closeEvent(event)
