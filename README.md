# PDF 翻译工程

基于 MinerU 的 PDF 翻译工具，自动将 PDF 转换为 Markdown，翻译成中文，并转换为 DOCX 格式。

## 功能特点

- **PDF 转 Markdown**：使用 MinerU 解析 PDF，保留公式、表格、图片等结构
- **自动翻译**：调用阿里云通义千问 API 将 Markdown 翻译成中文
- **DOCX 转换**：使用 Pandoc 将 Markdown 转换为 Word 文档，自动设置字体（英文 Times New Roman，中文宋体）
- **GPU 加速**：支持 NVIDIA CUDA 加速（需安装 CUDA 版 PyTorch）

## 环境要求

- Python 3.10-3.12
- Conda
- NVIDIA GPU（可选，用于加速）
- Pandoc（用于 DOCX 转换）

## 快速开始

### 1. 安装依赖

```bash
# 运行安装脚本
install.bat
```

安装脚本会自动：
- 创建 `pdf_translate_m` conda 环境
- 安装 MinerU 及所有依赖
- 安装 dashscope（翻译 API 客户端）
- 安装 python-docx（DOCX 处理）

### 2. 安装 Pandoc

Pandoc 用于 Markdown 到 DOCX 的转换，需要单独安装：

1. 访问 https://pandoc.org/installing.html 下载并安装
2. Windows 用户可使用 Chocolatey 安装：`choco install pandoc`

### 3. 配置 API 密钥

复制 `.env.example` 文件为 `.env`，然后填入你的阿里云 API 密钥：

```bash
copy .env.example .env
```

编辑 `.env` 文件：

```
ALIYUN_KEY=sk-your-api-key-here
ALIYUN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**获取 API 密钥**：访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/apiKey) 创建 API Key。

### 4. 使用方法

将 PDF 文件放入 `aims/` 目录，然后运行：

```batch
run_mineru_all.bat
```

完整流程：PDF → Markdown → 翻译 → DOCX → 输出到 `output/` 目录

## 分步执行

工程提供三个批处理脚本，可分步执行：

| 脚本 | 功能 |
|------|------|
| `run_mineru_all.bat` | 完整流程：PDF → Markdown → 翻译 → DOCX |
| `run_mineru_translate.bat` | PDF → Markdown → 翻译（不含 DOCX） |
| `run_mineru_convert.bat` | PDF → Markdown → DOCX（不翻译） |

## 目录结构

```
pdf_translate/
├── aims/                     # PDF 输入目录 / 临时处理目录
├── output/                   # 最终输出文件目录
├── media/                    # 提取的图片文件（由 pandoc 生成）
├── .env                      # API 密钥配置（需自行创建）
├── .env.example              # API 密钥配置模板
├── requirements.txt          # Python 依赖
├── translate_md.py           # 翻译脚本
├── convert_md_to_docx.py     # MD 转 DOCX 脚本
├── install.bat               # 安装脚本
├── run_mineru_all.bat        # 主批处理脚本
├── run_mineru_translate.bat  # 翻译脚本
└── run_mineru_convert.bat    # 转换脚本
```

## 翻译配置

`translate_md.py` 中可修改翻译相关配置：

- **专业领域**：当前针对化学与环境专业优化
- **模型**：使用 `qwen-plus` 模型
- **分块大小**：默认 3000 字符/块，避免超出 API 限制

## 常见问题

### CUDA is not available

如果运行时报错 "CUDA is not available"，需要安装 CUDA 版 PyTorch：

```bash
conda activate pdf_translate_m
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### Pandoc 未安装

运行 `convert_md_to_docx.py` 时会检查 pandoc，如未安装请先安装：
- Windows: `choco install pandoc` 或从官网下载安装

### MinerU 安装失败

如果自动安装失败，可手动安装：

```bash
pip install --upgrade pip
pip install uv
uv pip install -U "mineru[all]"
```

## 依赖说明

- **MinerU**: PDF 解析引擎
- **dashscope**: 阿里云通义千问 API 客户端
- **python-docx**: DOCX 文档处理
- **pandoc**: 文档格式转换工具
