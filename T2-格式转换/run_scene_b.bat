@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ==^> 场景B GBK→UTF-8
echo ==^> 不调用任何大模型 API。

if not exist .venv (
  echo ==^> 创建虚拟环境 .venv
  python -m venv .venv
  if errorlevel 1 (
    echo [错误] 创建 venv 失败。请先安装 Python 3.9+ 并勾选 Add to PATH。
    exit /b 1
  )
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
  echo [错误] 无法激活 .venv\Scripts\activate.bat
  exit /b 1
)

echo ==^> 安装依赖（课前若已预装会很快）
python -m pip install -r requirements.txt -q

echo ==^> 清空并重建 samples\output\scene_b
if exist "samples\output\scene_b" rmdir /S /Q "samples\output\scene_b"
mkdir "samples\output\scene_b"

echo ==^> 执行批处理
python format_batch.py --config config.scene_b.yaml
if errorlevel 1 exit /b %errorlevel%

echo.
echo ==^> 输出 samples\output\scene_b\
dir /B "samples\output\scene_b"
echo 场景完成。
endlocal
