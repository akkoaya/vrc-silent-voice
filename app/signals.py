"""Global signal bus for cross-component communication."""

from PyQt6.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    # ASR signals
    asr_text_recognized = pyqtSignal(str)       # partial/final recognized text
    asr_final_result = pyqtSignal(str)           # final ASR result
    asr_state_changed = pyqtSignal(bool)         # recording started/stopped

    # TTS signals
    tts_started = pyqtSignal()
    tts_finished = pyqtSignal()
    tts_error = pyqtSignal(str)
    tts_audio_ready = pyqtSignal(bytes)          # WAV audio data

    # Playback signals
    playback_started = pyqtSignal()
    playback_finished = pyqtSignal()

    # Pipeline signals
    pipeline_busy = pyqtSignal(bool)             # pipeline processing state

    # Config signals
    config_changed = pyqtSignal()


signal_bus = SignalBus()
