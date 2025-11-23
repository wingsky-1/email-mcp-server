"""测试 Pydantic 模型"""

import pytest
from pydantic import ValidationError

from email_mcp_server.models import (
    Attachment,
    AttachmentType,
    ConnectionInfo,
    EmailMessage,
    EmailValidationRequest,
    EmailValidationResponse,
    ProviderInfo,
    SendEmailToolRequest,
    SMTPConfig,
    SupportedProvidersResponse,
)


class TestSendEmailToolRequest:
    """测试 SendEmailToolRequest 模型"""

    @pytest.mark.unit
    def test_valid_request_creation(self):
        """测试有效的请求创建"""
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test Body"
        )

        assert request.to == ["test@example.com"]
        assert request.subject == "Test Subject"
        assert request.body == "Test Body"
        assert request.html_body is None
        assert request.cc is None
        assert request.bcc is None
        assert request.attachments is None
        assert request.reply_to is None
        assert request.priority == 3

    @pytest.mark.unit
    def test_min_length_validation(self):
        """测试字段最小长度验证"""
        with pytest.raises(ValidationError) as exc_info:
            SendEmailToolRequest(to=[], subject="")  # 空列表和空主题

        assert "to" in str(exc_info.value)
        assert "subject" in str(exc_info.value)

    @pytest.mark.unit
    def test_email_list_validation_valid(self):
        """测试有效邮箱列表验证"""
        request = SendEmailToolRequest(
            to=["user1@example.com", "user2@example.com"],
            subject="Test",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"]
        )

        assert request.to == ["user1@example.com", "user2@example.com"]
        assert request.cc == ["cc@example.com"]
        assert request.bcc == ["bcc@example.com"]

    @pytest.mark.unit
    def test_email_list_validation_invalid(self):
        """测试无效邮箱列表验证"""
        with pytest.raises(ValidationError) as exc_info:
            SendEmailToolRequest(
                to=["invalid-email", "user2@example.com"],
                subject="Test"
            )

        assert "Invalid email address: invalid-email" in str(exc_info.value)

    @pytest.mark.unit
    def test_email_list_normalization(self):
        """测试邮箱地址标准化"""
        request = SendEmailToolRequest(
            to=["User@EXAMPLE.COM", "user2@Example.Com"],
            subject="Test"
        )

        assert request.to == ["user@example.com", "user2@example.com"]

    @pytest.mark.unit
    def test_reply_to_validation_valid(self):
        """测试有效的回复邮箱验证"""
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test",
            reply_to="reply@example.com"
        )

        assert request.reply_to == "reply@example.com"

    @pytest.mark.unit
    def test_reply_to_validation_invalid(self):
        """测试无效的回复邮箱验证"""
        with pytest.raises(ValidationError) as exc_info:
            SendEmailToolRequest(
                to=["test@example.com"],
                subject="Test",
                reply_to="invalid-email"
            )

        assert "Invalid reply-to email address: invalid-email" in str(exc_info.value)

    @pytest.mark.unit
    def test_reply_to_normalization(self):
        """测试回复邮箱标准化"""
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test",
            reply_to="REPLY@EXAMPLE.COM"
        )

        assert request.reply_to == "reply@example.com"

    @pytest.mark.unit
    def test_priority_validation(self):
        """测试优先级验证"""
        # 有效范围 1-5
        SendEmailToolRequest(to=["test@example.com"], subject="Test", priority=1)
        SendEmailToolRequest(to=["test@example.com"], subject="Test", priority=5)

        # 超出范围
        with pytest.raises(ValidationError):
            SendEmailToolRequest(to=["test@example.com"], subject="Test", priority=0)

        with pytest.raises(ValidationError):
            SendEmailToolRequest(to=["test@example.com"], subject="Test", priority=6)

    @pytest.mark.unit
    def test_attachments_validation_valid(self):
        """测试有效附件路径验证"""
        attachments = [
            "/path/to/file.txt",
            "http://example.com/file.pdf",
            "https://example.com/image.jpg",
            "./relative/file.txt",
            "../parent/file.txt"
        ]

        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test",
            attachments=attachments
        )

        assert request.attachments == attachments

    @pytest.mark.unit
    def test_attachments_validation_empty(self):
        """测试空附件路径验证"""
        with pytest.raises(ValidationError) as exc_info:
            SendEmailToolRequest(
                to=["test@example.com"],
                subject="Test",
                attachments=["", "valid/path"]
            )

        assert "Attachment path cannot be empty" in str(exc_info.value)

    @pytest.mark.unit
    def test_to_email_message_conversion(self):
        """测试转换为 EmailMessage"""
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test Body",
            html_body="<h1>Test HTML</h1>",
            cc=["cc@example.com"],
            reply_to="reply@example.com",
            priority=1,
            attachments=["test.txt"]
        )

        message = request.to_email_message()

        assert message.to == ["test@example.com"]
        assert message.subject == "Test Subject"
        assert message.body == "Test Body"
        assert message.html_body == "<h1>Test HTML</h1>"
        assert message.cc == ["cc@example.com"]
        assert message.reply_to == "reply@example.com"
        assert message.priority == 1
        assert message.attachments is not None
        assert len(message.attachments) == 1
        assert message.attachments[0].path == "test.txt"

    @pytest.mark.unit
    def test_to_email_message_no_attachments(self):
        """测试无附件时转换为 EmailMessage"""
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test",
            body="Test Body"
        )

        message = request.to_email_message()

        assert message.attachments is None


class TestEmailValidationRequest:
    """测试 EmailValidationRequest 模型"""

    @pytest.mark.unit
    def test_valid_email(self):
        """测试有效邮箱"""
        request = EmailValidationRequest(email="test@example.com")
        assert request.email == "test@example.com"

    @pytest.mark.unit
    def test_min_length_validation(self):
        """测试最小长度验证"""
        with pytest.raises(ValidationError) as exc_info:
            EmailValidationRequest(email="")

        assert "String should have at least 1 character" in str(exc_info.value)


class TestAttachmentModel:
    """测试 Attachment 模型"""

    @pytest.mark.unit
    def test_local_attachment(self):
        """测试本地附件模型"""
        attachment = Attachment(
            path="/path/to/file.pdf",
            type=AttachmentType.LOCAL
        )

        assert attachment.path == "/path/to/file.pdf"
        assert attachment.type == AttachmentType.LOCAL
        assert attachment.filename is None
        assert attachment.content_type is None
        assert attachment.size is None

    @pytest.mark.unit
    def test_remote_attachment(self):
        """测试远程附件模型"""
        attachment = Attachment(
            path="https://example.com/file.pdf",
            type=AttachmentType.REMOTE
        )

        assert attachment.path == "https://example.com/file.pdf"
        assert attachment.type == AttachmentType.REMOTE

    @pytest.mark.unit
    def test_from_path_local(self):
        """测试从路径创建本地附件"""
        attachment = Attachment.from_path("/path/to/file.txt")
        assert attachment.path == "/path/to/file.txt"
        assert attachment.type == AttachmentType.LOCAL

    @pytest.mark.unit
    def test_from_path_remote(self):
        """测试从路径创建远程附件"""
        attachment = Attachment.from_path("https://example.com/file.pdf")
        assert attachment.path == "https://example.com/file.pdf"
        assert attachment.type == AttachmentType.REMOTE

    @pytest.mark.unit
    def test_from_path_http(self):
        """测试 http 协议远程附件"""
        attachment = Attachment.from_path("http://example.com/file.pdf")
        assert attachment.path == "http://example.com/file.pdf"
        assert attachment.type == AttachmentType.REMOTE


class TestEmailMessage:
    """测试 EmailMessage 模型"""

    @pytest.mark.unit
    def test_basic_email_message(self):
        """测试基本邮件消息"""
        message = EmailMessage(
            to=["recipient@example.com"],
            subject="Test Subject"
        )

        assert message.to == ["recipient@example.com"]
        assert message.subject == "Test Subject"
        assert message.body is None
        assert message.html_body is None
        assert message.cc is None
        assert message.bcc is None
        assert message.attachments is None
        assert message.reply_to is None
        assert message.priority == 3

    @pytest.mark.unit
    def test_complete_email_message(self):
        """测试完整邮件消息"""
        attachment = Attachment.from_path("/path/to/file.pdf")
        message = EmailMessage(
            to=["recipient@example.com"],
            subject="Test Subject",
            body="Plain text body",
            html_body="<h1>HTML Body</h1>",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            attachments=[attachment],
            reply_to="reply@example.com",
            priority=1
        )

        assert message.to == ["recipient@example.com"]
        assert message.subject == "Test Subject"
        assert message.body == "Plain text body"
        assert message.html_body == "<h1>HTML Body</h1>"
        assert message.cc == ["cc@example.com"]
        assert message.bcc == ["bcc@example.com"]
        assert message.attachments == [attachment]
        assert message.reply_to == "reply@example.com"
        assert message.priority == 1

    @pytest.mark.unit
    def test_empty_recipients(self):
        """测试空收件人列表"""
        with pytest.raises(ValidationError) as exc_info:
            EmailMessage(subject="Test")

        assert "Field required" in str(exc_info.value)

    @pytest.mark.unit
    def test_invalid_email_in_recipients(self):
        """测试收件人中包含无效邮箱"""
        with pytest.raises(ValidationError) as exc_info:
            EmailMessage(
                to=["valid@example.com", "invalid-email"],
                subject="Test"
            )

        assert "Invalid email address: invalid-email" in str(exc_info.value)

    @pytest.mark.unit
    def test_has_attachments_method(self):
        """测试 has_attachments 方法"""
        # 无附件
        message_no_attachments = EmailMessage(
            to=["test@example.com"],
            subject="Test"
        )
        assert not message_no_attachments.has_attachments()

        # 有附件
        attachment = Attachment.from_path("/path/to/file.pdf")
        message_with_attachments = EmailMessage(
            to=["test@example.com"],
            subject="Test",
            attachments=[attachment]
        )
        assert message_with_attachments.has_attachments()

    @pytest.mark.unit
    def test_get_total_attachments_size(self):
        """测试获取附件总大小"""
        # 无附件
        message_no_attachments = EmailMessage(
            to=["test@example.com"],
            subject="Test"
        )
        assert message_no_attachments.get_total_attachments_size() == 0

        # 有附件
        attachment1 = Attachment.from_path("/path/to/file1.pdf")
        attachment1.size = 1024
        attachment2 = Attachment.from_path("/path/to/file2.pdf")
        attachment2.size = 2048
        message_with_attachments = EmailMessage(
            to=["test@example.com"],
            subject="Test",
            attachments=[attachment1, attachment2]
        )
        assert message_with_attachments.get_total_attachments_size() == 3072

        # 附件大小为 None
        attachment_no_size = Attachment.from_path("/path/to/file3.pdf")
        message_mixed_sizes = EmailMessage(
            to=["test@example.com"],
            subject="Test",
            attachments=[attachment1, attachment_no_size]
        )
        assert message_mixed_sizes.get_total_attachments_size() == 1024


class TestConnectionInfo:
    """测试 ConnectionInfo 模型"""

    @pytest.mark.unit
    def test_connection_info_creation(self):
        """测试连接信息创建"""
        info = ConnectionInfo(
            provider="gmail",
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            use_tls=True,
            use_ssl=False,
            connected=False
        )

        assert info.provider == "gmail"
        assert info.smtp_server == "smtp.gmail.com"
        assert info.smtp_port == 587
        assert info.use_tls is True
        assert info.use_ssl is False
        assert info.connected is False


class TestSMTPConfig:
    """测试 SMTPConfig 模型"""

    @pytest.mark.unit
    def test_smtp_config_creation(self):
        """测试 SMTP 配置创建"""
        config = SMTPConfig(
            server="smtp.gmail.com",
            port=587,
            use_tls=True,
            use_ssl=False
        )

        assert config.server == "smtp.gmail.com"
        assert config.port == 587
        assert config.use_tls is True
        assert config.use_ssl is False

    @pytest.mark.unit
    def test_smtp_config_defaults(self):
        """测试 SMTP 配置默认值"""
        config = SMTPConfig(
            server="smtp.gmail.com",
            port=587
        )

        assert config.use_tls is True  # 默认值
        assert config.use_ssl is False  # 默认值


class TestProviderInfo:
    """测试 ProviderInfo 模型"""

    @pytest.mark.unit
    def test_provider_info_creation(self):
        """测试提供商信息创建"""
        provider = ProviderInfo(
            name="Gmail",
            domain="gmail.com",
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            security="TLS",
            auth_required="App-specific password",
            setup_notes="Enable 2-step verification"
        )

        assert provider.name == "Gmail"
        assert provider.domain == "gmail.com"
        assert provider.smtp_server == "smtp.gmail.com"
        assert provider.smtp_port == 587
        assert provider.security == "TLS"
        assert provider.auth_required == "App-specific password"
        assert provider.setup_notes == "Enable 2-step verification"


class TestEmailValidationResponse:
    """测试 EmailValidationResponse 模型"""

    @pytest.mark.unit
    def test_valid_email_response(self):
        """测试有效邮箱响应"""
        response = EmailValidationResponse(
            success=True,
            valid=True,
            email="test@example.com",
            message="Email address is valid"
        )

        assert response.success is True
        assert response.valid is True
        assert response.email == "test@example.com"
        assert response.message == "Email address is valid"

    @pytest.mark.unit
    def test_invalid_email_response(self):
        """测试无效邮箱响应"""
        response = EmailValidationResponse(
            success=True,
            valid=False,
            email="invalid-email",
            message="Email address is invalid: invalid-email"
        )

        assert response.success is True
        assert response.valid is False
        assert response.email == "invalid-email"
        assert response.message == "Email address is invalid: invalid-email"


class TestSupportedProvidersResponse:
    """测试 SupportedProvidersResponse 模型"""

    @pytest.mark.unit
    def test_supported_providers_response(self):
        """测试支持的提供商响应"""
        providers = [
            ProviderInfo(
                name="Gmail",
                domain="gmail.com",
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                security="TLS",
                auth_required="App-specific password",
                setup_notes="Setup notes"
            ),
            ProviderInfo(
                name="QQ Mail",
                domain="qq.com",
                smtp_server="smtp.qq.com",
                smtp_port=587,
                security="TLS",
                auth_required="Authorization code",
                setup_notes="QQ mail setup"
            )
        ]

        response = SupportedProvidersResponse(
            success=True,
            supported_providers=providers
        )

        assert response.success is True
        assert len(response.supported_providers) == 2
        assert response.supported_providers[0].name == "Gmail"
        assert response.supported_providers[1].name == "QQ Mail"


class TestModelsEdgeCases:
    """测试模型边界条件和异常场景"""

    @pytest.mark.unit
    def test_email_message_extreme_recipients(self):
        """测试极多数量的收件人"""
        # 测试大量收件人
        many_recipients = [f"user{i}@example.com" for i in range(100)]
        message = EmailMessage(
            to=many_recipients,
            subject="Test with many recipients",
            body="Test body"
        )
        assert len(message.to) == 100
        assert all("@example.com" in email for email in message.to)

    @pytest.mark.unit
    def test_email_message_very_long_fields(self):
        """测试非常长的字段"""
        very_long_subject = "A" * 1000  # 1000字符的主题
        very_long_body = "B" * 100000  # 100KB的正文

        message = EmailMessage(
            to=["test@example.com"],
            subject=very_long_subject,
            body=very_long_body
        )

        assert len(message.subject) == 1000
        assert len(message.body) == 100000

    @pytest.mark.unit
    def test_email_message_unicode_content(self):
        """测试Unicode内容"""
        unicode_subject = "测试主题 📧 with émojis"
        unicode_body = "测试内容 with various characters: 中文, русский, العربية, हिन्दी"

        message = EmailMessage(
            to=["test@example.com"],
            subject=unicode_subject,
            body=unicode_body,
            html_body=f"<p>{unicode_body}</p>"
        )

        assert message.subject == unicode_subject
        assert message.body == unicode_body
        assert message.html_body == f"<p>{unicode_body}</p>"

    @pytest.mark.unit
    def test_attachment_edge_cases(self):
        """测试附件边界情况"""
        # 测试非常长的文件路径
        long_path = "/very/long/path/that/exceeds/normal/filesystem/limits/" + "a" * 200 + ".txt"
        attachment = Attachment(path=long_path, type=AttachmentType.LOCAL)

        assert attachment.path == long_path
        assert attachment.type == AttachmentType.LOCAL

        # 测试特殊字符的文件名
        special_chars_url = "https://example.com/file with spaces & symbols.pdf"
        attachment = Attachment(path=special_chars_url, type=AttachmentType.REMOTE)

        assert attachment.path == special_chars_url
        assert attachment.type == AttachmentType.REMOTE

    @pytest.mark.unit
    def test_smtp_config_invalid_combinations(self):
        """测试SMTP配置的无效组合"""
        # TLS和SSL不应该同时为True（虽然在某些情况下可能技术上行得通）
        config = SMTPConfig(
            server="smtp.example.com",
            port=587,
            use_tls=True,
            use_ssl=True  # 这种组合虽然可能，但通常不建议
        )

        assert config.use_tls is True
        assert config.use_ssl is True

    @pytest.mark.unit
    def test_send_email_tool_request_all_fields(self):
        """测试包含所有字段的邮件发送请求"""
        many_recipients = [f"user{i}@example.com" for i in range(10)]
        many_cc = [f"cc{i}@example.com" for i in range(5)]
        many_bcc = [f"bcc{i}@example.com" for i in range(3)]
        many_attachments = [
            f"https://example.com/file{i}.pdf" for i in range(20)
        ]

        request = SendEmailToolRequest(
            to=many_recipients,
            subject="Complex email with all fields",
            body="Email body",
            html_body="<h1>HTML Body</h1>",
            cc=many_cc,
            bcc=many_bcc,
            reply_to="reply@example.com",
            priority=1,
            attachments=many_attachments
        )

        assert len(request.to) == 10
        assert len(request.cc) == 5
        assert len(request.bcc) == 3
        assert len(request.attachments) == 20
        assert request.priority == 1

    @pytest.mark.unit
    def test_email_message_special_characters_in_emails(self):
        """测试邮箱地址中的特殊字符"""
        # 测试各种合法的特殊字符
        valid_emails = [
            "user+tag@example.com",
            "user.name@example.com",
            "user_name@example.com",
            "user-name@example.com",
            "user123@example.com",
            "test.email+tag@example.co.uk"
        ]

        message = EmailMessage(to=valid_emails, subject="Test", body="Body")
        assert message.to == valid_emails

    @pytest.mark.unit
    def test_attachment_size_calculation_edge_cases(self):
        """测试附件大小计算的边界情况"""
        # 测试零字节附件
        zero_size_attachment = Attachment.from_path("/path/to/zero.txt")
        zero_size_attachment.size = 0

        message = EmailMessage(
            to=["test@example.com"],
            subject="Test",
            body="Body",
            attachments=[zero_size_attachment]
        )

        assert message.get_total_attachments_size() == 0

        # 测试大小为None的附件
        unknown_size_attachment = Attachment.from_path("/path/to/unknown.txt")
        unknown_size_attachment.size = None

        message = EmailMessage(
            to=["test@example.com"],
            subject="Test",
            body="Body",
            attachments=[unknown_size_attachment]
        )

        assert message.get_total_attachments_size() == 0

    @pytest.mark.unit
    def test_model_field_type_validation(self):
        """测试模型字段类型验证"""
        # 测试错误的类型应该被Pydantic拒绝
        with pytest.raises(ValidationError):
            SendEmailToolRequest(
                to=123,  # 应该是列表
                subject="Test",
                body="Body"
            )

        with pytest.raises(ValidationError):
            EmailMessage(
                to="not_a_list@example.com",  # 应该是列表
                subject="Test",
                body="Body"
            )

    @pytest.mark.unit
    def test_connection_info_all_fields(self):
        """测试连接信息所有字段"""
        info = ConnectionInfo(
            provider="custom",
            smtp_server="smtp.custom.com",
            smtp_port=465,
            use_tls=False,
            use_ssl=True,
            connected=True
        )

        assert info.provider == "custom"
        assert info.smtp_server == "smtp.custom.com"
        assert info.smtp_port == 465
        assert info.use_tls is False
        assert info.use_ssl is True
        assert info.connected is True

    @pytest.mark.unit
    def test_provider_info_all_fields(self):
        """测试提供商信息所有字段"""
        # 所有字段都是必需的
        provider = ProviderInfo(
            name="Test Provider",
            domain="test.com",
            smtp_server="smtp.test.com",
            smtp_port=587,
            security="TLS",
            auth_required="Password",
            setup_notes="Setup instructions"
        )

        assert provider.name == "Test Provider"
        assert provider.domain == "test.com"
        assert provider.smtp_server == "smtp.test.com"
        assert provider.smtp_port == 587
        assert provider.security == "TLS"
        assert provider.auth_required == "Password"
        assert provider.setup_notes == "Setup instructions"
