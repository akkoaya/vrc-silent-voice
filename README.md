<p align="center">
  <img src="VRCSV.png" alt="VRC Silent Voice" width="400">
</p>

<h1 align="center">VRC Silent Voice</h1>

<p align="center">
  <b>为 VRChat 无言势打造的语音合成工具</b>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#安装">安装</a> •
  <a href="#使用说明">使用说明</a> •
  <a href="#技术栈">技术栈</a>
</p>

<p align="center">
  中文 | <a href="README_EN.md">English</a>
</p>

---

## 这是什么？

在 VRChat 中，有一群玩家选择不使用自己的真实声音交流——他们被称为**无言势**。可能是出于社恐、隐私保护、声音焦虑，或者单纯觉得用自己的声音说话不够有趣。

**VRC Silent Voice** 就是为他们而生的。它让你可以用**你喜欢的声音**在 VRChat 中自由交流：

1. 对着麦克风说话（或直接打字）
2. 离线语音识别自动转为文字
3. GPT-SoVITS 将文字合成为你想要的声音
4. 通过虚拟声卡在 VRChat 中播放

**你的声音，由你定义。**

## 功能特性

- **离线语音识别 (ASR)** — 基于 Sherpa-ONNX，完全离线，隐私安全，支持中/英/日/韩多语言
- **高质量语音合成 (TTS)** — 接入 GPT-SoVITS V2 API，只需几秒参考音频即可克隆任意音色
- **双设备播放** — 合成语音同时输出到扬声器（自我监听）和虚拟声卡（游戏内播放）
- **灵活的语音模式** — 按住说话 / 按键切换 / 持续开启，适配不同使用习惯
- **完整参数控制** — 语速、温度、采样等 GPT-SoVITS 全部参数均可调节
- **多语言界面** — 支持中文 / English / 日本語
- **配置持久化** — 所有设置自动保存，下次启动即恢复

## 快速开始

### 前置要求

| 依赖 | 说明 |
|------|------|
| [Python 3.10+](https://www.python.org/) | 运行环境 |
| [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) | 语音合成后端 |
| [VB-Audio Virtual Cable](https://vb-audio.com/Cable/) | 虚拟声卡，用于将音频输入到 VRChat |
| [Sherpa-ONNX 模型](models/README.md) | 离线语音识别模型 |

### 安装

```bash
git clone https://github.com/akkoaya/vrc-silent-voice.git
cd vrc-silent-voice
pip install -r requirements.txt
```

### 启动

```bash
# 1. 先启动 GPT-SoVITS API 服务
python api_v2.py -a 127.0.0.1 -p 9880 -c GPT_SoVITS/configs/tts_infer.yaml

# 2. 启动 VRC Silent Voice
python main.py
```

## 使用说明

### 首次配置

1. 在 **设置** 页面配置：
   - **TTS**：API 地址、参考音频路径、提示文本
   - **TTS**：选择物理扬声器（监听）和虚拟声卡（游戏内播放）
   - **ASR**：选择麦克风、语音模式和热键

2. 在 **主页** 使用：
   - **打字模式**：输入文本 → 点击「生成语音」→ 双设备播放
   - **语音模式**：开启 ASR → 按热键说话 → 自动识别并合成播放

### VRChat 配置

1. 安装 [VB-Audio Virtual Cable](https://vb-audio.com/Cable/)
2. 在本应用设置中将 **虚拟声卡** 设为 `CABLE Input (VB-Audio Virtual Cable)`
3. 在 VRChat 音频设置中将 **麦克风** 设为 `CABLE Output (VB-Audio Virtual Cable)`

## 项目结构

```
vrc-silent-voice/
├── main.py                     # 入口
├── requirements.txt            # 依赖
├── config.json                 # 运行时配置 (自动生成)
├── app/
│   ├── config.py               # 配置 dataclass
│   ├── i18n.py                 # 国际化
│   ├── signals.py              # 全局信号总线
│   ├── common/
│   │   └── audio_devices.py    # 音频设备枚举
│   ├── core/
│   │   ├── asr_engine.py       # Sherpa-ONNX ASR 封装
│   │   ├── asr_worker.py       # 麦克风采集线程
│   │   ├── hotkey_manager.py   # 全局热键管理
│   │   ├── tts_client.py       # GPT-SoVITS HTTP 客户端
│   │   ├── audio_player.py     # 双设备音频播放
│   │   └── pipeline.py         # 编排器
│   └── ui/
│       ├── main_window.py      # 主窗口
│       ├── generation_page.py  # 生成页面
│       ├── settings_page.py    # 设置页面
│       ├── about_page.py       # 关于页面
│       └── components/         # UI 组件
├── models/                     # ASR 模型目录
└── tests/                      # 测试
```

## 技术栈

| 模块 | 技术 |
|------|------|
| UI 框架 | PyQt6 + PyQt-Fluent-Widgets |
| 语音识别 | Sherpa-ONNX (离线流式) |
| 语音合成 | GPT-SoVITS V2 API |
| 音频处理 | sounddevice + soundfile |
| 全局热键 | pynput |
| HTTP 客户端 | httpx |

## 许可证

本项目采用 [GPL-3.0 License](LICENSE) 开源。

## 致谢

- [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) — 强大的少样本语音合成
- [Sherpa-ONNX](https://github.com/k2-fsa/sherpa-onnx) — 高性能离线语音识别
- [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) — 现代化 Fluent Design UI 组件
- [VB-Audio Virtual Cable](https://vb-audio.com/Cable/) — 虚拟声卡驱动

## 备注

如果该项目对您有帮助，请在右上角添加Star，非常感谢
