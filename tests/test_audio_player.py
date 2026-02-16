"""Tests for dual-device audio player."""

import numpy as np
from unittest.mock import patch, MagicMock

from app.core.audio_player import AudioPlayer

_DEVICE_INFO = {"default_samplerate": 48000}


def test_play_array_default_device():
    """When no device names set, should play on default device."""
    player = AudioPlayer()
    data = np.zeros((4800,), dtype="float32")  # 0.1s of silence at 48kHz

    with patch("app.core.audio_player.find_device_by_name", return_value=-1), \
         patch("app.core.audio_player.sd.play") as mock_play, \
         patch("app.core.audio_player.sd.query_devices", return_value=_DEVICE_INFO):
        import threading
        done = threading.Event()

        def on_finished():
            done.set()

        player.play_array(data, 48000, on_finished)
        done.wait(timeout=2.0)

        mock_play.assert_called_once()
        call_args = mock_play.call_args
        assert call_args.kwargs["samplerate"] == 48000
        assert call_args.kwargs["device"] is None


def test_play_with_named_devices():
    """When device names are set and found, should play on both."""
    player = AudioPlayer(speaker_device_name="Speakers", virtual_device_name="CABLE")

    data = np.zeros((4800,), dtype="float32")

    with patch("app.core.audio_player.find_device_by_name") as mock_find, \
         patch("app.core.audio_player.sd.play") as mock_play, \
         patch("app.core.audio_player.sd.query_devices", return_value=_DEVICE_INFO):

        mock_find.side_effect = lambda name, is_input: {"Speakers": 3, "CABLE": 5}.get(name, -1)

        import threading
        done = threading.Event()
        player.play_array(data, 48000, lambda: done.set())
        done.wait(timeout=2.0)

        assert mock_play.call_count == 2
        devices_used = {call.kwargs["device"] for call in mock_play.call_args_list}
        assert devices_used == {3, 5}


def test_stop():
    player = AudioPlayer()
    with patch("app.core.audio_player.sd.stop") as mock_stop:
        player.stop()
        mock_stop.assert_called_once()
        assert not player.is_playing


def test_update_devices():
    player = AudioPlayer()
    player.update_devices("New Speaker", "New Cable")
    assert player.speaker_device_name == "New Speaker"
    assert player.virtual_device_name == "New Cable"


def test_play_wav_bytes():
    """Test playing from WAV bytes."""
    player = AudioPlayer()

    # Create minimal WAV in memory
    import io
    import soundfile as sf
    buf = io.BytesIO()
    data = np.zeros((4800,), dtype="float32")
    sf.write(buf, data, 48000, format="WAV")
    wav_bytes = buf.getvalue()

    with patch("app.core.audio_player.find_device_by_name", return_value=-1), \
         patch("app.core.audio_player.sd.play") as mock_play, \
         patch("app.core.audio_player.sd.query_devices", return_value=_DEVICE_INFO):
        import threading
        done = threading.Event()
        player.play_wav_bytes(wav_bytes, lambda: done.set())
        done.wait(timeout=2.0)
        mock_play.assert_called_once()
