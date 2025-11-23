"""Mock策略规范 - 统一Mock使用规范"""

from unittest.mock import Mock, patch
from typing import Dict, Any, Optional
import pytest


class MockStrategy:
    """Mock策略类，定义统一的Mock使用规范"""

    # 网络操作Mock策略
    NETWORK_MOCKS = {
        "smtp_connections": True,    # SMTP连接100%Mock
        "http_requests": True,       # HTTP请求100%Mock
        "dns_resolution": True,      # DNS解析100%Mock
    }

    # 文件系统Mock策略
    FILESYSTEM_MOCKS = {
        "remote_files": True,        # 远程文件操作Mock
        "local_files": False,        # 本地文件操作部分真实
        "temp_files": True,          # 临时文件Mock
    }

    # 数据模型Mock策略
    MODEL_MOCKS = {
        "pydantic_models": False,    # Pydantic模型不Mock，真实验证
        "external_apis": True,       # 外部API 100%Mock
    }

    @staticmethod
    def create_smtp_mock() -> tuple[Mock, Mock]:
        """创建标准SMTP Mock"""
        mock_smtp = Mock()
        mock_conn = Mock()

        # 配置连接Mock
        mock_smtp.return_value = mock_conn
        mock_conn.ehlo.return_value = (250, b"OK")
        mock_conn.starttls.return_value = (220, b"Ready to start TLS")
        mock_conn.login.return_value = (235, b"Authentication successful")
        mock_conn.sendmail.return_value = {}
        mock_conn.quit.return_value = (221, b"Bye")

        return mock_smtp, mock_conn

    @staticmethod
    def create_smtp_ssl_mock() -> tuple[Mock, Mock]:
        """创建SSL SMTP Mock"""
        mock_smtp_ssl = Mock()
        mock_conn = Mock()

        mock_smtp_ssl.return_value = mock_conn
        mock_conn.login.return_value = (235, b"Authentication successful")
        mock_conn.sendmail.return_value = {}
        mock_conn.quit.return_value = (221, b"Bye")

        return mock_smtp_ssl, mock_conn

    @staticmethod
    def create_http_session_mock(response_data: Optional[bytes] = None) -> tuple[Mock, Mock]:
        """创建HTTP Session Mock"""
        mock_session_class = Mock()
        mock_session = Mock()
        mock_response = Mock()

        mock_session_class.return_value = mock_session
        mock_session.get.return_value = mock_response

        if response_data:
            mock_response.content = response_data
            mock_response.status_code = 200
            mock_response.headers = {'content-type': 'application/octet-stream'}
        else:
            mock_response.content = b"Default mock content for testing"
            mock_response.status_code = 200
            mock_response.headers = {'content-type': 'text/plain'}

        mock_response.raise_for_status.return_value = None

        return mock_session_class, mock_session

    @staticmethod
    def create_error_smtp_mock(error_type: str, error_message: Optional[str] = None) -> tuple[Mock, Mock]:
        """创建错误SMTP Mock"""
        import smtplib

        mock_smtp = Mock()
        mock_conn = Mock()
        mock_smtp.return_value = mock_conn

        if error_type == "auth_failure":
            mock_conn.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")
        elif error_type == "connect_error":
            mock_smtp.side_effect = smtplib.SMTPConnectError(421, b"Service not available")
        elif error_type == "disconnected":
            mock_smtp.side_effect = smtplib.SMTPServerDisconnected("Server disconnected")
        elif error_type == "recipients_refused":
            mock_conn.sendmail.side_effect = smtplib.SMTPRecipientsRefused({"recipient@example.com": "Refused"})
        elif error_type == "sender_refused":
            mock_conn.sendmail.side_effect = smtplib.SMTPSenderRefused(550, "Sender refused", "test@example.com")
        elif error_type == "data_error":
            mock_conn.sendmail.side_effect = smtplib.SMTPDataError(550, "Data error")
        else:
            mock_conn.sendmail.side_effect = Exception(error_message or "General error")

        return mock_smtp, mock_conn

    @staticmethod
    def create_filesystem_mock(file_exists: bool = True, file_size: int = 1024) -> Dict[str, Mock]:
        """创建文件系统Mock"""
        mock_path = Mock()
        mock_path.exists.return_value = file_exists
        mock_path.stat.return_value.st_size = file_size
        mock_path.name = "test_file.txt"
        mock_path.suffix = ".txt"

        return {
            "path": mock_path,
            "stat_result": mock_path.stat.return_value
        }

    @staticmethod
    def apply_email_settings_mock(settings_data: Optional[Dict[str, Any]] = None):
        """应用邮箱设置Mock装饰器"""
        if settings_data is None:
            from .test_data_factory import TestDataFactory
            settings_data = TestDataFactory.create_email_settings_mock()

        def decorator(func):
            return patch('email_mcp_server.email_service.get_email_settings')(
                patch('email_mcp_server.config.get_email_settings')(
                    func
                )
            )
        return decorator

    @staticmethod
    def apply_app_settings_mock(settings_data: Optional[Dict[str, Any]] = None):
        """应用应用设置Mock装饰器"""
        if settings_data is None:
            from .test_data_factory import TestDataFactory
            settings_data = TestDataFactory.create_app_settings_mock()

        return patch('email_mcp_server.attachment_service.get_app_settings')(
            lambda *args, **kwargs: Mock(**settings_data)
        )


# 预定义的Mock配置
def create_standard_email_settings_mock():
    """创建标准邮箱设置Mock"""
    settings_mock = Mock()
    settings_mock.address = "test@example.com"
    settings_mock.password = "test_password"
    settings_mock.provider = Mock()
    settings_mock.provider.value = "gmail"

    smtp_config = Mock()
    smtp_config.server = "smtp.gmail.com"
    smtp_config.port = 587
    smtp_config.use_tls = True
    smtp_config.use_ssl = False
    settings_mock.smtp_config = smtp_config

    return settings_mock

STANDARD_EMAIL_SETTINGS_MOCK = create_standard_email_settings_mock()

STANDARD_APP_SETTINGS_MOCK = Mock(
    log_level="INFO",
    max_attachment_size=25 * 1024 * 1024,
    temp_dir="temp",
    download_timeout=30,
    max_retries=3,
    require_confirmation=False
)


# Mock装饰器工厂
def mock_email_service(func):
    """EmailService Mock装饰器"""
    @patch('email_mcp_server.email_service.get_email_settings')
    def wrapper(mock_get_settings, *args, **kwargs):
        # 设置Mock返回值
        settings_mock = Mock()
        settings_mock.address = "test@example.com"
        settings_mock.password = "test_password"
        settings_mock.provider = Mock()
        settings_mock.provider.value = "gmail"
        settings_mock.smtp_config = Mock(
            server="smtp.gmail.com",
            port=587,
            use_tls=True,
            use_ssl=False
        )
        mock_get_settings.return_value = settings_mock

        return func(*args, **kwargs)
    return wrapper


def mock_attachment_service(func):
    """AttachmentService Mock装饰器"""
    @patch('email_mcp_server.attachment_service.get_app_settings')
    def wrapper(mock_get_settings, *args, **kwargs):
        mock_get_settings.return_value = STANDARD_APP_SETTINGS_MOCK
        return func(*args, **kwargs)
    return wrapper


# Mock上下文管理器
class SMTPMockContext:
    """SMTP Mock上下文管理器"""

    def __init__(self, error_type: Optional[str] = None):
        self.error_type = error_type

    def __enter__(self):
        if self.error_type:
            return MockStrategy.create_error_smtp_mock(self.error_type)
        else:
            return MockStrategy.create_smtp_mock()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class HTTPSessionMockContext:
    """HTTP Session Mock上下文管理器"""

    def __init__(self, response_data: Optional[bytes] = None, should_fail: bool = False):
        self.response_data = response_data
        self.should_fail = should_fail

    def __enter__(self):
        mock_session_class, mock_session = MockStrategy.create_http_session_mock(self.response_data)

        if self.should_fail:
            mock_session.get.side_effect = Exception("Network error")

        return mock_session_class, mock_session

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# 验证Mock策略的函数
def validate_mock_strategy(test_function):
    """验证测试函数是否遵循Mock策略"""
    def wrapper(*args, **kwargs):
        # 这里可以添加Mock策略验证逻辑
        # 例如检查是否正确Mock了外部依赖
        return test_function(*args, **kwargs)
    return wrapper