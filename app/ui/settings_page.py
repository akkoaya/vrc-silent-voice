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
from app.i18n import t
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
        self.asr_group = SettingCardGroup(t("settings.asr_group"), self.scroll_widget)

        # ASR enable switch
        self.asr_card = _SettingCard(t("settings.asr_switch"), t("settings.asr_switch_desc"), self.asr_group)
        self.asr_enabled_switch = SwitchButton()
        self.asr_enabled_switch.setChecked(self.config.asr.enabled)
        self.asr_enabled_switch.checkedChanged.connect(self._on_asr_enabled_changed)
        self.asr_card.add_widget(self.asr_enabled_switch)
        self.asr_group.addSettingCard(self.asr_card)

        # Microphone selection (with refresh button)
        self.mic_device_card = AudioDeviceCard(
            t("settings.microphone"), t("settings.mic_desc"),
            is_input=True,
            current_device=self.config.asr.microphone_name,
            parent=self.asr_group,
        )
        self.mic_device_card.combo.currentTextChanged.connect(self._on_mic_changed)
        self.asr_group.addSettingCard(self.mic_device_card)

        # Voice mode
        self.voice_mode_card = _SettingCard(
            t("settings.voice_mode"),
            t("settings.voice_mode_desc"),
            self.asr_group,
        )
        self._voice_modes = ["push_to_talk", "toggle", "open_mic"]
        self.voice_mode_combo = ComboBox()
        for mode in self._voice_modes:
            self.voice_mode_combo.addItem(t(f"voice_mode.{mode}"), userData=mode)
        current_idx = self._voice_modes.index(self.config.asr.voice_mode)
        self.voice_mode_combo.setCurrentIndex(current_idx)
        self.voice_mode_combo.currentIndexChanged.connect(self._on_voice_mode_changed)
        self.voice_mode_card.add_widget(self.voice_mode_combo)
        self.asr_group.addSettingCard(self.voice_mode_card)

        # Hotkey (with capture button)
        self.hotkey_card = _SettingCard(t("settings.hotkey"), t("settings.hotkey_desc"), self.asr_group)
        self.hotkey_edit = HotkeyEdit(current_hotkey=self.config.asr.hotkey)
        self.hotkey_edit.hotkey_changed.connect(self._on_hotkey_changed)
        self.hotkey_card.add_widget(self.hotkey_edit)
        self.asr_group.addSettingCard(self.hotkey_card)

        # Language
        self.lang_card = _SettingCard(t("settings.asr_lang"), t("settings.asr_lang_desc"), self.asr_group)
        self.lang_combo = ComboBox()
        self.lang_combo.addItems(["zh", "en", "ja", "ko", "auto"])
        self.lang_combo.setCurrentText(self.config.asr.language)
        self.lang_combo.currentTextChanged.connect(self._on_lang_changed)
        self.lang_card.add_widget(self.lang_combo)
        self.asr_group.addSettingCard(self.lang_card)

        self.expand_layout.addWidget(self.asr_group)

    def _init_tts_group(self):
        self.tts_group = SettingCardGroup(t("settings.tts_group"), self.scroll_widget)

        # API URL
        self.api_card = _SettingCard(t("settings.api_url"), t("settings.api_url_desc"), self.tts_group)
        self.api_url_edit = LineEdit()
        self.api_url_edit.setMinimumWidth(260)
        self.api_url_edit.setText(self.config.tts.api_url)
        self.api_url_edit.textChanged.connect(self._on_api_url_changed)
        self.api_card.add_widget(self.api_url_edit)
        self.tts_group.addSettingCard(self.api_card)

        # Reference audio
        self.ref_card = _SettingCard(t("settings.ref_audio"), t("settings.ref_audio_desc"), self.tts_group)
        self.ref_path_edit = LineEdit()
        self.ref_path_edit.setMinimumWidth(200)
        self.ref_path_edit.setText(self.config.tts.ref_audio_path)
        self.ref_path_edit.textChanged.connect(self._on_ref_path_changed)
        self.ref_browse_btn = PushButton(t("settings.browse"))
        self.ref_browse_btn.clicked.connect(self._browse_ref_audio)
        self.ref_card.add_widget(self.ref_path_edit)
        self.ref_card.add_widget(self.ref_browse_btn)
        self.tts_group.addSettingCard(self.ref_card)

        # Prompt text
        self.prompt_card = _SettingCard(t("settings.prompt_text"), t("settings.prompt_text_desc"), self.tts_group)
        self.prompt_text_edit = LineEdit()
        self.prompt_text_edit.setMinimumWidth(260)
        self.prompt_text_edit.setText(self.config.tts.prompt_text)
        self.prompt_text_edit.textChanged.connect(self._on_prompt_text_changed)
        self.prompt_card.add_widget(self.prompt_text_edit)
        self.tts_group.addSettingCard(self.prompt_card)

        # Prompt language
        self.prompt_lang_card = _SettingCard(t("settings.prompt_lang"), t("settings.prompt_lang_desc"), self.tts_group)
        self.prompt_lang_combo = ComboBox()
        self.prompt_lang_combo.addItems(["zh", "en", "ja", "ko", "yue", "auto"])
        self.prompt_lang_combo.setCurrentText(self.config.tts.prompt_lang)
        self.prompt_lang_combo.currentTextChanged.connect(self._on_prompt_lang_changed)
        self.prompt_lang_card.add_widget(self.prompt_lang_combo)
        self.tts_group.addSettingCard(self.prompt_lang_card)

        # Speaker device (physical speaker for self-monitoring, with refresh)
        self.speaker_device_card = AudioDeviceCard(
            t("settings.speaker_device"), t("settings.speaker_desc"),
            is_input=False,
            allow_none=True,
            current_device=self.config.tts.speaker_device_name,
            parent=self.tts_group,
        )
        self.speaker_device_card.combo.currentTextChanged.connect(self._on_speaker_changed)
        self.tts_group.addSettingCard(self.speaker_device_card)

        # Virtual cable device (for VRChat, with refresh)
        self.virtual_device_card = AudioDeviceCard(
            t("settings.virtual_device"), t("settings.virtual_desc"),
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

    def _on_voice_mode_changed(self, index):
        self.config.asr.voice_mode = self._voice_modes[index]
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
        self.config.tts.speaker_device_name = "" if text == t("device.none") else text
        signal_bus.config_changed.emit()

    def _on_virtual_changed(self, text):
        self.config.tts.virtual_device_name = text
        signal_bus.config_changed.emit()

    def _browse_ref_audio(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("settings.select_ref_audio"), "", "Audio Files (*.wav *.mp3 *.flac);;All Files (*)"
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
