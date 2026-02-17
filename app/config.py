"""Configuration dataclasses with JSON persistence."""

from __future__ import annotations

import sys
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


def _get_base_dir() -> Path:
    """Return the base directory for bundled data (models, icons, etc.)."""
    if getattr(sys, "frozen", False):
        # PyInstaller onedir: data files are in sys._MEIPASS
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def _get_app_dir() -> Path:
    """Return the directory for user-writable files (config.json, etc.)."""
    if getattr(sys, "frozen", False):
        # Next to the executable so users can find/edit it
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()
APP_DIR = _get_app_dir()
CONFIG_PATH = APP_DIR / "config.json"


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
    enabled: bool = True
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
class OSCConfig:
    enabled: bool = False
    ip: str = "127.0.0.1"
    port: int = 9000
    notification_sound: bool = True


@dataclass
class AppConfig:
    language: str = "en"
    asr: ASRConfig = field(default_factory=ASRConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    osc: OSCConfig = field(default_factory=OSCConfig)

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
                language=data.get("language", "en"),
                asr=ASRConfig(**data.get("asr", {})),
                tts=TTSConfig(**data.get("tts", {})),
                osc=OSCConfig(**data.get("osc", {})),
            )
        except (json.JSONDecodeError, TypeError):
            return cls()
