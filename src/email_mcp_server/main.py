"""Main entry point for the Email MCP Server."""

import logging
import sys

import mcp.server.stdio
from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions

from .config import get_settings
from .email_tools import register_email_tools
from .logging_config import setup_logging

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)

# 创建 MCP 服务器实例
mcp = FastMCP("Email MCP Server")


def create_server() -> FastMCP:
    """创建并配置 MCP 服务器实例."""
    settings = get_settings()

    # 注册邮件相关工具
    register_email_tools(mcp)

    logger.info("Email MCP Server initialized")
    return mcp


def main() -> None:
    """主程序入口."""
    try:
        server = create_server()

        # 启动 stdio 服务器
        logger.info("Starting Email MCP Server...")

        # 运行服务器
        async def run_server():
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="email-mcp-server",
                        server_version="0.1.0",
                        capabilities=server.get_capabilities(
                            notification_options=None, experimental_capabilities=None
                        ),
                    ),
                )

        import asyncio

        asyncio.run(run_server())

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
