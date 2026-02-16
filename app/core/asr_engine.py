"""Sherpa-ONNX ASR engine wrapper for streaming speech recognition."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import sherpa_onnx


class ASREngine:
    """Wraps sherpa-onnx OnlineRecognizer for streaming ASR."""

    def __init__(
        self,
        model_dir: str = "models",
        language: str = "zh",
        sample_rate: int = 16000,
    ):
        self.model_dir = Path(model_dir)
        self.language = language
        self.sample_rate = sample_rate
        self._recognizer: Optional[sherpa_onnx.OnlineRecognizer] = None
        self._stream: Optional[sherpa_onnx.OnlineStream] = None

    def is_model_available(self) -> bool:
        """Check if required model files exist."""
        model_path = self._find_model_path()
        return model_path is not None

    def _find_model_path(self) -> Optional[Path]:
        """Find model directory based on language."""
        if not self.model_dir.exists():
            return None

        # Look for subdirectories containing model files
        for subdir in self.model_dir.iterdir():
            if not subdir.is_dir():
                continue
            # Check for paraformer model files (encoder.onnx, decoder.onnx, tokens.txt)
            has_encoder = (subdir / "encoder.onnx").exists() or (subdir / "encoder.int8.onnx").exists()
            has_decoder = (subdir / "decoder.onnx").exists() or (subdir / "decoder.int8.onnx").exists()
            has_tokens = (subdir / "tokens.txt").exists()
            if has_encoder and has_decoder and has_tokens:
                return subdir

        # Check model_dir itself
        has_encoder = (self.model_dir / "encoder.onnx").exists() or (self.model_dir / "encoder.int8.onnx").exists()
        has_decoder = (self.model_dir / "decoder.onnx").exists() or (self.model_dir / "decoder.int8.onnx").exists()
        has_tokens = (self.model_dir / "tokens.txt").exists()
        if has_encoder and has_decoder and has_tokens:
            return self.model_dir

        return None

    def initialize(self) -> bool:
        """Initialize the recognizer with found model files."""
        model_path = self._find_model_path()
        if model_path is None:
            return False

        # Determine model file names (prefer int8 for speed)
        encoder = str(model_path / "encoder.int8.onnx") if (model_path / "encoder.int8.onnx").exists() else str(model_path / "encoder.onnx")
        decoder = str(model_path / "decoder.int8.onnx") if (model_path / "decoder.int8.onnx").exists() else str(model_path / "decoder.onnx")
        tokens = str(model_path / "tokens.txt")

        try:
            self._recognizer = sherpa_onnx.OnlineRecognizer.from_paraformer(
                tokens=tokens,
                encoder=encoder,
                decoder=decoder,
                num_threads=4,
                sample_rate=self.sample_rate,
                feature_dim=80,
                enable_endpoint_detection=True,
                rule1_min_trailing_silence=2.4,
                rule2_min_trailing_silence=1.0,
                rule3_min_utterance_length=20.0,
                decoding_method="greedy_search",
                provider="cpu",
            )
            self._stream = self._recognizer.create_stream()
            return True
        except Exception as e:
            print(f"ASR engine initialization failed: {e}")
            self._recognizer = None
            return False

    @property
    def is_initialized(self) -> bool:
        return self._recognizer is not None

    def accept_waveform(self, samples) -> None:
        """Feed audio samples (float32, mono, sample_rate) to the recognizer."""
        if self._stream is None:
            return
        self._stream.accept_waveform(self.sample_rate, samples.tolist())

    def get_partial_result(self) -> str:
        """Get the current partial recognition result."""
        if self._recognizer is None or self._stream is None:
            return ""
        while self._recognizer.is_ready(self._stream):
            self._recognizer.decode_stream(self._stream)
        return self._recognizer.get_result(self._stream).strip()

    def is_endpoint(self) -> bool:
        """Check if an endpoint (end of utterance) is detected."""
        if self._recognizer is None or self._stream is None:
            return False
        return self._recognizer.is_endpoint(self._stream)

    def reset(self) -> None:
        """Reset the stream for a new utterance."""
        if self._recognizer is not None and self._stream is not None:
            self._recognizer.reset(self._stream)

    def shutdown(self) -> None:
        """Release resources."""
        self._stream = None
        self._recognizer = None
