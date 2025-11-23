#!/bin/bash

echo "Starting Email MCP Server..."

# 优先尝试使用 uv
if command -v uv &> /dev/null; then
    echo "Using uv package manager..."
    uv run python -m email_mcp_server
else
    # 回退到传统虚拟环境方式
    echo "uv not found, using traditional virtual environment..."

    if [ -f ".venv/bin/activate" ]; then
        echo "Activating virtual environment..."
        source .venv/bin/activate
        python -m email_mcp_server
    else
        echo "Virtual environment not found. Please run:"
        echo "  uv sync"
        echo "OR"
        echo "  python -m venv .venv"
        echo "  source .venv/bin/activate"
        echo "  pip install -e \".[dev]\""
        exit 1
    fi
fi