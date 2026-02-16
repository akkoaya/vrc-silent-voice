# VRC Silent Voice

VRChat 语音交互工具：通过离线语音识别(ASR)捕获语音转文字，调用 GPT-SoVITS API 合成语音，再通过虚拟声卡在游戏内播放。

## 功能

- **离线语音识别 (ASR)**: 使用 Sherpa-ONNX 实现离线流式中文语音识别
- **语音合成 (TTS)**: 调用 GPT-SoVITS V2 API 进行高质量语音合成
- **双设备播放**: 同时输出到物理扬声器（自我监听）和虚拟声卡（VRChat 内播放）
- **全局热键**: 支持按住说话、切换说话、持续开启三种模式
- **自定义热键**: 可自定义语音触发按键
- **麦克风选择**: 支持选择输入设备
- **完整参数控制**: 支持 GPT-SoVITS API 全部参数调整
- **配置持久化**: 所有设置自动保存到 config.json

## 前置要求

1. **Python 3.10+**
2. **GPT-SoVITS**: 启动 API 服务
   ```bash
   python api_v2.py -a 127.0.0.1 -p 9880 -c GPT_SoVITS/configs/tts_infer.yaml
   ```
3. **VB-Audio Virtual Cable**: 安装虚拟声卡 https://vb-audio.com/Cable/
4. **Sherpa-ONNX 模型**: 见 [models/README.md](models/README.md)

## 安装

```bash
cd vrc-silent-voice
pip install -r requirements.txt
```

## 使用

```bash
python main.py
```

### 快速开始

1. 启动 GPT-SoVITS API 服务
2. 运行 `python main.py`
3. 在设置页面配置:
   - TTS: API 地址、参考音频路径、提示文本
   - TTS: 选择物理扬声器和虚拟声卡设备
   - ASR: 选择麦克风、语音模式和热键
4. 在生成页面:
   - 输入文本 → 点击"生成语音" → 双设备播放
   - 或开启 ASR → 按热键说话 → 自动识别并合成

### VRChat 设置

1. 安装 VB-Audio Virtual Cable
2. 在应用设置中将"虚拟声卡"设为 `CABLE Input (VB-Audio Virtual Cable)`
3. 在 VRChat 设置中将麦克风设为 `CABLE Output (VB-Audio Virtual Cable)`

## 项目结构

```
vrc-silent-voice/
├── main.py                    # 入口
├── requirements.txt           # 依赖
├── config.json                # 运行时配置(自动生成)
├── app/
│   ├── config.py              # 配置 dataclass
│   ├── signals.py             # 全局信号总线
│   ├── common/
│   │   └── audio_devices.py   # 音频设备枚举
│   ├── core/
│   │   ├── asr_engine.py      # Sherpa-ONNX ASR 封装
│   │   ├── asr_worker.py      # 麦克风采集线程
│   │   ├── hotkey_manager.py  # 全局热键管理
│   │   ├── tts_client.py      # GPT-SoVITS HTTP 客户端
│   │   ├── audio_player.py    # 双设备音频播放
│   │   └── pipeline.py        # 编排器
│   └── ui/
│       ├── main_window.py     # 主窗口
│       ├── generation_page.py # 生成页面
│       ├── settings_page.py   # 设置页面
│       └── components/        # UI 组件
├── models/                    # ASR 模型目录
└── tests/                     # 测试
```

## 测试

```bash
python -m pytest tests/ -v
```

## 技术栈

- **UI**: PyQt5 + PyQt-Fluent-Widgets
- **ASR**: Sherpa-ONNX (离线流式识别)
- **TTS**: GPT-SoVITS V2 API
- **音频**: sounddevice + soundfile
- **热键**: pynput
- **HTTP**: httpx
