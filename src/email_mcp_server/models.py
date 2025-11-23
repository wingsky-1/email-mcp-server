"""Data models for the Email MCP Server."""

from enum import Enum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pydantic
from pydantic import BaseModel, Field, field_validator


class AttachmentType(str, Enum):
    """附件类型."""

    LOCAL = "local"
    REMOTE = "remote"


class AttachmentResult(BaseModel):
    """附件处理结果模型."""

    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="MIME类型")
    data: bytes = Field(..., description="文件数据")
    size: int = Field(..., description="文件大小（字节）")
    is_temp: bool = Field(..., description="是否为临时文件")


class SMTPConfig(BaseModel):
    """SMTP 服务器配置."""

    server: str
    port: int
    use_tls: bool = True
    use_ssl: bool = False


class ConnectionInfo(BaseModel):
    """连接信息模型."""

    provider: str = Field(..., description="邮箱提供商")
    smtp_server: str = Field(..., description="SMTP服务器")
    smtp_port: int = Field(..., description="SMTP端口")
    use_tls: bool = Field(..., description="是否使用TLS")
    use_ssl: bool = Field(..., description="是否使用SSL")
    connected: bool = Field(..., description="是否已连接")


class Attachment(BaseModel):
    """附件模型."""

    path: str
    type: AttachmentType
    filename: str | None = None
    content_type: str | None = None
    size: int | None = None

    @classmethod
    def from_path(cls, path: str) -> Attachment:
        """从路径创建附件对象."""
        if path.startswith(("http://", "https://")):
            return cls(path=path, type=AttachmentType.REMOTE)
        else:
            return cls(path=path, type=AttachmentType.LOCAL)

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str, info: pydantic.ValidationInfo) -> str:
        """验证路径格式."""
        attachment_type = info.data.get("type")

        if attachment_type == AttachmentType.LOCAL:
            # 验证本地路径格式
            try:
                path_obj = Path(v)
                if not path_obj.is_absolute():
                    raise ValueError("Local file path must be absolute")
            except Exception as e:
                raise ValueError(f"Invalid local file path: {e}") from e

        elif attachment_type == AttachmentType.REMOTE:
            # 验证URL格式
            try:
                parsed = urlparse(v)
                if not parsed.scheme or not parsed.netloc:
                    raise ValueError("Invalid URL format")
            except Exception as e:
                raise ValueError(f"Invalid remote URL: {e}") from e

        return v


class EmailMessage(BaseModel):
    """邮件消息模型."""

    to: list[str] = Field(..., description="收件人邮箱列表")
    subject: str = Field(..., description="邮件主题")
    body: str | None = Field(None, description="邮件正文")
    html_body: str | None = Field(None, description="HTML格式的邮件正文")
    cc: list[str] | None = Field(None, description="抄送邮箱列表")
    bcc: list[str] | None = Field(None, description="密送邮箱列表")
    attachments: list[Attachment] | None = Field(None, description="附件列表")
    reply_to: str | None = Field(None, description="回复邮箱")
    priority: int | None = Field(3, description="邮件优先级 (1-5)", ge=1, le=5)

    @field_validator("to")
    @classmethod
    def validate_recipients(cls, v: list[str]) -> list[str]:
        """验证收件人邮箱格式."""
        if not v:
            raise ValueError("At least one recipient is required")

        validated_emails: list[str] = []
        for email in v:
            if not cls._is_valid_email(email):
                raise ValueError(f"Invalid email address: {email}")
            validated_emails.append(email.lower())

        return validated_emails

    @field_validator("cc")
    @classmethod
    def validate_cc(cls, v: list[str] | None) -> list[str] | None:
        """验证抄送邮箱格式."""
        if v is None:
            return None

        validated_emails: list[str] = []
        for email in v:
            if not cls._is_valid_email(email):
                raise ValueError(f"Invalid CC email address: {email}")
            validated_emails.append(email.lower())

        return validated_emails

    @field_validator("bcc")
    @classmethod
    def validate_bcc(cls, v: list[str] | None) -> list[str] | None:
        """验证密送邮箱格式."""
        if v is None:
            return None

        validated_emails: list[str] = []
        for email in v:
            if not cls._is_valid_email(email):
                raise ValueError(f"Invalid BCC email address: {email}")
            validated_emails.append(email.lower())

        return validated_emails

    @field_validator("reply_to")
    @classmethod
    def validate_reply_to(cls, v: str | None) -> str | None:
        """验证回复邮箱格式."""
        if v is None:
            return None

        if not cls._is_valid_email(v):
            raise ValueError(f"Invalid reply-to email address: {v}")

        return v.lower()

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """验证邮箱地址格式."""
        try:
            local, domain = email.rsplit("@", 1)
            if not local or not domain:
                return False

            # 简单的邮箱格式验证
            if len(local) > 64 or len(domain) > 255:
                return False

            # 检查域名是否包含点
            return "." in domain
        except ValueError:
            return False

    def has_attachments(self) -> bool:
        """检查是否包含附件."""
        return bool(self.attachments)

    def get_total_attachments_size(self) -> int:
        """获取附件总大小."""
        if not self.attachments:
            return 0

        total_size = 0
        for attachment in self.attachments:
            if attachment.size:
                total_size += attachment.size

        return total_size


class SendEmailRequest(BaseModel):
    """发送邮件请求模型."""

    message: EmailMessage = Field(..., description="邮件消息")
    require_confirmation: bool | None = Field(None, description="是否需要确认")
    timeout: int | None = Field(None, description="超时时间（秒）")


class SendEmailToolRequest(BaseModel):
    """MCP 发送邮件工具请求模型."""

    to: list[str] = Field(..., description="收件人邮箱列表", min_length=1)
    subject: str = Field(..., description="邮件主题", min_length=1)
    body: str | None = Field(None, description="邮件正文（纯文本格式）")
    html_body: str | None = Field(None, description="邮件正文（HTML格式）")
    cc: list[str] | None = Field(None, description="抄送邮箱列表")
    bcc: list[str] | None = Field(None, description="密送邮箱列表")
    attachments: list[str] | None = Field(None, description="附件路径列表")
    reply_to: str | None = Field(None, description="回复邮箱地址")
    priority: int = Field(default=3, description="邮件优先级", ge=1, le=5)
    require_confirmation: bool | None = Field(
        default=None,
        description="是否需要用户确认发送。None表示使用全局设置，True表示强制要求确认，False表示跳过确认"
    )

    @field_validator("to", "cc", "bcc")
    @classmethod
    def validate_email_lists(cls, v: list[str] | None) -> list[str] | None:
        """验证邮箱列表格式."""
        if v is None:
            return None

        validated_emails: list[str] = []
        for email in v:
            if not email or "@" not in email:
                raise ValueError(f"Invalid email address: {email}")
            validated_emails.append(email.lower())

        return validated_emails

    @field_validator("reply_to")
    @classmethod
    def validate_reply_to(cls, v: str | None) -> str | None:
        """验证回复邮箱格式."""
        if v is None:
            return None

        if not v or "@" not in v:
            raise ValueError(f"Invalid reply-to email address: {v}")

        return v.lower()

    @field_validator("attachments")
    @classmethod
    def validate_attachments(cls, v: list[str] | None) -> list[str] | None:
        """验证附件路径."""
        if v is None:
            return None

        validated_paths: list[str] = []
        for path in v:
            if not path:
                raise ValueError("Attachment path cannot be empty")

            # 基本路径格式验证
            if not (path.startswith(("http://", "https://", "/", "C:", "D:", "E:", "F:", "G:", "H:")) or path.startswith(("./", "../", "\\"))):
                # 相对路径也允许
                pass

            validated_paths.append(path)

        return validated_paths

    def to_email_message(self) -> EmailMessage:
        """转换为 EmailMessage 对象."""
        # 处理附件
        message_attachments = None
        if self.attachments:
            message_attachments = [Attachment.from_path(path) for path in self.attachments]

        return EmailMessage(
            to=self.to,
            subject=self.subject,
            body=self.body,
            html_body=self.html_body,
            cc=self.cc,
            bcc=self.bcc,
            attachments=message_attachments,
            reply_to=self.reply_to,
            priority=self.priority,
        )


class SendEmailResponse(BaseModel):
    """发送邮件响应模型."""

    success: bool = Field(..., description="是否发送成功")
    message_id: str | None = Field(None, description="邮件ID")
    status: str | None = Field(None, description="发送状态")
    error: dict[str, Any] | None = Field(None, description="错误信息")
    attachments_processed: int | None = Field(None, description="已处理的附件数量")


class EmailConfirmationRequest(BaseModel):
    """邮件确认请求模型."""

    message: EmailMessage = Field(..., description="待确认的邮件消息")
    summary: str = Field(..., description="邮件摘要")


class EmailConfirmationResponse(BaseModel):
    """邮件确认响应模型."""

    confirmed: bool = Field(..., description="是否确认发送")
    message: str | None = Field(None, description="用户消息")


class EmailValidationResponse(BaseModel):
    """邮箱验证响应模型."""

    success: bool = Field(..., description="操作是否成功")
    valid: bool = Field(..., description="邮箱地址是否有效")
    email: str = Field(..., description="验证的邮箱地址")
    message: str = Field(..., description="验证结果消息")


class ProviderInfo(BaseModel):
    """邮箱提供商信息模型."""

    name: str = Field(..., description="提供商名称")
    domain: str = Field(..., description="域名")
    smtp_server: str = Field(..., description="SMTP服务器地址")
    smtp_port: int = Field(..., description="SMTP端口")
    security: str = Field(..., description="安全类型")
    auth_required: str = Field(..., description="认证要求")
    setup_notes: str = Field(..., description="设置说明")


class SupportedProvidersResponse(BaseModel):
    """支持的邮箱提供商响应模型."""

    success: bool = Field(..., description="操作是否成功")
    supported_providers: list[ProviderInfo] = Field(..., description="支持的提供商列表")


class EmailValidationRequest(BaseModel):
    """邮箱验证请求模型."""

    email: str = Field(..., description="要验证的邮箱地址", min_length=1)


class CheckEmailConfigRequest(BaseModel):
    """检查邮箱配置请求模型."""
    pass  # 无需参数


class GetSupportedProvidersRequest(BaseModel):
    """获取支持的提供商请求模型."""
    pass  # 无需参数


class EmailStatusResponse(BaseModel):
    """邮件状态响应模型."""

    configured: bool = Field(..., description="是否已配置邮箱")
    provider: str | None = Field(None, description="邮箱提供商")
    smtp_config: SMTPConfig | None = Field(None, description="SMTP配置（隐藏敏感信息）")
    test_connection: bool | None = Field(None, description="连接测试结果")
