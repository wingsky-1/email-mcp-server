@echo off
echo Starting Email MCP Server...

REM 优先尝试使用 uv
where uv >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo Using uv package manager...
    uv run email-mcp-server
    goto end
)

REM 回退到传统虚拟环境方式
echo uv not found, using traditional virtual environment...
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
    email-mcp-server
) else (
    echo Virtual environment not found. Please run:
    echo   uv sync
    echo OR
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -e ".[dev]"
    pause
    exit /b 1
)

:end
pause