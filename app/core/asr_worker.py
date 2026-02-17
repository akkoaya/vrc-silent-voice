"""ASR Worker: QThread for microphone capture and real-time recognition."""

from __future__ import annotations

from typing import Optional

import numpy as np
import sounddevice as sd
from PyQt6.QtCore import QThread, pyqtSignal

from app.common.audio_devices import find_device_by_name
from app.core.asr_engine import ASREngine


def _resample(data: np.ndarray, src_rate: int, dst_rate: int) -> np.ndarray:
    """Simple linear-interpolation resample from src_rate to dst_rate."""
    if src_rate == dst_rate:
        return data
    ratio = dst_rate / src_rate
    n_samples = int(len(data) * ratio)
    indices = np.arange(n_samples) / ratio
    indices_floor = np.floor(indices).astype(int)
    indices_ceil = np.minimum(indices_floor + 1, len(data) - 1)
    frac = indices - indices_floor
    return data[indices_floor] * (1 - frac) + data[indices_ceil] * frac


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
            # Feed ~0.8s of silence to flush the decoder's internal buffer,
            # ensuring the last token is fully recognized.
            silence = np.zeros(int(self.engine.sample_rate * 0.8), dtype=np.float32)
            self.engine.accept_waveform(silence)
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

        # Query device's default sample rate
        target_rate = self.engine.sample_rate
        try:
            info = sd.query_devices(device_idx, kind="input")
            device_rate = int(info["default_samplerate"])
        except Exception:
            device_rate = target_rate

        try:
            with sd.InputStream(
                samplerate=device_rate,
                channels=1,
                dtype="float32",
                blocksize=int(device_rate * 0.1),  # 100ms chunks
                device=device_idx,
            ) as stream:
                self._stream = stream
                while self._running:
                    if not self._recording:
                        self.msleep(50)
                        continue

                    data, overflowed = stream.read(int(device_rate * 0.1))
                    if data.size == 0:
                        continue

                    samples = data.flatten()
                    # Resample to engine's expected rate if needed
                    if device_rate != target_rate:
                        samples = _resample(samples, device_rate, target_rate)

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
