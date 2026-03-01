@echo off
echo ========================================
echo MinerU PDF 翻译工具 - 安装脚本
echo ========================================
echo.

rem 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10-3.12
    pause
    exit /b 1
)

echo [1/5] 创建 conda 环境...
conda create -n pdf_translate_m python=3.10 -y
if errorlevel 1 (
    echo [错误] 创建 conda 环境失败
    pause
    exit /b 1
)

echo [2/5] 激活环境...
call conda activate pdf_translate_m

echo [4/5] 安装 uv...
pip install uv 

echo [5/5] 安装 MinerU 和依赖...
uv pip install -U "mineru[all]" 
pip install dashscope python-docx 
uv pip install "mineru[core,lmdeploy]"

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 使用说明：
echo 1. 编辑 .env 文件，填入你的阿里云 API 密钥
echo 2. 将 PDF 文件放入 aims 目录
echo 3. 运行 run_mineru_all.bat 开始处理
echo.
echo 注意：还需要安装 pandoc 用于 DOCX 转换
echo 访问 https://pandoc.org/installing.html 下载安装
echo.

pause
