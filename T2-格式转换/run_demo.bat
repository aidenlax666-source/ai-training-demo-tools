@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ==^> T2 最小一键演示（CSV→Excel + 可选重命名）
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

if not exist config.demo-minimal.yaml (
  echo [错误] 缺少 config.demo-minimal.yaml
  exit /b 1
)
copy /Y config.demo-minimal.yaml config.yaml >nul

echo ==^> 清空 samples\output 根目录下的旧文件
if not exist samples\output mkdir samples\output
del /Q samples\output\*.* 2>nul

echo ==^> 执行最小演示
python format_batch.py --config config.demo-minimal.yaml
if errorlevel 1 exit /b %errorlevel%

echo.
echo ==^> 输出目录 samples\output\
dir /B samples\output
echo.
echo 最小演示完成。三种精讲场景请分别双击：
echo   run_scene_a.bat   CSV^↔Excel
echo   run_scene_b.bat   GBK→UTF-8
echo   run_scene_c.bat   批量重命名
endlocal
