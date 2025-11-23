"""Main entry point for the Email MCP Server."""

import logging

from mcp.server.fastmcp import FastMCP

from .config import get_email_settings
from .email_tools import register_email_tools
from .logging_config import setup_logging

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)

# 全局服务器实例（延迟初始化）
_mcp_instance = None


def create_server(name: str = "Email MCP Server") -> FastMCP:
    """创建并配置 MCP 服务器实例."""
    global _mcp_instance

    if _mcp_instance is None:
        # 创建 MCP 服务器实例
        _mcp_instance = FastMCP(
            name=name,
            instructions="一个强大的邮件发送MCP服务器，支持QQ邮箱和Gmail，可以发送文本、HTML邮件和附件。",
            website_url="https://github.com/your-email/email-mcp-server",
            debug=False,
            log_level="INFO",
        )

        # 注册工具
        try:
            register_email_tools(_mcp_instance)
            logger.info("Email tools registered successfully")
        except Exception as e:
            logger.error(f"Failed to register email tools: {e}")

    try:
        # 测试邮箱配置
        email_settings = get_email_settings()
        logger.info(f"Configured for email provider: {email_settings.provider.value}")
    except Exception as e:
        logger.warning(f"Email configuration issue: {e}")
        logger.info(
            "Server will start but email functions require proper configuration"
        )

    logger.info("Email MCP Server initialized successfully")
    return _mcp_instance


def get_server() -> FastMCP:
    """获取已初始化的服务器实例."""
    if _mcp_instance is None:
        return create_server()
    return _mcp_instance


def main() -> None:
    """主程序入口."""
    try:
        # 创建并配置服务器
        server = create_server()

        # 启动 stdio 服务器
        logger.info("Starting Email MCP Server in STDIO mode...")

        # 使用 FastMCP 的内置 run 方法
        server.run(transport="stdio")

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
