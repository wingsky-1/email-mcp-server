"""EmailService 测试 - 完整功能测试"""

import pytest
import smtplib
from unittest.mock import Mock, patch, MagicMock
from typing import Generator
from pathlib import Path

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

from email_mcp_server.email_service import EmailService
from email_mcp_server.config import EmailSettings
from email_mcp_server.models import EmailMessage, Attachment, AttachmentType
from email_mcp_server.exceptions import (
    AuthenticationError,
    SMTPConnectionError,
    EmailServiceError,
    ValidationError
)
from .test_data_factory import TestDataFactory
from .mock_strategy import MockStrategy, STANDARD_EMAIL_SETTINGS_MOCK


@pytest.fixture
def email_service() -> Generator[EmailService, None, None]:
    """使用统一Mock配置的EmailService实例"""
    with patch('email_mcp_server.email_service.get_email_settings') as mock_get_settings:
        mock_get_settings.return_value = STANDARD_EMAIL_SETTINGS_MOCK

        # 创建EmailService实例并Mock附件服务
        service = EmailService()
        service.attachment_service = Mock()
        yield service


class TestEmailServiceBasic:
    """EmailService 基础功能测试"""

    @pytest.mark.unit
    def test_service_initialization(self, email_service):
        """测试服务初始化"""
        assert email_service.settings is not None
        assert email_service.settings.address == "test@example.com"
        assert email_service.settings.password == "test_password"
        assert email_service._connection is None

    @pytest.mark.unit
    def test_connect_success_tls(self, email_service):
        """测试TLS连接成功"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_smtp.return_value = mock_conn

            email_service.connect()

            # 验证连接参数
            mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
            mock_conn.ehlo.assert_called()
            mock_conn.starttls.assert_called_once()
            mock_conn.login.assert_called_once_with("test@example.com", "test_password")
            assert email_service._connection is mock_conn

    @pytest.mark.unit
    def test_connect_success_ssl(self, email_service):
        """测试SSL连接成功"""
        email_service.settings.smtp_config.use_tls = False
        email_service.settings.smtp_config.use_ssl = True

        with patch('smtplib.SMTP_SSL') as mock_smtp_ssl:
            mock_conn = Mock()
            mock_smtp_ssl.return_value = mock_conn

            email_service.connect()

            mock_smtp_ssl.assert_called_once_with("smtp.gmail.com", 587)
            mock_conn.login.assert_called_once_with("test@example.com", "test_password")
            assert email_service._connection is mock_conn

    @pytest.mark.unit
    def test_connect_already_connected(self, email_service):
        """测试重复连接"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_smtp.return_value = mock_conn

            # 第一次连接
            email_service.connect()

            # 第二次连接应该不创建新连接
            email_service.connect()

            # 验证只调用了一次SMTP构造函数
            assert mock_smtp.call_count == 1

    @pytest.mark.unit
    def test_disconnect_success(self, email_service):
        """测试断开连接成功"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_smtp.return_value = mock_conn

            email_service.connect()
            email_service.disconnect()

            mock_conn.quit.assert_called_once()
            assert email_service._connection is None

    @pytest.mark.unit
    def test_disconnect_not_connected(self, email_service):
        """测试未连接时断开连接"""
        # 应该不抛出异常
        email_service.disconnect()
        assert email_service._connection is None

    @pytest.mark.unit
    def test_disconnect_with_exception(self, email_service):
        """测试断开连接时的异常处理"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.quit.side_effect = Exception("Disconnect error")
            mock_smtp.return_value = mock_conn

            email_service.connect()
            # 应该不抛出异常
            email_service.disconnect()
            assert email_service._connection is None


class TestEmailServiceConnectionErrors:
    """EmailService 连接错误测试"""

    @pytest.mark.unit
    def test_connect_authentication_failure_535(self, email_service):
        """测试认证失败错误 (535)"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")
            mock_smtp.return_value = mock_conn

            with pytest.raises(SMTPConnectionError, match="Connection error"):
                email_service.connect()

    @pytest.mark.unit
    def test_connect_authentication_failure_530(self, email_service):
        """测试需要认证错误 (530)"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.login.side_effect = smtplib.SMTPAuthenticationError(530, b"Authentication required")
            mock_smtp.return_value = mock_conn

            with pytest.raises(SMTPConnectionError, match="Connection error"):
                email_service.connect()

    @pytest.mark.unit
    def test_connect_authentication_failure_other(self, email_service):
        """测试其他认证错误"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.login.side_effect = smtplib.SMTPAuthenticationError(550, b"Other error")
            mock_smtp.return_value = mock_conn

            with pytest.raises(SMTPConnectionError, match="Connection error"):
                email_service.connect()

    @pytest.mark.unit
    def test_connect_server_connect_error(self, email_service):
        """测试服务器连接错误"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPConnectError(421, b"Service not available")

            with pytest.raises(SMTPConnectionError, match="Failed to connect"):
                email_service.connect()

    @pytest.mark.unit
    def test_connect_server_disconnected(self, email_service):
        """测试服务器断开连接错误"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPServerDisconnected("Server disconnected")

            with pytest.raises(SMTPConnectionError, match="SMTP server disconnected"):
                email_service.connect()

    @pytest.mark.unit
    def test_connect_general_exception(self, email_service):
        """测试连接时的其他异常"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = Exception("General error")

            with pytest.raises(SMTPConnectionError, match="Connection error"):
                email_service.connect()


class TestEmailServiceSending:
    """EmailService 邮件发送测试"""

    @pytest.mark.unit
    def test_send_simple_email_success(self, email_service):
        """测试发送简单邮件成功"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_smtp.return_value = mock_conn
            mock_conn.sendmail.return_value = {}

            email_service.connect()

            message = TestDataFactory.create_email_message(
                to=["recipient@example.com"],
                subject="Test Subject",
                body="Test Body"
            )

            result = email_service.send_email(message)

            assert result == "sent"
            mock_conn.sendmail.assert_called_once()
            call_args = mock_conn.sendmail.call_args[0]
            assert call_args[0] == "test@example.com"  # from_addr
            assert call_args[1] == ["recipient@example.com"]  # to_addrs

    @pytest.mark.unit
    def test_send_email_with_cc_bcc(self, email_service):
        """测试发送带抄送和密送的邮件"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.sendmail.return_value = {}
            mock_smtp.return_value = mock_conn

            email_service.connect()

            message = EmailMessage(
                to=["to@example.com"],
                subject="Test",
                body="Body",
                cc=["cc@example.com"],
                bcc=["bcc@example.com"]
            )

            email_service.send_email(message)

            # 验证收件人列表包含所有类型
            call_args = mock_conn.sendmail.call_args[0]
            recipients = call_args[1]
            assert "to@example.com" in recipients
            assert "cc@example.com" in recipients
            assert "bcc@example.com" in recipients

    @pytest.mark.unit
    def test_send_email_with_html_content(self, email_service):
        """测试发送HTML邮件"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.sendmail.return_value = {}
            mock_smtp.return_value = mock_conn

            email_service.connect()

            message = EmailMessage(
                to=["recipient@example.com"],
                subject="HTML Test",
                body="Plain text",
                html_body="<h1>HTML Content</h1>"
            )

            email_service.send_email(message)

            mock_conn.sendmail.assert_called_once()

    @pytest.mark.unit
    def test_send_email_with_priority(self, email_service):
        """测试发送带优先级的邮件"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.sendmail.return_value = {}
            mock_smtp.return_value = mock_conn

            email_service.connect()

            message = EmailMessage(
                to=["recipient@example.com"],
                subject="Priority Test",
                body="Body",
                priority=1  # High priority
            )

            email_service.send_email(message)

            mock_conn.sendmail.assert_called_once()

    @pytest.mark.unit
    def test_send_email_with_attachments(self, email_service):
        """测试发送带附件的邮件"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.sendmail.return_value = {}
            mock_smtp.return_value = mock_conn

            email_service.connect()

            # Mock附件处理
            attachment_result = Mock()
            attachment_result.filename = "test.txt"
            attachment_result.content_type = "text/plain"
            attachment_result.data = b"test content"
            attachment_result.size = 12

            email_service.attachment_service.process_attachment.return_value = attachment_result

            attachment = Attachment(path="/path/to/test.txt", type=AttachmentType.LOCAL)

            message = EmailMessage(
                to=["recipient@example.com"],
                subject="Attachment Test",
                body="Body",
                attachments=[attachment]
            )

            email_service.send_email(message)

            # 验证附件被处理
            email_service.attachment_service.process_attachment.assert_called_once_with(attachment)
            mock_conn.sendmail.assert_called_once()

    @pytest.mark.unit
    def test_send_email_auto_connect(self, email_service):
        """测试发送邮件时自动连接"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.sendmail.return_value = {}
            mock_smtp.return_value = mock_conn

            # 不手动连接，让send_email自动连接
            message = EmailMessage(
                to=["recipient@example.com"],
                subject="Auto Connect Test",
                body="Body"
            )

            email_service.send_email(message)

            mock_smtp.assert_called_once()
            mock_conn.sendmail.assert_called_once()

    @pytest.mark.unit
    def test_send_email_partial_failure(self, email_service):
        """测试部分邮件发送失败"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            # 模拟部分发送失败
            mock_conn.sendmail.return_value = {"failed@example.com": "Error message"}
            mock_smtp.return_value = mock_conn

            email_service.connect()

            message = EmailMessage(
                to=["recipient@example.com", "failed@example.com"],
                subject="Partial Failure Test",
                body="Body"
            )

            with pytest.raises(EmailServiceError, match="Failed to send to 1 recipients"):
                email_service.send_email(message)

    @pytest.mark.unit
    def test_send_email_recipients_refused(self, email_service):
        """测试所有收件人被拒绝"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.sendmail.side_effect = smtplib.SMTPRecipientsRefused({"recipient@example.com": "Refused"})
            mock_smtp.return_value = mock_conn

            email_service.connect()

            message = EmailMessage(
                to=["recipient@example.com"],
                subject="Recipients Refused Test",
                body="Body"
            )

            with pytest.raises(EmailServiceError, match="All recipients were refused"):
                email_service.send_email(message)

    @pytest.mark.unit
    def test_send_email_sender_refused(self, email_service):
        """测试发件人被拒绝"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.sendmail.side_effect = smtplib.SMTPSenderRefused(550, "Sender refused", "test@example.com")
            mock_smtp.return_value = mock_conn

            email_service.connect()

            message = EmailMessage(
                to=["recipient@example.com"],
                subject="Sender Refused Test",
                body="Body"
            )

            with pytest.raises(EmailServiceError, match="Sender address refused"):
                email_service.send_email(message)

    @pytest.mark.unit
    def test_send_email_data_error(self, email_service):
        """测试邮件数据错误"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.sendmail.side_effect = smtplib.SMTPDataError(550, "Data error")
            mock_smtp.return_value = mock_conn

            email_service.connect()

            message = EmailMessage(
                to=["recipient@example.com"],
                subject="Data Error Test",
                body="Body"
            )

            with pytest.raises(EmailServiceError, match="Message data refused"):
                email_service.send_email(message)

    @pytest.mark.unit
    def test_send_email_general_error(self, email_service):
        """测试发送邮件时的其他异常"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.sendmail.side_effect = Exception("General error")
            mock_smtp.return_value = mock_conn

            email_service.connect()

            message = EmailMessage(
                to=["recipient@example.com"],
                subject="General Error Test",
                body="Body"
            )

            with pytest.raises(EmailServiceError, match="Failed to send email"):
                email_service.send_email(message)

    @pytest.mark.unit
    def test_send_email_no_connection_available(self, email_service):
        """测试没有可用连接时的错误"""
        # Mock connect方法设置connection为None，触发"无连接"错误
        with patch.object(email_service, 'connect') as mock_connect:
            # 连接方法什么都不做，保持_connection为None
            mock_connect.return_value = None

            message = EmailMessage(
                to=["recipient@example.com"],
                subject="No Connection Test",
                body="Body"
            )

            with pytest.raises(EmailServiceError, match="No SMTP connection available"):
                email_service.send_email(message)

    @pytest.mark.unit
    def test_send_email_attachment_processing_error(self, email_service):
        """测试附件处理错误"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_conn.sendmail.return_value = {}
            mock_smtp.return_value = mock_conn

            email_service.connect()

            # Mock附件处理失败
            email_service.attachment_service.process_attachment.side_effect = Exception("Attachment error")

            attachment = Attachment(path="/path/to/test.txt", type=AttachmentType.LOCAL)

            message = EmailMessage(
                to=["recipient@example.com"],
                subject="Attachment Error Test",
                body="Body",
                attachments=[attachment]
            )

            with pytest.raises(EmailServiceError, match="Failed to process attachment"):
                email_service.send_email(message)


class TestEmailServiceUtility:
    """EmailService 工具方法测试"""

    @pytest.mark.unit
    def test_get_connection_info(self, email_service):
        """测试获取连接信息"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_smtp.return_value = mock_conn

            # 未连接状态
            info = email_service.get_connection_info()
            assert info.provider == "gmail"
            assert info.smtp_server == "smtp.gmail.com"
            assert info.smtp_port == 587
            assert info.use_tls is True
            assert info.use_ssl is False
            assert info.connected is False

            # 已连接状态
            email_service.connect()
            info = email_service.get_connection_info()
            assert info.connected is True

    @pytest.mark.unit
    def test_test_connection_success(self, email_service):
        """测试连接测试成功"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_smtp.return_value = mock_conn

            result = email_service.test_connection()
            assert result is True

            # 验证连接被清理
            assert email_service._connection is None
            email_service.attachment_service.cleanup_temp_files.assert_called_once()

    @pytest.mark.unit
    def test_test_connection_failure(self, email_service):
        """测试连接测试失败"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPConnectError(421, b"Service not available")

            result = email_service.test_connection()
            assert result is False

            # 验证连接被清理
            assert email_service._connection is None
            email_service.attachment_service.cleanup_temp_files.assert_called_once()


class TestEmailServiceValidation:
    """EmailService 验证功能测试"""

    @pytest.mark.unit
    def test_validate_email_format_valid(self):
        """测试有效邮箱格式验证"""
        from email_mcp_server.email_service import validate_email_format

        assert validate_email_format("test@example.com") is True
        assert validate_email_format("user.name@domain.co.uk") is True
        assert validate_email_format("user+tag@example.org") is True

    @pytest.mark.unit
    def test_validate_email_format_invalid(self):
        """测试无效邮箱格式验证"""
        from email_mcp_server.email_service import validate_email_format

        assert validate_email_format("invalid-email") is False
        assert validate_email_format("@example.com") is False
        assert validate_email_format("test@") is False
        assert validate_email_format("test.example.com") is False
        assert validate_email_format("") is False

    @pytest.mark.unit
    def test_validate_email_address_valid(self):
        """测试有效邮箱地址验证"""
        from email_mcp_server.email_service import validate_email_address

        # 应该不抛出异常
        validate_email_address("test@example.com")
        validate_email_address("user@domain.org")

    @pytest.mark.unit
    def test_validate_email_address_invalid(self):
        """测试无效邮箱地址验证"""
        from email_mcp_server.email_service import validate_email_address

        with pytest.raises(ValidationError):
            validate_email_address("")

        with pytest.raises(ValidationError):
            validate_email_address("invalid-email")

    @pytest.mark.unit
    def test_validate_multiple_emails_valid(self):
        """测试验证多个有效邮箱地址"""
        from email_mcp_server.email_service import validate_multiple_emails

        emails = ["user1@example.com", "user2@example.org"]
        # 应该不抛出异常
        validate_multiple_emails(emails)

    @pytest.mark.unit
    def test_validate_multiple_emails_invalid(self):
        """测试验证包含无效地址的邮箱列表"""
        from email_mcp_server.email_service import validate_multiple_emails

        # 空列表
        with pytest.raises(ValidationError):
            validate_multiple_emails([])

        # 包含无效地址
        with pytest.raises(ValidationError):
            validate_multiple_emails(["valid@example.com", "invalid-email"])


if __name__ == "__main__":
    # 可以直接运行这个测试文件
    pytest.main([__file__, "-v"])