"""GPT-SoVITS V2 API HTTP client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import TTSConfig


class TTSClient:
    """Synchronous HTTP client for GPT-SoVITS V2 API."""

    def __init__(self, config: TTSConfig):
        self.config = config
        self._client = httpx.Client(timeout=60.0)

    @property
    def base_url(self) -> str:
        return self.config.api_url.rstrip("/")

    def check_connection(self) -> bool:
        try:
            r = self._client.get(self.base_url + "/docs")
            return r.status_code == 200
        except httpx.HTTPError:
            return False

    def synthesize(
        self,
        text: str,
        text_lang: Optional[str] = None,
        ref_audio_path: Optional[str] = None,
        prompt_text: Optional[str] = None,
        prompt_lang: Optional[str] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        temperature: Optional[float] = None,
        speed_factor: Optional[float] = None,
        text_split_method: Optional[str] = None,
        batch_size: Optional[int] = None,
        seed: Optional[int] = None,
        media_type: Optional[str] = None,
        streaming_mode: Optional[bool] = None,
        repetition_penalty: Optional[float] = None,
        sample_steps: Optional[int] = None,
        super_sampling: Optional[bool] = None,
    ) -> bytes:
        """Send text to TTS API and return WAV audio bytes."""
        cfg = self.config
        payload = {
            "text": text,
            "text_lang": text_lang or cfg.text_lang,
            "ref_audio_path": ref_audio_path or cfg.ref_audio_path,
            "prompt_text": prompt_text if prompt_text is not None else cfg.prompt_text,
            "prompt_lang": prompt_lang or cfg.prompt_lang,
            "top_k": top_k if top_k is not None else cfg.top_k,
            "top_p": top_p if top_p is not None else cfg.top_p,
            "temperature": temperature if temperature is not None else cfg.temperature,
            "speed_factor": speed_factor if speed_factor is not None else cfg.speed_factor,
            "text_split_method": text_split_method or cfg.text_split_method,
            "batch_size": batch_size if batch_size is not None else cfg.batch_size,
            "seed": seed if seed is not None else cfg.seed,
            "media_type": media_type or cfg.media_type,
            "streaming_mode": streaming_mode if streaming_mode is not None else cfg.streaming_mode,
            "repetition_penalty": repetition_penalty if repetition_penalty is not None else cfg.repetition_penalty,
            "sample_steps": sample_steps if sample_steps is not None else cfg.sample_steps,
            "super_sampling": super_sampling if super_sampling is not None else cfg.super_sampling,
        }

        r = self._client.post(self.base_url + "/tts", json=payload)
        r.raise_for_status()
        return r.content

    def set_gpt_weights(self, weights_path: str) -> bool:
        try:
            r = self._client.get(
                self.base_url + "/set_gpt_weights",
                params={"weights_path": weights_path},
            )
            return r.status_code == 200
        except httpx.HTTPError:
            return False

    def set_sovits_weights(self, weights_path: str) -> bool:
        try:
            r = self._client.get(
                self.base_url + "/set_sovits_weights",
                params={"weights_path": weights_path},
            )
            return r.status_code == 200
        except httpx.HTTPError:
            return False

    def close(self):
        self._client.close()
