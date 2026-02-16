# Sherpa-ONNX ASR 模型

本目录用于存放离线语音识别模型文件。

## 推荐模型

| 模型 | 语言 | 压缩包大小 | 说明 |
|------|------|-----------|------|
| sherpa-onnx-streaming-paraformer-bilingual-zh-en | 中文 + 英文 | ~999 MB | **推荐** |
| sherpa-onnx-streaming-paraformer-trilingual-zh-cantonese-en | 中文 + 粤语 + 英文 | ~999 MB | 需要粤语时选择 |

## Windows 安装指南

### 浏览器手动下载

1. 打开浏览器访问：
   https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-paraformer-bilingual-zh-en.tar.bz2
2. 下载完成后，使用 [7-Zip](https://7-zip.org/) 右键 → 解压到当前文件夹，得到 `.tar` 文件
3. 再次用 7-Zip 解压 `.tar` 文件
4. 将解压出的 `sherpa-onnx-streaming-paraformer-bilingual-zh-en` 文件夹移动到项目的 `models/` 目录下

## 验证安装

安装完成后，`models/` 目录结构应为：
```
models/
├── README.md
└── sherpa-onnx-streaming-paraformer-bilingual-zh-en/
    ├── encoder.int8.onnx    (158 MB, 推荐使用)
    ├── decoder.int8.onnx    (68 MB, 推荐使用)
    ├── encoder.onnx         (607 MB, 全精度)
    ├── decoder.onnx         (218 MB, 全精度)
    ├── tokens.txt
    └── test_wavs/
        └── 0.wav
```

程序优先使用 `int8` 量化版本（更快、更省内存）。如果磁盘空间有限，可以删除全精度版本：
```powershell
Remove-Item models\sherpa-onnx-streaming-paraformer-bilingual-zh-en\encoder.onnx
Remove-Item models\sherpa-onnx-streaming-paraformer-bilingual-zh-en\decoder.onnx
```

## 支持的模型格式

程序会自动在 `models/` 目录及其子目录中搜索以下文件：
- `encoder.onnx` 或 `encoder.int8.onnx`
- `decoder.onnx` 或 `decoder.int8.onnx`
- `tokens.txt`

## 常见问题

**Q: 下载速度很慢怎么办？**
A: GitHub 在国内访问可能较慢，可以尝试：
- 使用代理/VPN
- 使用 GitHub 镜像站（如 https://mirror.ghproxy.com/）
- 使用迅雷等下载工具下载 `.tar.bz2` 文件后手动解压

**Q: 启动后提示"ASR 模型未找到"？**
A: 确认 `models/` 目录下有包含 `encoder.int8.onnx`、`decoder.int8.onnx`、`tokens.txt` 的子文件夹。

**Q: 只需要中文识别，有更小的模型吗？**
A: 目前推荐的双语模型是最佳平衡选择。更多模型请访问：
https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models

## 其他语言模型

访问 https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models 查看所有可用模型。
