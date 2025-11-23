"""pytest 配置文件"""

import asyncio
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch
from typing import TYPE_CHECKING

import pytest

from email_mcp_server.config import reload_settings

if TYPE_CHECKING:
    from email_mcp_server.email_service import EmailService


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """异步事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_email_settings() -> Generator[Mock]:
    """模拟邮箱配置，使用.env.test中的真实配置"""
    import os
    from pathlib import Path

    # 加载.env.test文件
    env_test_path = Path(__file__).parent.parent / ".env.test"
    if env_test_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_test_path)

    with patch('email_mcp_server.config.get_email_settings') as mock:
        # 使用真实配置创建 Mock 对象
        from email_mcp_server.config import EmailSettings
        try:
            # 尝试获取真实配置
            real_settings = EmailSettings()

            # 创建基于真实配置的 Mock 对象，但仍然使用 Mock 接口
            settings = Mock()
            settings.address = real_settings.address
            settings.password = real_settings.password

            # Mock provider 属性
            provider_mock = Mock()
            provider_mock.value = real_settings.provider.value
            settings.provider = provider_mock

            # Mock SMTP 配置，使用真实配置的值
            smtp_config_mock = Mock()
            real_smtp = real_settings.smtp_config
            smtp_config_mock.server = real_smtp.server
            smtp_config_mock.port = real_smtp.port
            smtp_config_mock.use_tls = real_smtp.use_tls
            smtp_config_mock.use_ssl = real_smtp.use_ssl
            settings.smtp_config = smtp_config_mock

        except Exception:
            # 如果获取真实配置失败，回退到默认 Mock 配置
            settings = Mock()
            settings.address = os.getenv("EMAIL_ADDRESS", "test@example.com")
            settings.password = os.getenv("EMAIL_PASSWORD", "test_password")

            # Mock provider 属性
            provider_mock = Mock()
            provider_mock.value = "gmail"
            settings.provider = provider_mock

            # Mock SMTP 配置
            smtp_config_mock = Mock()
            smtp_config_mock.server = "smtp.gmail.com"
            smtp_config_mock.port = 587
            smtp_config_mock.use_tls = True
            smtp_config_mock.use_ssl = False
            settings.smtp_config = smtp_config_mock

        mock.return_value = settings
        yield mock


@pytest.fixture
def email_service_with_real_config(mock_email_settings) -> Generator[EmailService]:
    """使用真实配置的EmailService实例"""
    from email_mcp_server.email_service import EmailService

    # 在fixture激活状态下创建EmailService实例
    service = EmailService()
    yield service


@pytest.fixture
def temp_attachment_file(tmp_path: Path) -> str:
    """临时附件文件"""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test attachment content")
    return str(test_file)


@pytest.fixture
def temp_image_file(tmp_path: Path) -> str:
    """临时图片文件"""
    test_file = tmp_path / "test_image.jpg"
    # 创建一个简单的 JPEG 文件头
    test_file.write_bytes(b'\xff\xd8\xff\xe0\x00\x10JFIF')
    return str(test_file)


@pytest.fixture
def mock_requests_get() -> Generator[Mock]:
    """Mock requests.get"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.content = b"Remote file content"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_smtp_connection() -> Generator[Mock]:
    """Mock SMTP 连接"""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_conn = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_conn
        mock_conn.sendmail.return_value = {}
        yield mock_conn


@pytest.fixture
def mock_smtp_ssl_connection() -> Generator[Mock]:
    """Mock SMTP SSL 连接"""
    with patch('smtplib.SMTP_SSL') as mock_smtp:
        mock_conn = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_conn
        mock_conn.sendmail.return_value = {}
        yield mock_conn


@pytest.fixture
def reload_settings_after_test() -> Generator[None]:
    """测试后重新加载设置"""
    yield
    reload_settings()
