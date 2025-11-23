"""测试数据工厂 - 统一管理测试数据"""

from typing import Dict, Any, Optional
from email_mcp_server.models import (
    EmailMessage,
    Attachment,
    AttachmentType,
    SendEmailToolRequest,
    AttachmentResult
)


class TestDataFactory:
    """测试数据工厂类，统一创建各种测试对象"""

    @staticmethod
    def create_email_settings_mock() -> Dict[str, Any]:
        """创建邮箱设置Mock"""
        return {
            "address": "test@example.com",
            "password": "test_password",
            "provider": "gmail",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "use_tls": True,
            "use_ssl": False
        }

    @staticmethod
    def create_app_settings_mock() -> Dict[str, Any]:
        """创建应用设置Mock"""
        return {
            "log_level": "INFO",
            "log_file": None,
            "max_attachment_size": 25 * 1024 * 1024,  # 25MB
            "temp_dir": "temp",
            "download_timeout": 30,
            "max_retries": 3,
            "require_confirmation": False
        }

    @staticmethod
    def create_email_message(**kwargs) -> EmailMessage:
        """创建邮件消息对象"""
        defaults = {
            "to": ["recipient@example.com"],
            "subject": "Test Email",
            "body": "This is a test email body",
            "html_body": "<p>This is a test email body in HTML</p>",
            "cc": None,
            "bcc": None,
            "attachments": None,
            "reply_to": None,
            "priority": 3
        }
        defaults.update(kwargs)

        return EmailMessage(**defaults)

    @staticmethod
    def create_send_email_request(**kwargs) -> SendEmailToolRequest:
        """创建发送邮件请求对象"""
        defaults = {
            "to": ["recipient@example.com"],
            "subject": "Test Subject",
            "body": "Test body content",
            "html_body": "<p>Test HTML content</p>",
            "cc": None,
            "bcc": None,
            "attachments": None,
            "reply_to": None,
            "priority": 3
        }
        defaults.update(kwargs)

        return SendEmailToolRequest(**defaults)

    @staticmethod
    def create_attachment(path: str, attachment_type: AttachmentType, **kwargs) -> Attachment:
        """创建附件对象"""
        defaults = {
            "path": path,
            "type": attachment_type,
            "filename": None,
            "content_type": None,
            "size": None
        }
        defaults.update(kwargs)

        return Attachment(**defaults)

    @staticmethod
    def create_local_attachment(path: str = "/path/to/local/file.txt", **kwargs) -> Attachment:
        """创建本地附件对象"""
        return TestDataFactory.create_attachment(path, AttachmentType.LOCAL, **kwargs)

    @staticmethod
    def create_remote_attachment(url: str = "https://example.com/file.pdf", **kwargs) -> Attachment:
        """创建远程附件对象"""
        return TestDataFactory.create_attachment(url, AttachmentType.REMOTE, **kwargs)

    @staticmethod
    def create_attachment_result(**kwargs) -> AttachmentResult:
        """创建附件结果对象"""
        defaults = {
            "filename": "test_file.txt",
            "content_type": "text/plain",
            "data": b"Test file content for testing purposes",
            "size": 41,
            "is_temp": False
        }
        defaults.update(kwargs)

        return AttachmentResult(**defaults)

    @staticmethod
    def create_local_attachment_result(**kwargs) -> AttachmentResult:
        """创建本地附件结果对象"""
        defaults = {
            "filename": "local_file.txt",
            "content_type": "text/plain",
            "data": b"Local file content for testing",
            "size": 30,
            "is_temp": False
        }
        defaults.update(kwargs)
        return TestDataFactory.create_attachment_result(**defaults)

    @staticmethod
    def create_remote_attachment_result(**kwargs) -> AttachmentResult:
        """创建远程附件结果对象"""
        defaults = {
            "filename": "remote_file.pdf",
            "content_type": "application/pdf",
            "data": b"PDF file content for testing purposes",
            "size": 38,
            "is_temp": True
        }
        defaults.update(kwargs)
        return TestDataFactory.create_attachment_result(**defaults)

    @staticmethod
    def create_complex_email_message() -> EmailMessage:
        """创建复杂邮件消息（包含所有字段）"""
        return TestDataFactory.create_email_message(
            to=["user1@example.com", "user2@example.com"],
            subject="Complex Test Email with All Features",
            body="This is a complex test email with all features enabled",
            html_body="<h1>Complex Test Email</h1><p>This email contains all features.</p>",
            cc=["cc1@example.com", "cc2@example.com"],
            bcc=["bcc@example.com"],
            attachments=[
                TestDataFactory.create_local_attachment("/path/to/file1.txt"),
                TestDataFactory.create_remote_attachment("https://example.com/file2.pdf")
            ],
            reply_to="reply@example.com",
            priority=1
        )

    @staticmethod
    def create_test_emails_list() -> Dict[str, str]:
        """创建测试邮箱地址列表"""
        return {
            "valid_single": "test@example.com",
            "valid_multiple": ["user1@example.com", "user2@example.org", "user3@example.net"],
            "valid_with_tags": "user+tag@example.com",
            "valid_subdomain": "user@mail.example.com",
            "invalid_format": "invalid-email",
            "missing_domain": "test@",
            "missing_user": "@example.com",
            "empty": ""
        }

    @staticmethod
    def create_error_test_data() -> Dict[str, Any]:
        """创建错误测试数据"""
        return {
            "network_errors": [
                "Connection timeout",
                "DNS resolution failed",
                "Server not responding"
            ],
            "auth_errors": [
                "Authentication failed (535)",
                "Authentication required (530)",
                "Invalid credentials"
            ],
            "smtp_errors": [
                "Recipients refused",
                "Sender refused",
                "Message data refused",
                "Service not available"
            ]
        }