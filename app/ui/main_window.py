"""Main application window with fluent navigation."""

from qfluentwidgets import (
    FluentWindow, FluentIcon, NavigationItemPosition,
    InfoBar, InfoBarPosition,
)
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSize, QTimer

from app.config import AppConfig
from app.core.pipeline import Pipeline
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
            "主页",
        )
        self.addSubInterface(
            self.settings_page,
            FluentIcon.SETTING,
            "设置",
        )
        self.addSubInterface(
            self.about_page,
            FluentIcon.INFO,
            "关于",
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
        signal_bus.playback_finished.connect(
            lambda: self._show_info("播放完成")
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
                "GPT-SoVITS API 未连接",
                f"无法连接到 {self.config.tts.api_url}，请确保 API 服务已启动",
            )

        # Check ref audio
        if not self.config.tts.ref_audio_path:
            self._show_warning(
                "未设置参考音频",
                "请在设置页面配置参考音频路径",
            )

        # Initialize ASR if enabled
        if self.config.asr.enabled:
            if not self.pipeline.asr_engine.is_model_available():
                self._show_warning(
                    "ASR 模型未找到",
                    "请下载 sherpa-onnx 模型到 models/ 目录，详见 models/README.md",
                )
            else:
                self.pipeline.initialize_asr()

        # Check virtual audio cable
        from app.common.audio_devices import get_output_devices
        devices = get_output_devices()
        has_cable = any("CABLE" in name.upper() or "VIRTUAL" in name.upper() for _, name in devices)
        if not has_cable:
            self._show_warning(
                "未检测到虚拟声卡",
                "未找到 VB-Audio Virtual Cable，VRChat 内播放功能将不可用",
            )

    def _on_generate(self):
        text = self.generation_page.text_edit.toPlainText().strip()
        if not text:
            self._show_error("请输入要合成的文本")
            return
        if not self.config.tts.ref_audio_path:
            self._show_error("请先在设置中配置参考音频路径")
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
            title="错误",
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
