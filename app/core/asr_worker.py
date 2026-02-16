"""ASR Worker: QThread for microphone capture and real-time recognition."""

from __future__ import annotations

from typing import Optional

import numpy as np
import sounddevice as sd
from PyQt5.QtCore import QThread, pyqtSignal

from app.common.audio_devices import find_device_by_name
from app.core.asr_engine import ASREngine


class ASRWorker(QThread):
    """Captures audio from microphone and feeds it to ASR engine in real-time."""

    text_partial = pyqtSignal(str)   # partial recognition result
    text_final = pyqtSignal(str)     # final result (endpoint detected)
    error = pyqtSignal(str)
    state_changed = pyqtSignal(bool) # recording state

    def __init__(
        self,
        engine: ASREngine,
        microphone_name: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.engine = engine
        self.microphone_name = microphone_name
        self._running = False
        self._recording = False
        self._stream: Optional[sd.InputStream] = None

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start_recording(self):
        """Start capturing audio."""
        self._recording = True
        self.state_changed.emit(True)

    def stop_recording(self):
        """Stop capturing audio and emit final result."""
        if self._recording:
            self._recording = False
            self.state_changed.emit(False)
            # Get any remaining text
            result = self.engine.get_partial_result()
            if result:
                self.text_final.emit(result)
            self.engine.reset()

    def run(self):
        """Main thread loop: open mic stream and process audio."""
        if not self.engine.is_initialized:
            self.error.emit("ASR引擎未初始化，请检查模型文件")
            return

        self._running = True
        device_idx = find_device_by_name(self.microphone_name, is_input=True)
        if device_idx < 0:
            device_idx = None  # use default

        try:
            with sd.InputStream(
                samplerate=self.engine.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=int(self.engine.sample_rate * 0.1),  # 100ms chunks
                device=device_idx,
            ) as stream:
                self._stream = stream
                while self._running:
                    if not self._recording:
                        self.msleep(50)
                        continue

                    data, overflowed = stream.read(int(self.engine.sample_rate * 0.1))
                    if data.size == 0:
                        continue

                    samples = data.flatten()
                    self.engine.accept_waveform(samples)

                    text = self.engine.get_partial_result()
                    if text:
                        self.text_partial.emit(text)

                    if self.engine.is_endpoint():
                        final_text = self.engine.get_partial_result()
                        if final_text:
                            self.text_final.emit(final_text)
                        self.engine.reset()

        except Exception as e:
            self.error.emit(f"麦克风错误: {e}")
        finally:
            self._running = False
            self._stream = None

    def stop(self):
        """Stop the worker thread."""
        self._running = False
        self._recording = False
        self.wait(3000)
