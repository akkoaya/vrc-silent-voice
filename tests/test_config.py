"""Tests for configuration system."""

import json
import tempfile
from pathlib import Path

from app.config import AppConfig, ASRConfig, TTSConfig


def test_default_config():
    cfg = AppConfig()
    assert cfg.asr.language == "zh"
    assert cfg.tts.api_url == "http://127.0.0.1:9880"
    assert cfg.tts.top_k == 5
    assert cfg.asr.voice_mode == "push_to_talk"


def test_save_and_load(tmp_path):
    path = tmp_path / "config.json"
    cfg = AppConfig()
    cfg.asr.language = "en"
    cfg.tts.temperature = 0.8
    cfg.save(path)

    loaded = AppConfig.load(path)
    assert loaded.asr.language == "en"
    assert loaded.tts.temperature == 0.8


def test_load_missing_file(tmp_path):
    path = tmp_path / "nonexistent.json"
    cfg = AppConfig.load(path)
    assert cfg.asr.language == "zh"
    # Should have created the file
    assert path.exists()


def test_load_corrupt_file(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("not json", encoding="utf-8")
    cfg = AppConfig.load(path)
    assert cfg.asr.language == "zh"  # falls back to defaults


def test_roundtrip_preserves_all_fields(tmp_path):
    path = tmp_path / "config.json"
    cfg = AppConfig()
    cfg.tts.ref_audio_path = "/some/audio.wav"
    cfg.tts.speed_factor = 1.5
    cfg.asr.hotkey = "Key.f5"
    cfg.save(path)

    loaded = AppConfig.load(path)
    assert loaded.tts.ref_audio_path == "/some/audio.wav"
    assert loaded.tts.speed_factor == 1.5
    assert loaded.asr.hotkey == "Key.f5"
