"""Dual-device audio player: physical speaker + virtual cable."""

from __future__ import annotations

import io
import threading
from typing import Optional

import numpy as np
import sounddevice as sd
import soundfile as sf

from app.common.audio_devices import find_device_by_name


class AudioPlayer:
    """Plays WAV audio simultaneously on two output devices."""

    def __init__(
        self,
        speaker_device_name: str = "",
        virtual_device_name: str = "",
    ):
        self.speaker_device_name = speaker_device_name
        self.virtual_device_name = virtual_device_name
        self._playing = False

    def update_devices(self, speaker_name: str, virtual_name: str):
        self.speaker_device_name = speaker_name
        self.virtual_device_name = virtual_name

    def play_wav_bytes(
        self,
        wav_data: bytes,
        on_finished: Optional[callable] = None,
    ):
        """Play WAV audio bytes on both devices concurrently."""
        data, samplerate = sf.read(io.BytesIO(wav_data), dtype="float32")
        self.play_array(data, samplerate, on_finished)

    def play_array(
        self,
        data: np.ndarray,
        samplerate: int,
        on_finished: Optional[callable] = None,
    ):
        """Play numpy audio array on both devices concurrently."""
        self._playing = True

        speaker_idx = find_device_by_name(self.speaker_device_name, is_input=False)
        virtual_idx = find_device_by_name(self.virtual_device_name, is_input=False)

        threads = []

        if speaker_idx >= 0:
            t = threading.Thread(
                target=self._play_on_device,
                args=(data, samplerate, speaker_idx),
                daemon=True,
            )
            threads.append(t)

        if virtual_idx >= 0:
            t = threading.Thread(
                target=self._play_on_device,
                args=(data, samplerate, virtual_idx),
                daemon=True,
            )
            threads.append(t)

        # If no specific devices found, play on default
        if not threads:
            t = threading.Thread(
                target=self._play_on_device,
                args=(data, samplerate, None),
                daemon=True,
            )
            threads.append(t)

        for t in threads:
            t.start()

        # Wait in background thread to avoid blocking
        def _wait():
            for t in threads:
                t.join()
            self._playing = False
            if on_finished:
                on_finished()

        threading.Thread(target=_wait, daemon=True).start()

    @staticmethod
    def _play_on_device(data: np.ndarray, samplerate: int, device_idx: Optional[int]):
        try:
            sd.play(data, samplerate=samplerate, device=device_idx, blocking=True)
        except Exception as e:
            print(f"Audio playback error on device {device_idx}: {e}")

    @property
    def is_playing(self) -> bool:
        return self._playing

    def stop(self):
        sd.stop()
        self._playing = False
