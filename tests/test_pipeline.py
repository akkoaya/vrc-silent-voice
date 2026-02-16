"""Tests for pipeline orchestrator."""

from unittest.mock import patch, MagicMock, PropertyMock
import pytest

from app.config import AppConfig
from app.core.pipeline import Pipeline, TTSWorker


@pytest.fixture
def config():
    cfg = AppConfig()
    cfg.asr.enabled = False  # Disable ASR for basic tests
    cfg.tts.api_url = "http://127.0.0.1:9880"
    cfg.tts.ref_audio_path = "/test/ref.wav"
    return cfg


def test_pipeline_creation(config):
    with patch("app.core.pipeline.TTSClient") as mock_tts:
        p = Pipeline(config)
        assert p.tts_client is not None
        assert p.audio_player is not None
        assert p.asr_engine is not None
        p.shutdown()


def test_synthesize_when_busy(config):
    with patch("app.core.pipeline.TTSClient"):
        p = Pipeline(config)
        p._busy = True

        errors = []
        from app.signals import signal_bus
        signal_bus.tts_error.connect(lambda e: errors.append(e))

        p.synthesize("test")
        assert len(errors) == 1
        assert "稍候" in errors[0]

        signal_bus.tts_error.disconnect()
        p.shutdown()


def test_synthesize_empty_text(config):
    with patch("app.core.pipeline.TTSClient") as mock_tts_cls:
        p = Pipeline(config)
        p.synthesize("")
        p.synthesize("   ")
        # Should not create any TTSWorker
        assert p._tts_worker is None
        p.shutdown()


def test_update_audio_devices(config):
    with patch("app.core.pipeline.TTSClient"):
        p = Pipeline(config)
        config.tts.speaker_device_name = "New Speaker"
        config.tts.virtual_device_name = "New Cable"
        p.update_audio_devices()
        assert p.audio_player.speaker_device_name == "New Speaker"
        assert p.audio_player.virtual_device_name == "New Cable"
        p.shutdown()


def test_check_tts_connection(config):
    with patch("app.core.pipeline.TTSClient") as mock_cls:
        instance = mock_cls.return_value
        instance.check_connection.return_value = True
        p = Pipeline(config)
        assert p.check_tts_connection() is True
        p.shutdown()
