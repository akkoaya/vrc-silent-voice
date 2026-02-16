"""Global hotkey manager using pynput for ASR voice control."""

from __future__ import annotations

import threading
from typing import Callable, Optional

from pynput import keyboard


class HotkeyManager:
    """Manages global hotkey for ASR voice control.

    Supports three modes:
    - push_to_talk: Record while key is held down
    - toggle: Press to start/stop recording
    - open_mic: Always recording (hotkey ignored)
    """

    def __init__(
        self,
        hotkey: str = "Key.f2",
        mode: str = "push_to_talk",
        on_start: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
    ):
        self.mode = mode
        self.on_start = on_start
        self.on_stop = on_stop
        self._hotkey_str = hotkey
        self._target_key = self._parse_key(hotkey)
        self._listener: Optional[keyboard.Listener] = None
        self._is_active = False  # Whether recording is active (for toggle mode)
        self._key_held = False   # Whether key is currently held down

    @staticmethod
    def _parse_key(key_str: str):
        """Parse a key string like 'Key.f2' or 'a' into a pynput key."""
        key_str = key_str.strip()
        if key_str.startswith("Key."):
            attr = key_str[4:]
            return getattr(keyboard.Key, attr, None)
        if len(key_str) == 1:
            return keyboard.KeyCode.from_char(key_str)
        # Try as vk code
        try:
            return keyboard.KeyCode.from_vk(int(key_str))
        except (ValueError, TypeError):
            return None

    def _keys_match(self, key) -> bool:
        """Check if pressed key matches the target hotkey."""
        if self._target_key is None:
            return False
        if isinstance(self._target_key, keyboard.Key):
            return key == self._target_key
        if isinstance(self._target_key, keyboard.KeyCode):
            if isinstance(key, keyboard.KeyCode):
                return key.char == self._target_key.char if self._target_key.char else key.vk == self._target_key.vk
        return False

    def update_hotkey(self, hotkey: str):
        self._hotkey_str = hotkey
        self._target_key = self._parse_key(hotkey)

    def update_mode(self, mode: str):
        if mode == "open_mic" and not self._is_active:
            self._is_active = True
            if self.on_start:
                self.on_start()
        elif self.mode == "open_mic" and mode != "open_mic" and self._is_active:
            self._is_active = False
            if self.on_stop:
                self.on_stop()
        self.mode = mode

    def _on_press(self, key):
        if self.mode == "open_mic":
            return

        if not self._keys_match(key):
            return

        if self.mode == "push_to_talk":
            if not self._key_held:
                self._key_held = True
                self._is_active = True
                if self.on_start:
                    self.on_start()

        elif self.mode == "toggle":
            if not self._key_held:
                self._key_held = True
                self._is_active = not self._is_active
                if self._is_active:
                    if self.on_start:
                        self.on_start()
                else:
                    if self.on_stop:
                        self.on_stop()

    def _on_release(self, key):
        if self.mode == "open_mic":
            return

        if not self._keys_match(key):
            return

        self._key_held = False

        if self.mode == "push_to_talk":
            if self._is_active:
                self._is_active = False
                if self.on_stop:
                    self.on_stop()

    def start(self):
        """Start listening for hotkeys."""
        if self._listener is not None:
            return

        if self.mode == "open_mic":
            self._is_active = True
            if self.on_start:
                self.on_start()

        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self):
        """Stop listening and clean up."""
        if self._is_active and self.on_stop:
            self.on_stop()
        self._is_active = False
        self._key_held = False
        if self._listener:
            self._listener.stop()
            self._listener = None

    @property
    def is_running(self) -> bool:
        return self._listener is not None and self._listener.is_alive()
