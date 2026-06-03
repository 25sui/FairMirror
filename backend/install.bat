@echo off
chcp 65001 >nul
echo ========================================
echo FairMirror 后端服务安装脚本
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)
echo ✓ Python环境正常

echo.
echo [2/3] 安装基础依赖...
pip install -r requirements_base.txt
if errorlevel 1 (
    echo ❌ 基础依赖安装失败
    pause
    exit /b 1
)
echo ✓ 基础依赖安装完成

echo.
echo [3/3] 检查AI模型依赖（可选）...
echo 正在检查 transformers 和 torch...
pip show transformers >nul 2>&1
if errorlevel 1 (
    echo ⚠ transformers 未安装，AI模型功能将不可用
    echo    如需完整功能，请运行: pip install transformers torch
) else (
    echo ✓ AI模型依赖已安装
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 启动服务：
echo   uvicorn app.main:app --reload
echo.
echo 或使用简化版偏见检测（无需AI模型）：
echo   python run_simple.py
echo.
pause
