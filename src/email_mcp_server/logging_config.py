"""Logging configuration for the Email MCP Server."""

import logging
import logging.handlers
import sys
from pathlib import Path

from .config import get_app_settings


def setup_logging() -> None:
    """设置日志配置."""
    try:
        settings = get_app_settings()

        # 创建日志格式
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

        # 清除现有的处理器
        root_logger.handlers.clear()

        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # 添加文件处理器（如果配置了日志文件）
        if settings.log_file:
            log_path = Path(settings.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # 使用轮转文件处理器，每个文件最大 10MB，保留 5 个备份
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_path,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # 设置第三方库的日志级别
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)

    except Exception as e:
        # 如果日志配置失败，使用基本配置
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logging.warning(f"Failed to configure logging: {e}")


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器."""
    return logging.getLogger(name)
