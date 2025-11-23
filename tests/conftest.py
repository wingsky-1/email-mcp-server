"""pytest 配置文件 - 统一Mock配置系统"""

import asyncio
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch
from typing import TYPE_CHECKING

import pytest

from email_mcp_server.config import reload_settings, EmailSettings

if TYPE_CHECKING:
    from email_mcp_server.email_service import EmailService


# 环境配置
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """自动加载测试环境配置"""
    env_test_path = Path(__file__).parent.parent / ".env.test"
    if env_test_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_test_path)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """异步事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# 核心Mock配置
@pytest.fixture
def mock_email_settings() -> Generator[Mock]:
    """统一邮箱配置Mock - 自动使用.env.test中的真实配置"""
    with patch('email_mcp_server.config.get_email_settings') as mock:
        try:
            # 使用真实配置创建Mock对象
            real_settings = EmailSettings()
            settings = _create_mock_from_real_settings(real_settings)
        except Exception:
            # 回退到环境变量配置
            settings = _create_fallback_mock_settings()

        mock.return_value = settings
        yield mock


def _create_mock_from_real_settings(real_settings: EmailSettings) -> Mock:
    """从真实配置创建Mock对象"""
    settings = Mock()
    settings.address = real_settings.address
    settings.password = real_settings.password
    settings.provider = real_settings.provider
    settings.smtp_config = real_settings.smtp_config
    return settings


def _create_fallback_mock_settings() -> Mock:
    """创建回退Mock配置"""
    import os
    settings = Mock()
    settings.address = os.getenv("EMAIL_ADDRESS", "test@example.com")
    settings.password = os.getenv("EMAIL_PASSWORD", "test_password")

    # Mock provider
    from email_mcp_server.models import EmailProvider
    settings.provider = EmailProvider.GMAIL

    # Mock SMTP配置
    from email_mcp_server.models import SMTPConfig
    settings.smtp_config = SMTPConfig(
        server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        port=int(os.getenv("SMTP_PORT", "587")),
        use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        use_ssl=os.getenv("SMTP_USE_SSL", "false").lower() == "true"
    )
    return settings


# 服务实例 fixtures
@pytest.fixture
def email_service(mock_email_settings) -> Generator[EmailService]:
    """标准EmailService实例 - 使用统一Mock配置"""
    from email_mcp_server.email_service import EmailService
    service = EmailService()
    yield service


@pytest.fixture
def email_service_with_real_config(mock_email_settings) -> Generator[EmailService]:
    """使用真实配置的EmailService实例 - 兼容性fixture"""
    from email_mcp_server.email_service import EmailService
    service = EmailService()
    yield service


# 文件和数据 fixtures
@pytest.fixture
def temp_attachment_file(tmp_path: Path) -> str:
    """临时文本附件文件"""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test attachment content for email testing")
    return str(test_file)


@pytest.fixture
def temp_image_file(tmp_path: Path) -> str:
    """临时图片文件"""
    test_file = tmp_path / "test_image.jpg"
    # 创建一个简单的 JPEG 文件头
    test_file.write_bytes(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C')
    return str(test_file)


@pytest.fixture
def temp_pdf_file(tmp_path: Path) -> str:
    """临时PDF文件"""
    test_file = tmp_path / "test.pdf"
    # 创建简单的PDF文件头
    test_file.write_bytes(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n')
    return str(test_file)


@pytest.fixture
def sample_email_message():
    """示例邮件消息"""
    from email_mcp_server.models import EmailMessage
    return EmailMessage(
        to=["recipient@example.com"],
        subject="Test Subject",
        body="Test Body",
        html_body="<p>Test HTML Body</p>",
        cc=["cc@example.com"],
        reply_to="reply@example.com",
        priority=1
    )


# 网络和连接 Mock fixtures
@pytest.fixture
def mock_smtp_connection():
    """Mock SMTP连接 - 支持TLS"""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_conn = Mock()
        mock_smtp.return_value = mock_conn
        mock_conn.sendmail.return_value = {}
        mock_conn.ehlo.return_value = (250, b"OK")
        mock_conn.starttls.return_value = (220, b"Ready")
        mock_conn.login.return_value = (235, b"Authentication successful")
        mock_conn.quit.return_value = (221, b"Bye")
        yield mock_smtp, mock_conn


@pytest.fixture
def mock_smtp_ssl_connection():
    """Mock SMTP SSL连接"""
    with patch('smtplib.SMTP_SSL') as mock_smtp_ssl:
        mock_conn = Mock()
        mock_smtp_ssl.return_value = mock_conn
        mock_conn.sendmail.return_value = {}
        mock_conn.login.return_value = (235, b"Authentication successful")
        mock_conn.quit.return_value = (221, b"Bye")
        yield mock_smtp_ssl, mock_conn


@pytest.fixture
def mock_requests_session():
    """Mock requests.Session用于附件下载"""
    with patch('requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.content = b"Remote file content for testing"
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/plain'}
        mock_session.get.return_value = mock_response

        yield mock_session, mock_response


@pytest.fixture
def mock_failed_requests():
    """Mock失败的requests请求"""
    with patch('requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # 模拟网络错误
        mock_session.get.side_effect = Exception("Network error")

        yield mock_session


# 确认机制 Mock fixtures
@pytest.fixture
def mock_confirmation_accept():
    """Mock用户确认接受"""
    mock_result = Mock()
    mock_result.action = "accept"
    mock_result.data = None
    return mock_result


@pytest.fixture
def mock_confirmation_cancel():
    """Mock用户确认取消"""
    mock_result = Mock()
    mock_result.action = "cancel"
    mock_result.data = None
    return mock_result


@pytest.fixture
def mock_elicit_context():
    """Mock带有确认功能的Context"""
    class MockContext:
        def __init__(self, response_data=None):
            self.response_data = response_data
            self.elicit_calls = []

        async def elicit(self, message, response_type=None):
            self.elicit_calls.append((message, response_type))
            if self.response_data:
                return self.response_data
            # 默认返回接受
            mock_result = Mock()
            mock_result.action = "accept"
            mock_result.data = None
            return mock_result

    return MockContext


# 清理和状态管理 fixtures
@pytest.fixture
def cleanup_temp_files():
    """清理临时文件"""
    temp_files = []

    def add_temp_file(file_path):
        temp_files.append(file_path)

    yield add_temp_file

    # 清理创建的临时文件
    import os
    for file_path in temp_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass  # 忽略清理错误


@pytest.fixture
def reload_settings_after_test():
    """测试后重新加载设置"""
    yield
    reload_settings()


# 错误模拟 fixtures
@pytest.fixture
def mock_smtp_auth_error():
    """Mock SMTP认证错误"""
    import smtplib
    with patch('smtplib.SMTP') as mock_smtp:
        mock_conn = Mock()
        mock_smtp.return_value = mock_conn
        mock_conn.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")
        yield mock_smtp, mock_conn


@pytest.fixture
def mock_smtp_connection_error():
    """Mock SMTP连接错误"""
    import smtplib
    with patch('smtplib.SMTP') as mock_smtp:
        mock_smtp.side_effect = smtplib.SMTPConnectError(421, b"Service not available")
        yield mock_smtp
