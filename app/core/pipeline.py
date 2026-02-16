"""Pipeline orchestrator: ASR → TTS → AudioPlayer."""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import QObject, QThread, pyqtSignal

from app.config import AppConfig
from app.core.asr_engine import ASREngine
from app.core.asr_worker import ASRWorker
from app.core.audio_player import AudioPlayer
from app.core.hotkey_manager import HotkeyManager
from app.core.tts_client import TTSClient
from app.signals import signal_bus


class TTSWorker(QThread):
    """Background thread for TTS synthesis to avoid blocking UI."""

    finished = pyqtSignal(bytes)  # WAV audio data
    error = pyqtSignal(str)

    def __init__(self, client: TTSClient, text: str, params: dict = None, parent=None):
        super().__init__(parent)
        self.client = client
        self.text = text
        self.params = params or {}

    def run(self):
        try:
            wav_data = self.client.synthesize(self.text, **self.params)
            self.finished.emit(wav_data)
        except Exception as e:
            self.error.emit(str(e))


class Pipeline(QObject):
    """Orchestrates ASR → TTS → AudioPlayer flow."""

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config

        # Core components
        self.tts_client = TTSClient(config.tts)
        self.audio_player = AudioPlayer(
            speaker_device_name=config.tts.speaker_device_name,
            virtual_device_name=config.tts.virtual_device_name,
        )
        self.asr_engine = ASREngine(
            model_dir=config.asr.model_dir,
            language=config.asr.language,
            sample_rate=config.asr.sample_rate,
        )
        self.asr_worker: Optional[ASRWorker] = None
        self.hotkey_manager: Optional[HotkeyManager] = None
        self._tts_worker: Optional[TTSWorker] = None
        self._busy = False

    def initialize_asr(self) -> bool:
        """Initialize ASR engine and start worker thread."""
        if not self.config.asr.enabled:
            return True

        if not self.asr_engine.initialize():
            signal_bus.tts_error.emit("ASR模型未找到，请下载模型到 models/ 目录")
            return False

        self.asr_worker = ASRWorker(
            engine=self.asr_engine,
            microphone_name=self.config.asr.microphone_name,
        )
        self.asr_worker.text_partial.connect(self._on_asr_partial)
        self.asr_worker.text_final.connect(self._on_asr_final)
        self.asr_worker.error.connect(lambda e: signal_bus.tts_error.emit(e))
        self.asr_worker.state_changed.connect(signal_bus.asr_state_changed.emit)

        # Set up hotkey
        self.hotkey_manager = HotkeyManager(
            hotkey=self.config.asr.hotkey,
            mode=self.config.asr.voice_mode,
            on_start=self._on_hotkey_start,
            on_stop=self._on_hotkey_stop,
        )

        self.asr_worker.start()
        self.hotkey_manager.start()
        return True

    def _on_hotkey_start(self):
        if self.asr_worker:
            self.asr_worker.start_recording()

    def _on_hotkey_stop(self):
        if self.asr_worker:
            self.asr_worker.stop_recording()

    def _on_asr_partial(self, text: str):
        signal_bus.asr_text_recognized.emit(text)

    def _on_asr_final(self, text: str):
        signal_bus.asr_final_result.emit(text)
        # Auto-synthesize final ASR result
        self.synthesize(text)

    def synthesize(self, text: str, **params):
        """Send text to TTS and play result."""
        if not text.strip():
            return
        if self._busy:
            signal_bus.tts_error.emit("正在合成中，请稍候...")
            return

        self._busy = True
        signal_bus.pipeline_busy.emit(True)
        signal_bus.tts_started.emit()

        self._tts_worker = TTSWorker(self.tts_client, text, params)
        self._tts_worker.finished.connect(self._on_tts_done)
        self._tts_worker.error.connect(self._on_tts_error)
        self._tts_worker.start()

    def _on_tts_done(self, wav_data: bytes):
        signal_bus.tts_finished.emit()
        signal_bus.tts_audio_ready.emit(wav_data)
        signal_bus.playback_started.emit()

        self.audio_player.play_wav_bytes(
            wav_data,
            on_finished=self._on_playback_done,
        )

    def _on_tts_error(self, error: str):
        self._busy = False
        signal_bus.pipeline_busy.emit(False)
        signal_bus.tts_error.emit(error)

    def _on_playback_done(self):
        self._busy = False
        signal_bus.pipeline_busy.emit(False)
        signal_bus.playback_finished.emit()

    def update_audio_devices(self):
        """Update audio player devices from config."""
        self.audio_player.update_devices(
            self.config.tts.speaker_device_name,
            self.config.tts.virtual_device_name,
        )

    def update_asr_settings(self):
        """Update ASR-related settings from config."""
        if self.hotkey_manager:
            self.hotkey_manager.update_hotkey(self.config.asr.hotkey)
            self.hotkey_manager.update_mode(self.config.asr.voice_mode)
        if self.asr_worker:
            self.asr_worker.microphone_name = self.config.asr.microphone_name

    def check_tts_connection(self) -> bool:
        return self.tts_client.check_connection()

    def shutdown(self):
        """Clean up all resources."""
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        if self.asr_worker:
            self.asr_worker.stop()
        if self._tts_worker and self._tts_worker.isRunning():
            self._tts_worker.quit()
            self._tts_worker.wait(2000)
        self.audio_player.stop()
        self.tts_client.close()
        self.asr_engine.shutdown()
