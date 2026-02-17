"""VRChat OSC Chatbox client using python-osc."""

from pythonosc import udp_client

MAX_CHATBOX_LENGTH = 144


class OSCClient:
    """Send text to VRChat's in-game chatbox via OSC."""

    def __init__(self, ip: str = "127.0.0.1", port: int = 9000):
        self._ip = ip
        self._port = port
        self._client = udp_client.SimpleUDPClient(ip, port)

    def send_chatbox(self, text: str, immediate: bool = True, sound: bool = True):
        """Send a message to VRChat chatbox.

        Parameters
        ----------
        text : str
            Message text (truncated to 144 chars).
        immediate : bool
            True to send immediately, False to populate keyboard.
        sound : bool
            Whether to play the VRChat notification sound.
        """
        text = text[:MAX_CHATBOX_LENGTH]
        self._client.send_message("/chatbox/input", [text, immediate, sound])

    def set_typing(self, is_typing: bool):
        """Toggle the VRChat typing indicator."""
        self._client.send_message("/chatbox/typing", [is_typing])

    def update_address(self, ip: str, port: int):
        """Recreate the UDP client with a new address."""
        self._ip = ip
        self._port = port
        self._client = udp_client.SimpleUDPClient(ip, port)
