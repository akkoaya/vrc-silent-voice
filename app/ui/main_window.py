"""Main application window with fluent navigation."""

from qfluentwidgets import (
    FluentWindow, FluentIcon, NavigationItemPosition,
    InfoBar, InfoBarPosition, RoundMenu, Action, NavigationToolButton,
)
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSize, QTimer
from PyQt6.QtGui import QIcon

from app.config import AppConfig
from app.core.pipeline import Pipeline
from app.i18n import t, set_language, get_language, LANGUAGES
from app.signals import signal_bus
from app.ui.generation_page import GenerationPage
from app.ui.settings_page import SettingsPage
from app.ui.about_page import AboutPage


class MainWindow(FluentWindow):
    def __init__(self, config: AppConfig = None):
        super().__init__()
        self.config = config or AppConfig.load()

        # Create pipeline
        self.pipeline = Pipeline(self.config, parent=self)

        # Create pages
        self.generation_page = GenerationPage(self.config, self)
        self.settings_page = SettingsPage(self.config, self)
        self.about_page = AboutPage(self)

        self._init_navigation()
        self._init_window()
        self._connect_signals()

        # Deferred initialization after window is shown
        QTimer.singleShot(500, self._deferred_init)

    def _init_navigation(self):
        self.addSubInterface(
            self.generation_page,
            FluentIcon.HOME,
            t("nav.home"),
        )
        self.addSubInterface(
            self.settings_page,
            FluentIcon.SETTING,
            t("nav.settings"),
        )

        # Language switch button (above About)
        self.lang_btn = NavigationToolButton(FluentIcon.LANGUAGE)
        self.lang_btn.clicked.connect(self._show_language_menu)
        self.navigationInterface.addWidget(
            "languageButton",
            self.lang_btn,
            onClick=self._show_language_menu,
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(
            self.about_page,
            FluentIcon.INFO,
            t("nav.about"),
            position=NavigationItemPosition.BOTTOM,
        )

    def _show_language_menu(self):
        menu = RoundMenu(parent=self)
        current = get_language()
        for code, name in LANGUAGES.items():
            action = Action(name, triggered=lambda checked, c=code: self._change_language(c))
            action.setEnabled(code != current)
            menu.addAction(action)
        menu.exec(self.lang_btn.mapToGlobal(self.lang_btn.rect().center()))

    def _change_language(self, lang: str):
        self.config.language = lang
        self.config.save()
        InfoBar.warning(
            title=t("lang.changed_title"),
            content=t("lang.changed"),
            parent=self,
            position=InfoBarPosition.TOP,
            duration=8000,
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
        signal_bus.playback_finished.connect(
            lambda: self._show_info(t("msg.playback_finished"))
        )

        # Error handling
        signal_bus.tts_error.connect(self._show_error)

        # Settings → pipeline updates
        signal_bus.config_changed.connect(self._on_config_changed)

    def _deferred_init(self):
        """Run after window is visible to show startup warnings."""
        # Check TTS connection
        if not self.pipeline.check_tts_connection():
            self._show_warning(
                t("msg.tts_not_connected"),
                t("msg.tts_not_connected_desc", url=self.config.tts.api_url),
            )

        # Check ref audio
        if not self.config.tts.ref_audio_path:
            self._show_warning(
                t("msg.no_ref_audio"),
                t("msg.no_ref_audio_desc"),
            )

        # Initialize ASR if enabled
        if self.config.asr.enabled:
            if not self.pipeline.asr_engine.is_model_available():
                self._show_warning(
                    t("msg.asr_model_missing"),
                    t("msg.asr_model_missing_desc"),
                )
            else:
                self.pipeline.initialize_asr()

        # Check virtual audio cable
        from app.common.audio_devices import get_output_devices
        devices = get_output_devices()
        has_cable = any("CABLE" in name.upper() or "VIRTUAL" in name.upper() for _, name in devices)
        if not has_cable:
            self._show_warning(
                t("msg.no_virtual_cable"),
                t("msg.no_virtual_cable_desc"),
            )

    def _on_generate(self):
        text = self.generation_page.text_edit.toPlainText().strip()
        if not text:
            self._show_error(t("msg.empty_text"))
            return
        if not self.config.tts.ref_audio_path:
            self._show_error(t("msg.no_ref_audio_error"))
            return
        params = self.generation_page.get_tts_params()
        self.pipeline.synthesize(text, **params)

    def _on_stop(self):
        self.pipeline.audio_player.stop()
        self.generation_page.set_busy(False)

    def _on_asr_final(self, text: str):
        self.generation_page.text_edit.setPlainText(text)

    def _on_config_changed(self):
        self.pipeline.update_audio_devices()
        self.pipeline.update_asr_settings()

    def _show_error(self, message: str):
        InfoBar.error(
            title=t("msg.error"),
            content=message,
            parent=self,
            position=InfoBarPosition.TOP,
            duration=5000,
        )

    def _show_warning(self, title: str, message: str):
        InfoBar.warning(
            title=title,
            content=message,
            parent=self,
            position=InfoBarPosition.TOP,
            duration=8000,
        )

    def _show_info(self, message: str):
        InfoBar.info(
            title="",
            content=message,
            parent=self,
            position=InfoBarPosition.TOP,
            duration=3000,
        )

    def closeEvent(self, event):
        self.generation_page.save_config()
        self.settings_page.save_config()
        self.pipeline.shutdown()
        super().closeEvent(event)
