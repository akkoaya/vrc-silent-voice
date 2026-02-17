"""Lightweight dict-based i18n module."""

from __future__ import annotations

LANGUAGES = {"en": "English", "ja": "日本語", "zh": "中文"}

_current_language = "en"

_translations: dict[str, dict[str, str]] = {
    # --- Navigation ---
    "nav.home": {"en": "Home", "ja": "ホーム", "zh": "主页"},
    "nav.settings": {"en": "Settings", "ja": "設定", "zh": "设置"},
    "nav.about": {"en": "About", "ja": "について", "zh": "关于"},

    # --- Generation page ---
    "gen.input_text": {"en": "Input Text", "ja": "入力テキスト", "zh": "输入文本"},
    "gen.placeholder": {
        "en": "Enter text to synthesize, or use speech recognition to auto-fill...",
        "ja": "合成するテキストを入力、または音声認識で自動入力...",
        "zh": "输入要合成的文本，或通过语音识别自动填入...",
    },
    "gen.params": {"en": "Synthesis Parameters", "ja": "合成パラメータ", "zh": "合成参数"},
    "gen.text_lang": {"en": "Text Language", "ja": "テキスト言語", "zh": "文本语言"},
    "gen.split_method": {"en": "Text Split Method", "ja": "テキスト分割方式", "zh": "文本切分方式"},
    "gen.speed": {"en": "Speed", "ja": "速度", "zh": "语速"},
    "gen.rep_penalty": {"en": "Repetition Penalty", "ja": "繰り返しペナルティ", "zh": "重复惩罚"},
    "gen.sample_steps": {"en": "Sample Steps", "ja": "サンプルステップ", "zh": "采样步数"},
    "gen.super_sampling": {"en": "Super Sampling", "ja": "スーパーサンプリング", "zh": "超采样"},
    "gen.generate": {"en": "Generate", "ja": "生成", "zh": "生成语音"},
    "gen.stop": {"en": "Stop", "ja": "停止", "zh": "停止"},
    "gen.synthesizing": {"en": "Synthesizing...", "ja": "合成中...", "zh": "正在合成..."},

    # --- ASR control card ---
    "asr.title": {"en": "Speech Recognition", "ja": "音声認識", "zh": "语音识别"},
    "asr.standby": {"en": "Standby", "ja": "待機", "zh": "待机"},
    "asr.recording": {"en": "Recording", "ja": "録音中", "zh": "录音中"},
    "asr.waiting": {"en": "Waiting for voice input...", "ja": "音声入力を待機中...", "zh": "等待语音输入..."},

    # --- Settings page ---
    "settings.asr_group": {"en": "Speech Recognition (ASR)", "ja": "音声認識 (ASR)", "zh": "语音识别 (ASR)"},
    "settings.asr_switch": {"en": "Speech Recognition", "ja": "音声認識スイッチ", "zh": "语音识别开关"},
    "settings.asr_switch_desc": {
        "en": "Enable to recognize speech via microphone and convert to text",
        "ja": "マイクで音声を認識しテキストに変換",
        "zh": "开启后可通过麦克风识别语音并自动转文字",
    },
    "settings.microphone": {"en": "Microphone", "ja": "マイク", "zh": "麦克风"},
    "settings.mic_desc": {
        "en": "Select input device for speech recognition",
        "ja": "音声認識に使用する入力デバイスを選択",
        "zh": "选择用于语音识别的输入设备",
    },
    "settings.voice_mode": {"en": "Voice Mode", "ja": "音声モード", "zh": "语音模式"},
    "settings.voice_mode_desc": {
        "en": "push_to_talk=Hold to talk, toggle=Toggle on/off, open_mic=Always on",
        "ja": "push_to_talk=押して話す, toggle=切り替え, open_mic=常時オン",
        "zh": "push_to_talk=按住说话, toggle=按键切换, open_mic=持续开启",
    },
    "settings.hotkey": {"en": "Hotkey", "ja": "ホットキー", "zh": "热键"},
    "settings.hotkey_desc": {
        "en": "Key to trigger speech recognition (click capture then press desired key)",
        "ja": "音声認識のトリガーキー（キャプチャをクリックしてキーを押す）",
        "zh": "语音识别触发按键（点击捕获按键后按下想要的按键）",
    },
    "settings.asr_lang": {"en": "Recognition Language", "ja": "認識言語", "zh": "识别语言"},
    "settings.asr_lang_desc": {"en": "Speech recognition model language", "ja": "音声認識モデルの言語", "zh": "语音识别模型语言"},

    "settings.tts_group": {"en": "Text-to-Speech (TTS)", "ja": "音声合成 (TTS)", "zh": "语音合成 (TTS)"},
    "settings.api_url": {"en": "API URL", "ja": "APIアドレス", "zh": "API 地址"},
    "settings.api_url_desc": {"en": "GPT-SoVITS API service URL", "ja": "GPT-SoVITS APIサービスのアドレス", "zh": "GPT-SoVITS API 服务地址"},
    "settings.ref_audio": {"en": "Reference Audio", "ja": "参照音声", "zh": "参考音频"},
    "settings.ref_audio_desc": {"en": "TTS reference audio file path", "ja": "TTS参照音声ファイルパス", "zh": "TTS 参考音频文件路径"},
    "settings.browse": {"en": "Browse", "ja": "参照", "zh": "浏览"},
    "settings.prompt_text": {"en": "Prompt Text", "ja": "プロンプトテキスト", "zh": "提示文本"},
    "settings.prompt_text_desc": {"en": "Text content of the reference audio", "ja": "参照音声に対応するテキスト内容", "zh": "参考音频对应的文本内容"},
    "settings.prompt_lang": {"en": "Prompt Language", "ja": "プロンプト言語", "zh": "提示语言"},
    "settings.prompt_lang_desc": {"en": "Language of the reference audio", "ja": "参照音声の言語", "zh": "参考音频的语言"},
    "settings.speaker_device": {"en": "Physical Speaker", "ja": "物理スピーカー", "zh": "物理扬声器"},
    "settings.speaker_desc": {
        "en": "Output device for self-monitoring synthesized voice; select \"None\" to disable",
        "ja": "合成音声のモニタリング用出力デバイス、「なし」で無効",
        "zh": "用于自己监听合成语音的输出设备，选择\"无\"则不监听",
    },
    "settings.virtual_device": {"en": "Virtual Audio Cable", "ja": "仮想オーディオケーブル", "zh": "虚拟声卡"},
    "settings.virtual_desc": {
        "en": "Virtual audio cable device for VRChat playback (e.g. CABLE Input)",
        "ja": "VRChatで再生する仮想オーディオケーブル（例: CABLE Input）",
        "zh": "用于VRChat游戏内播放的虚拟声卡设备 (如 CABLE Input)",
    },
    "settings.select_ref_audio": {
        "en": "Select Reference Audio",
        "ja": "参照音声を選択",
        "zh": "选择参考音频",
    },

    # --- About page ---
    "about.version": {"en": "Version: {version}", "ja": "バージョン: {version}", "zh": "版本: {version}"},
    "about.description": {
        "en": "VRChat voice synthesis tool based on GPT-SoVITS",
        "ja": "GPT-SoVITSベースのVRChat音声合成ツール",
        "zh": "基于 GPT-SoVITS 的 VRChat 语音合成工具",
    },
    "about.author": {"en": "Author", "ja": "作者", "zh": "作者"},
    "about.repo": {"en": "Repository", "ja": "リポジトリ", "zh": "项目地址"},
    "about.tech_stack": {"en": "Tech Stack", "ja": "技術スタック", "zh": "技术栈"},

    # --- Hotkey edit ---
    "hotkey.capture": {"en": "Capture", "ja": "キャプチャ", "zh": "捕获按键"},
    "hotkey.cancel": {"en": "Cancel", "ja": "キャンセル", "zh": "取消"},
    "hotkey.press_any": {"en": "Press any key...", "ja": "任意のキーを押す...", "zh": "按下任意键..."},

    # --- Audio device ---
    "device.none": {"en": "None", "ja": "なし", "zh": "无"},

    # --- Main window messages ---
    "msg.error": {"en": "Error", "ja": "エラー", "zh": "错误"},
    "msg.playback_finished": {"en": "Playback finished", "ja": "再生完了", "zh": "播放完成"},
    "msg.tts_not_connected": {
        "en": "GPT-SoVITS API not connected",
        "ja": "GPT-SoVITS API未接続",
        "zh": "GPT-SoVITS API 未连接",
    },
    "msg.tts_not_connected_desc": {
        "en": "Cannot connect to {url}, please make sure the API service is running",
        "ja": "{url}に接続できません。APIサービスが起動していることを確認してください",
        "zh": "无法连接到 {url}，请确保 API 服务已启动",
    },
    "msg.no_ref_audio": {"en": "Reference audio not set", "ja": "参照音声未設定", "zh": "未设置参考音频"},
    "msg.no_ref_audio_desc": {
        "en": "Please configure the reference audio path in Settings",
        "ja": "設定ページで参照音声パスを設定してください",
        "zh": "请在设置页面配置参考音频路径",
    },
    "msg.asr_model_missing": {"en": "ASR model not found", "ja": "ASRモデルが見つかりません", "zh": "ASR 模型未找到"},
    "msg.asr_model_missing_desc": {
        "en": "Please download the sherpa-onnx model to models/ directory, see models/README.md",
        "ja": "sherpa-onnxモデルをmodels/ディレクトリにダウンロードしてください。models/README.mdを参照",
        "zh": "请下载 sherpa-onnx 模型到 models/ 目录，详见 models/README.md",
    },
    "msg.no_virtual_cable": {
        "en": "Virtual audio cable not detected",
        "ja": "仮想オーディオケーブルが検出されません",
        "zh": "未检测到虚拟声卡",
    },
    "msg.no_virtual_cable_desc": {
        "en": "VB-Audio Virtual Cable not found, in-game VRChat playback will not work",
        "ja": "VB-Audio Virtual Cableが見つかりません。VRChat内再生機能は使用できません",
        "zh": "未找到 VB-Audio Virtual Cable，VRChat 内播放功能将不可用",
    },
    "msg.empty_text": {"en": "Please enter text to synthesize", "ja": "合成するテキストを入力してください", "zh": "请输入要合成的文本"},
    "msg.no_ref_audio_error": {
        "en": "Please configure reference audio path in Settings first",
        "ja": "先に設定で参照音声パスを設定してください",
        "zh": "请先在设置中配置参考音频路径",
    },

    # --- Language switch ---
    "lang.changed": {
        "en": "Language changed, please restart the application to take effect",
        "ja": "言語が変更されました。アプリケーションを再起動してください",
        "zh": "语言已更改，请重启应用生效",
    },
    "lang.changed_title": {"en": "Language Changed", "ja": "言語変更", "zh": "语言已更改"},
}


def set_language(lang: str) -> None:
    """Set the current UI language."""
    global _current_language
    if lang in LANGUAGES:
        _current_language = lang


def get_language() -> str:
    """Return the current UI language code."""
    return _current_language


def t(key: str, **kwargs) -> str:
    """Look up a translated string by key.

    Returns the string for the current language, formatted with any
    provided keyword arguments.  Falls back to the key itself when not found.
    """
    entry = _translations.get(key)
    if entry is None:
        return key
    text = entry.get(_current_language) or entry.get("en") or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
