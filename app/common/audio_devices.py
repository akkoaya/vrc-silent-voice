"""Audio device enumeration utilities."""

import platform
from typing import List, Tuple

import sounddevice as sd


def _get_preferred_host_api_devices() -> set:
    """Return device indices for the preferred host API on this platform.

    Windows: WASAPI (lowest latency, best compatibility)
    Linux/macOS: return empty set (accept all devices)
    """
    if platform.system() != "Windows":
        return set()
    hostapis = sd.query_hostapis()
    for api in hostapis:
        if "WASAPI" in api["name"]:
            return set(api["devices"])
    return set()


def _deduplicate(devices: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
    """Remove duplicate device names, keeping the first occurrence."""
    seen = set()
    result = []
    for idx, name in devices:
        if name not in seen:
            seen.add(name)
            result.append((idx, name))
    return result


def get_input_devices() -> List[Tuple[int, str]]:
    """Return list of (device_index, device_name) for input devices."""
    devices = sd.query_devices()
    preferred = _get_preferred_host_api_devices()
    result = []
    for i, dev in enumerate(devices):
        if dev["max_input_channels"] > 0:
            if not preferred or i in preferred:
                result.append((i, dev["name"]))
    return _deduplicate(result)


def get_output_devices() -> List[Tuple[int, str]]:
    """Return list of (device_index, device_name) for output devices."""
    devices = sd.query_devices()
    preferred = _get_preferred_host_api_devices()
    result = []
    for i, dev in enumerate(devices):
        if dev["max_output_channels"] > 0:
            if not preferred or i in preferred:
                result.append((i, dev["name"]))
    return _deduplicate(result)


def find_device_by_name(name: str, is_input: bool = True) -> int:
    """Find device index by name. Returns -1 if not found."""
    devices = get_input_devices() if is_input else get_output_devices()
    for idx, dev_name in devices:
        if name and name in dev_name:
            return idx
    return -1
