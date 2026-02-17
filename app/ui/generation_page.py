"""Generation page - text input, ASR control, TTS parameters, and generation."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QSizePolicy,
)
from PyQt6.QtCore import Qt

from qfluentwidgets import (
    ScrollArea, TextEdit, PushButton, ComboBox, SpinBox, DoubleSpinBox,
    StrongBodyLabel, BodyLabel, CardWidget, ProgressRing, FluentIcon,
    SwitchButton, ExpandLayout, SettingCardGroup,
)

from app.config import AppConfig
from app.i18n import t
from app.ui.components.asr_control_card import ASRControlCard


class GenerationPage(ScrollArea):
    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setObjectName("generationPage")

        self.scroll_widget = QWidget()
        self.v_layout = QVBoxLayout(self.scroll_widget)
        self.v_layout.setContentsMargins(36, 20, 36, 20)
        self.v_layout.setSpacing(16)

        self._init_asr_section()
        self._init_text_section()
        self._init_params_section()
        self._init_action_section()

        self.v_layout.addStretch()

        self.setWidget(self.scroll_widget)
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_widget.setStyleSheet("background: transparent;")

    def _init_asr_section(self):
        """ASR status card."""
        self.asr_card = ASRControlCard()
        self.v_layout.addWidget(self.asr_card)

    def _init_text_section(self):
        """Text input area."""
        label = StrongBodyLabel(t("gen.input_text"))
        self.v_layout.addWidget(label)

        self.text_edit = TextEdit()
        self.text_edit.setPlaceholderText(t("gen.placeholder"))
        self.text_edit.setMinimumHeight(100)
        self.text_edit.setMaximumHeight(200)
        self.text_edit.setStyleSheet("TextEdit { background: white; color: black; }")
        self.v_layout.addWidget(self.text_edit)

    def _init_params_section(self):
        """TTS parameter controls."""
        label = StrongBodyLabel(t("gen.params"))
        self.v_layout.addWidget(label)

        params_card = CardWidget()
        grid = QGridLayout(params_card)
        grid.setContentsMargins(20, 16, 20, 16)
        grid.setSpacing(12)
        row = 0

        # Text language
        grid.addWidget(BodyLabel(t("gen.text_lang")), row, 0)
        self.text_lang_combo = ComboBox()
        self.text_lang_combo.addItems(["zh", "en", "ja", "ko", "yue", "auto"])
        self.text_lang_combo.setCurrentText(self.config.tts.text_lang)
        self.text_lang_combo.setMinimumWidth(120)
        grid.addWidget(self.text_lang_combo, row, 1)

        grid.addWidget(BodyLabel(t("gen.split_method")), row, 2)
        self.split_combo = ComboBox()
        self._split_methods = ["cut0", "cut1", "cut2", "cut3", "cut4", "cut5"]
        for method in self._split_methods:
            self.split_combo.addItem(t(f"split.{method}"), userData=method)
        current_idx = self._split_methods.index(self.config.tts.text_split_method)
        self.split_combo.setCurrentIndex(current_idx)
        self.split_combo.setMinimumWidth(160)
        grid.addWidget(self.split_combo, row, 3)
        row += 1

        # Top K / Top P
        grid.addWidget(BodyLabel("Top K"), row, 0)
        self.top_k_spin = SpinBox()
        self.top_k_spin.setRange(1, 100)
        self.top_k_spin.setValue(self.config.tts.top_k)
        grid.addWidget(self.top_k_spin, row, 1)

        grid.addWidget(BodyLabel("Top P"), row, 2)
        self.top_p_spin = DoubleSpinBox()
        self.top_p_spin.setRange(0.0, 1.0)
        self.top_p_spin.setSingleStep(0.05)
        self.top_p_spin.setValue(self.config.tts.top_p)
        grid.addWidget(self.top_p_spin, row, 3)
        row += 1

        # Temperature / Speed
        grid.addWidget(BodyLabel("Temperature"), row, 0)
        self.temp_spin = DoubleSpinBox()
        self.temp_spin.setRange(0.01, 2.0)
        self.temp_spin.setSingleStep(0.05)
        self.temp_spin.setValue(self.config.tts.temperature)
        grid.addWidget(self.temp_spin, row, 1)

        grid.addWidget(BodyLabel(t("gen.speed")), row, 2)
        self.speed_spin = DoubleSpinBox()
        self.speed_spin.setRange(0.25, 4.0)
        self.speed_spin.setSingleStep(0.1)
        self.speed_spin.setValue(self.config.tts.speed_factor)
        grid.addWidget(self.speed_spin, row, 3)
        row += 1

        # Batch size / Seed
        grid.addWidget(BodyLabel("Batch Size"), row, 0)
        self.batch_spin = SpinBox()
        self.batch_spin.setRange(1, 64)
        self.batch_spin.setValue(self.config.tts.batch_size)
        grid.addWidget(self.batch_spin, row, 1)

        grid.addWidget(BodyLabel("Seed"), row, 2)
        self.seed_spin = SpinBox()
        self.seed_spin.setRange(-1, 999999)
        self.seed_spin.setValue(self.config.tts.seed)
        grid.addWidget(self.seed_spin, row, 3)
        row += 1

        # Repetition penalty / Sample steps
        grid.addWidget(BodyLabel(t("gen.rep_penalty")), row, 0)
        self.rep_penalty_spin = DoubleSpinBox()
        self.rep_penalty_spin.setRange(0.5, 3.0)
        self.rep_penalty_spin.setSingleStep(0.05)
        self.rep_penalty_spin.setValue(self.config.tts.repetition_penalty)
        grid.addWidget(self.rep_penalty_spin, row, 1)

        grid.addWidget(BodyLabel(t("gen.sample_steps")), row, 2)
        self.sample_steps_spin = SpinBox()
        self.sample_steps_spin.setRange(1, 128)
        self.sample_steps_spin.setValue(self.config.tts.sample_steps)
        grid.addWidget(self.sample_steps_spin, row, 3)
        row += 1

        # Super sampling switch
        grid.addWidget(BodyLabel(t("gen.super_sampling")), row, 0)
        self.super_sampling_switch = SwitchButton()
        self.super_sampling_switch.setChecked(self.config.tts.super_sampling)
        grid.addWidget(self.super_sampling_switch, row, 1)

        self.v_layout.addWidget(params_card)

    def _init_action_section(self):
        """Generate button and status."""
        action_row = QHBoxLayout()
        action_row.setSpacing(12)

        self.generate_btn = PushButton(FluentIcon.SEND, t("gen.generate"))
        self.generate_btn.setFixedHeight(40)
        self.generate_btn.setMinimumWidth(160)
        action_row.addWidget(self.generate_btn)

        self.stop_btn = PushButton(FluentIcon.CLOSE, t("gen.stop"))
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setEnabled(False)
        action_row.addWidget(self.stop_btn)

        action_row.addStretch()

        self.status_ring = ProgressRing()
        self.status_ring.setFixedSize(32, 32)
        self.status_ring.setRange(0, 0)
        self.status_ring.hide()
        action_row.addWidget(self.status_ring)

        self.status_label = BodyLabel("")
        action_row.addWidget(self.status_label)

        self.v_layout.addLayout(action_row)

    def get_tts_params(self) -> dict:
        """Collect current TTS parameter values from UI controls."""
        return {
            "text_lang": self.text_lang_combo.currentText(),
            "top_k": self.top_k_spin.value(),
            "top_p": self.top_p_spin.value(),
            "temperature": self.temp_spin.value(),
            "speed_factor": self.speed_spin.value(),
            "text_split_method": self._split_methods[self.split_combo.currentIndex()],
            "batch_size": self.batch_spin.value(),
            "seed": self.seed_spin.value(),
            "repetition_penalty": self.rep_penalty_spin.value(),
            "sample_steps": self.sample_steps_spin.value(),
            "super_sampling": self.super_sampling_switch.isChecked(),
        }

    def save_config(self):
        """Write current UI parameter values back to config object."""
        tts = self.config.tts
        tts.text_lang = self.text_lang_combo.currentText()
        tts.text_split_method = self._split_methods[self.split_combo.currentIndex()]
        tts.top_k = self.top_k_spin.value()
        tts.top_p = self.top_p_spin.value()
        tts.temperature = self.temp_spin.value()
        tts.speed_factor = self.speed_spin.value()
        tts.batch_size = self.batch_spin.value()
        tts.seed = self.seed_spin.value()
        tts.repetition_penalty = self.rep_penalty_spin.value()
        tts.sample_steps = self.sample_steps_spin.value()
        tts.super_sampling = self.super_sampling_switch.isChecked()

    def set_busy(self, busy: bool):
        """Toggle busy state UI."""
        self.generate_btn.setEnabled(not busy)
        self.stop_btn.setEnabled(busy)
        if busy:
            self.status_ring.show()
            self.status_label.setText(t("gen.synthesizing"))
        else:
            self.status_ring.hide()
            self.status_label.setText("")
