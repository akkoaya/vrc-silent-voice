"""Configuration dataclasses with JSON persistence."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


@dataclass
class ASRConfig:
    enabled: bool = True
    model_dir: str = "models"
    language: str = "zh"  # zh, en, ja, ko, auto
    microphone_name: str = ""
    voice_mode: str = "push_to_talk"  # push_to_talk, toggle, open_mic
    hotkey: str = "Key.f2"
    sample_rate: int = 16000


@dataclass
class TTSConfig:
    api_url: str = "http://127.0.0.1:9880"
    ref_audio_path: str = ""
    prompt_text: str = ""
    prompt_lang: str = "zh"
    text_lang: str = "zh"
    top_k: int = 5
    top_p: float = 1.0
    temperature: float = 1.0
    speed_factor: float = 1.0
    text_split_method: str = "cut5"
    batch_size: int = 1
    seed: int = -1
    media_type: str = "wav"
    streaming_mode: bool = False
    repetition_penalty: float = 1.35
    sample_steps: int = 32
    super_sampling: bool = False
    speaker_device_name: str = ""
    virtual_device_name: str = ""


@dataclass
class AppConfig:
    asr: ASRConfig = field(default_factory=ASRConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)

    def save(self, path: Optional[Path] = None) -> None:
        path = path or CONFIG_PATH
        path.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Optional[Path] = None) -> AppConfig:
        path = path or CONFIG_PATH
        if not path.exists():
            cfg = cls()
            cfg.save(path)
            return cfg
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return cls(
                asr=ASRConfig(**data.get("asr", {})),
                tts=TTSConfig(**data.get("tts", {})),
            )
        except (json.JSONDecodeError, TypeError):
            return cls()
