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


class SMTPConfig(BaseModel):
    """SMTP 服务器配置."""

    server: str
    port: int
    use_tls: bool = True
    use_ssl: bool = False


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


class EmailStatusResponse(BaseModel):
    """邮件状态响应模型."""

    configured: bool = Field(..., description="是否已配置邮箱")
    provider: str | None = Field(None, description="邮箱提供商")
    smtp_config: SMTPConfig | None = Field(None, description="SMTP配置（隐藏敏感信息）")
    test_connection: bool | None = Field(None, description="连接测试结果")
