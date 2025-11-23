"""pytest 配置文件"""

import asyncio
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from email_mcp_server.config import reload_settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """异步事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_email_settings() -> Generator[Mock]:
    """模拟邮箱配置"""
    with patch('email_mcp_server.config.get_email_settings') as mock:
        # 创建 EmailSettings 的 Mock 对象
        settings = Mock()
        settings.address = "test@example.com"
        settings.password = "test_password"

        # Mock provider 属性
        provider_mock = Mock()
        provider_mock.value = "gmail"
        settings.provider = provider_mock

        # Mock SMTP 配置
        settings.smtp_server = None
        settings.smtp_port = None
        settings.smtp_use_tls = None
        settings.smtp_use_ssl = None

        # Mock get_smtp_config 方法
        smtp_config_mock = Mock()
        smtp_config_mock.server = "smtp.gmail.com"
        smtp_config_mock.port = 587
        smtp_config_mock.use_tls = True
        smtp_config_mock.use_ssl = False
        settings.get_smtp_config = Mock(return_value=smtp_config_mock)

        mock.return_value = settings
        yield mock


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
