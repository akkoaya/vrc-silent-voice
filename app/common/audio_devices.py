"""Audio device enumeration utilities."""

from typing import List, Tuple

import sounddevice as sd


def get_input_devices() -> List[Tuple[int, str]]:
    """Return list of (device_index, device_name) for input devices."""
    devices = sd.query_devices()
    result = []
    for i, dev in enumerate(devices):
        if dev["max_input_channels"] > 0:
            result.append((i, dev["name"]))
    return result


def get_output_devices() -> List[Tuple[int, str]]:
    """Return list of (device_index, device_name) for output devices."""
    devices = sd.query_devices()
    result = []
    for i, dev in enumerate(devices):
        if dev["max_output_channels"] > 0:
            result.append((i, dev["name"]))
    return result


def find_device_by_name(name: str, is_input: bool = True) -> int:
    """Find device index by name. Returns -1 if not found."""
    devices = get_input_devices() if is_input else get_output_devices()
    for idx, dev_name in devices:
        if name and name in dev_name:
            return idx
    return -1
