"""Tests for TTS client."""

from unittest.mock import patch, MagicMock

import httpx
import pytest

from app.config import TTSConfig
from app.core.tts_client import TTSClient


@pytest.fixture
def tts_config():
    return TTSConfig(
        api_url="http://127.0.0.1:9880",
        ref_audio_path="/test/ref.wav",
        prompt_text="hello",
        prompt_lang="zh",
        text_lang="zh",
    )


@pytest.fixture
def client(tts_config):
    c = TTSClient(tts_config)
    yield c
    c.close()


def test_base_url(client):
    assert client.base_url == "http://127.0.0.1:9880"


def test_base_url_strips_trailing_slash():
    cfg = TTSConfig(api_url="http://localhost:9880/")
    c = TTSClient(cfg)
    assert c.base_url == "http://localhost:9880"
    c.close()


def test_synthesize_builds_correct_payload(client):
    fake_wav = b"RIFF\x00\x00\x00\x00WAVEfmt "
    mock_response = MagicMock()
    mock_response.content = fake_wav
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    with patch.object(client._client, "post", return_value=mock_response) as mock_post:
        result = client.synthesize("你好世界")

        assert result == fake_wav
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"]
        assert payload["text"] == "你好世界"
        assert payload["text_lang"] == "zh"
        assert payload["ref_audio_path"] == "/test/ref.wav"
        assert payload["top_k"] == 5


def test_synthesize_override_params(client):
    mock_response = MagicMock()
    mock_response.content = b"audio"
    mock_response.raise_for_status = MagicMock()

    with patch.object(client._client, "post", return_value=mock_response) as mock_post:
        client.synthesize("test", top_k=10, temperature=0.5, speed_factor=1.5)

        payload = mock_post.call_args.kwargs["json"]
        assert payload["top_k"] == 10
        assert payload["temperature"] == 0.5
        assert payload["speed_factor"] == 1.5


def test_check_connection_success(client):
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch.object(client._client, "get", return_value=mock_response):
        assert client.check_connection() is True


def test_check_connection_failure(client):
    with patch.object(client._client, "get", side_effect=httpx.ConnectError("refused")):
        assert client.check_connection() is False


def test_set_gpt_weights(client):
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch.object(client._client, "get", return_value=mock_response) as mock_get:
        result = client.set_gpt_weights("/path/to/weights.ckpt")
        assert result is True
        mock_get.assert_called_once_with(
            "http://127.0.0.1:9880/set_gpt_weights",
            params={"weights_path": "/path/to/weights.ckpt"},
        )
