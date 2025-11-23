@echo off
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting Email MCP Server...
python -m email_mcp_server

pause