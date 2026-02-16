"""Settings page - ASR and TTS configuration."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFileDialog,
)
from PyQt6.QtCore import Qt

from qfluentwidgets import (
    ScrollArea, ExpandLayout, SettingCardGroup,
    FluentIcon, LineEdit, ComboBox, PushButton, SwitchButton,
    BodyLabel, CardWidget, StrongBodyLabel,
)

from app.config import AppConfig
from app.common.audio_devices import get_input_devices, get_output_devices
from app.signals import signal_bus
from app.ui.components.hotkey_edit import HotkeyEdit
from app.ui.components.audio_device_card import AudioDeviceCard


class SettingsPage(ScrollArea):
    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setObjectName("settingsPage")

        self.scroll_widget = QWidget()
        self.expand_layout = ExpandLayout(self.scroll_widget)

        self._init_asr_group()
        self._init_tts_group()

        self.expand_layout.setSpacing(20)
        self.expand_layout.setContentsMargins(36, 20, 36, 20)

        self.setWidget(self.scroll_widget)
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_widget.setStyleSheet("background: transparent;")

    def _init_asr_group(self):
        self.asr_group = SettingCardGroup("语音识别 (ASR)", self.scroll_widget)

        # ASR enable switch
        self.asr_card = _SettingCard("语音识别开关", "开启后可通过麦克风识别语音并自动转文字", self.asr_group)
        self.asr_enabled_switch = SwitchButton()
        self.asr_enabled_switch.setChecked(self.config.asr.enabled)
        self.asr_enabled_switch.checkedChanged.connect(self._on_asr_enabled_changed)
        self.asr_card.add_widget(self.asr_enabled_switch)
        self.asr_group.addSettingCard(self.asr_card)

        # Microphone selection (with refresh button)
        self.mic_device_card = AudioDeviceCard(
            "麦克风", "选择用于语音识别的输入设备",
            is_input=True,
            current_device=self.config.asr.microphone_name,
            parent=self.asr_group,
        )
        self.mic_device_card.combo.currentTextChanged.connect(self._on_mic_changed)
        self.asr_group.addSettingCard(self.mic_device_card)

        # Voice mode
        self.voice_mode_card = _SettingCard(
            "语音模式",
            "push_to_talk=按住说话, toggle=按键切换, open_mic=持续开启",
            self.asr_group,
        )
        self.voice_mode_combo = ComboBox()
        self.voice_mode_combo.addItems(["push_to_talk", "toggle", "open_mic"])
        self.voice_mode_combo.setCurrentText(self.config.asr.voice_mode)
        self.voice_mode_combo.currentTextChanged.connect(self._on_voice_mode_changed)
        self.voice_mode_card.add_widget(self.voice_mode_combo)
        self.asr_group.addSettingCard(self.voice_mode_card)

        # Hotkey (with capture button)
        self.hotkey_card = _SettingCard("热键", "语音识别触发按键（点击捕获按键后按下想要的按键）", self.asr_group)
        self.hotkey_edit = HotkeyEdit(current_hotkey=self.config.asr.hotkey)
        self.hotkey_edit.hotkey_changed.connect(self._on_hotkey_changed)
        self.hotkey_card.add_widget(self.hotkey_edit)
        self.asr_group.addSettingCard(self.hotkey_card)

        # Language
        self.lang_card = _SettingCard("识别语言", "语音识别模型语言", self.asr_group)
        self.lang_combo = ComboBox()
        self.lang_combo.addItems(["zh", "en", "ja", "ko", "auto"])
        self.lang_combo.setCurrentText(self.config.asr.language)
        self.lang_combo.currentTextChanged.connect(self._on_lang_changed)
        self.lang_card.add_widget(self.lang_combo)
        self.asr_group.addSettingCard(self.lang_card)

        self.expand_layout.addWidget(self.asr_group)

    def _init_tts_group(self):
        self.tts_group = SettingCardGroup("语音合成 (TTS)", self.scroll_widget)

        # API URL
        self.api_card = _SettingCard("API 地址", "GPT-SoVITS API 服务地址", self.tts_group)
        self.api_url_edit = LineEdit()
        self.api_url_edit.setMinimumWidth(260)
        self.api_url_edit.setText(self.config.tts.api_url)
        self.api_url_edit.textChanged.connect(self._on_api_url_changed)
        self.api_card.add_widget(self.api_url_edit)
        self.tts_group.addSettingCard(self.api_card)

        # Reference audio
        self.ref_card = _SettingCard("参考音频", "TTS 参考音频文件路径", self.tts_group)
        self.ref_path_edit = LineEdit()
        self.ref_path_edit.setMinimumWidth(200)
        self.ref_path_edit.setText(self.config.tts.ref_audio_path)
        self.ref_path_edit.textChanged.connect(self._on_ref_path_changed)
        self.ref_browse_btn = PushButton("浏览")
        self.ref_browse_btn.clicked.connect(self._browse_ref_audio)
        self.ref_card.add_widget(self.ref_path_edit)
        self.ref_card.add_widget(self.ref_browse_btn)
        self.tts_group.addSettingCard(self.ref_card)

        # Prompt text
        self.prompt_card = _SettingCard("提示文本", "参考音频对应的文本内容", self.tts_group)
        self.prompt_text_edit = LineEdit()
        self.prompt_text_edit.setMinimumWidth(260)
        self.prompt_text_edit.setText(self.config.tts.prompt_text)
        self.prompt_text_edit.textChanged.connect(self._on_prompt_text_changed)
        self.prompt_card.add_widget(self.prompt_text_edit)
        self.tts_group.addSettingCard(self.prompt_card)

        # Prompt language
        self.prompt_lang_card = _SettingCard("提示语言", "参考音频的语言", self.tts_group)
        self.prompt_lang_combo = ComboBox()
        self.prompt_lang_combo.addItems(["zh", "en", "ja", "ko", "yue", "auto"])
        self.prompt_lang_combo.setCurrentText(self.config.tts.prompt_lang)
        self.prompt_lang_combo.currentTextChanged.connect(self._on_prompt_lang_changed)
        self.prompt_lang_card.add_widget(self.prompt_lang_combo)
        self.tts_group.addSettingCard(self.prompt_lang_card)

        # Speaker device (physical speaker for self-monitoring, with refresh)
        self.speaker_device_card = AudioDeviceCard(
            "物理扬声器", "用于自己监听合成语音的输出设备",
            is_input=False,
            current_device=self.config.tts.speaker_device_name,
            parent=self.tts_group,
        )
        self.speaker_device_card.combo.currentTextChanged.connect(self._on_speaker_changed)
        self.tts_group.addSettingCard(self.speaker_device_card)

        # Virtual cable device (for VRChat, with refresh)
        self.virtual_device_card = AudioDeviceCard(
            "虚拟声卡", "用于VRChat游戏内播放的虚拟声卡设备 (如 CABLE Input)",
            is_input=False,
            current_device=self.config.tts.virtual_device_name,
            parent=self.tts_group,
        )
        self.virtual_device_card.combo.currentTextChanged.connect(self._on_virtual_changed)
        self.tts_group.addSettingCard(self.virtual_device_card)

        self.expand_layout.addWidget(self.tts_group)

    # --- Event handlers ---

    def _on_asr_enabled_changed(self, checked):
        self.config.asr.enabled = checked
        signal_bus.config_changed.emit()

    def _on_mic_changed(self, text):
        self.config.asr.microphone_name = text
        signal_bus.config_changed.emit()

    def _on_voice_mode_changed(self, text):
        self.config.asr.voice_mode = text
        signal_bus.config_changed.emit()

    def _on_hotkey_changed(self, key_str):
        self.config.asr.hotkey = key_str
        signal_bus.config_changed.emit()

    def _on_lang_changed(self, text):
        self.config.asr.language = text
        signal_bus.config_changed.emit()

    def _on_api_url_changed(self, text):
        self.config.tts.api_url = text
        signal_bus.config_changed.emit()

    def _on_ref_path_changed(self, text):
        self.config.tts.ref_audio_path = text
        signal_bus.config_changed.emit()

    def _on_prompt_text_changed(self, text):
        self.config.tts.prompt_text = text
        signal_bus.config_changed.emit()

    def _on_prompt_lang_changed(self, text):
        self.config.tts.prompt_lang = text
        signal_bus.config_changed.emit()

    def _on_speaker_changed(self, text):
        self.config.tts.speaker_device_name = text
        signal_bus.config_changed.emit()

    def _on_virtual_changed(self, text):
        self.config.tts.virtual_device_name = text
        signal_bus.config_changed.emit()

    def _browse_ref_audio(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择参考音频", "", "Audio Files (*.wav *.mp3 *.flac);;All Files (*)"
        )
        if path:
            self.ref_path_edit.setText(path)

    def save_config(self):
        self.config.save()


class _SettingCard(CardWidget):
    """A simple setting card with a label, description, and right-side widgets."""

    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)

        self.h_layout = QHBoxLayout(self)
        self.h_layout.setContentsMargins(20, 0, 20, 0)

        left = QVBoxLayout()
        left.setSpacing(2)
        self.title_label = StrongBodyLabel(title)
        self.desc_label = BodyLabel(description)
        self.desc_label.setStyleSheet("color: gray; font-size: 12px;")
        left.addWidget(self.title_label)
        left.addWidget(self.desc_label)

        self.h_layout.addLayout(left)
        self.h_layout.addStretch()

    def add_widget(self, widget):
        self.h_layout.addWidget(widget)
