"""Email MCP tools using FastMCP decorators."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from .email_service import (
    EmailService,
    validate_email_address,
    validate_multiple_emails,
)
from .exceptions import EmailMCPServerError, format_error_response
from .logging_config import get_logger
from .models import (
    Attachment,
    EmailMessage,
    SendEmailResponse,
)

logger = get_logger(__name__)


def register_email_tools(mcp: FastMCP) -> None:
    """注册邮件相关工具到 FastMCP 服务器."""

    @mcp.tool(
        name="send_email",
        title="发送邮件",
        description="发送邮件给指定的收件人，支持HTML内容、附件和多种邮件选项"
    )
    async def send_email(
        to: list[str],
        subject: str,
        body: str | None = None,
        html_body: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        attachments: list[str] | None = None,
        reply_to: str | None = None,
        priority: int = 3,
    ) -> dict[str, Any]:
        """
        发送邮件工具

        Args:
            to: 收件人邮箱列表，必须提供至少一个有效的邮箱地址
            subject: 邮件主题，不能为空
            body: 邮件正文（纯文本格式）
            html_body: 邮件正文（HTML格式）
            cc: 抄送邮箱列表
            bcc: 密送邮箱列表
            attachments: 附件路径列表，支持本地文件路径或远程URL
            reply_to: 回复邮箱地址
            priority: 邮件优先级，范围1-5，1为最高优先级，5为最低优先级

        Returns:
            包含发送结果和详细信息的字典
        """
        try:
            # 验证必需参数
            if not to:
                return {
                    "success": False,
                    "error": "At least one recipient is required",
                    "error_code": "VALIDATION_ERROR"
                }

            if not subject:
                return {
                    "success": False,
                    "error": "Subject is required",
                    "error_code": "VALIDATION_ERROR"
                }

            if not body and not html_body:
                return {
                    "success": False,
                    "error": "Either body or html_body is required",
                    "error_code": "VALIDATION_ERROR"
                }

            # 验证邮箱格式
            try:
                validate_multiple_emails(to)
                if cc:
                    validate_multiple_emails(cc)
                if bcc:
                    validate_multiple_emails(bcc)
                if reply_to:
                    validate_email_address(reply_to)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Email validation error: {str(e)}",
                    "error_code": "VALIDATION_ERROR"
                }

            # 处理附件
            attachment_objects = []
            if attachments:
                for att_path in attachments:
                    try:
                        attachment = Attachment.from_path(att_path)
                        attachment_objects.append(attachment)
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Attachment error for {att_path}: {str(e)}",
                            "error_code": "ATTACHMENT_ERROR"
                        }

            # 创建邮件消息
            message = EmailMessage(
                to=to,
                subject=subject,
                body=body,
                html_body=html_body,
                cc=cc,
                bcc=bcc,
                attachments=attachment_objects if attachment_objects else None,
                reply_to=reply_to,
                priority=priority,
            )

            # 发送邮件
            email_service = EmailService()
            try:
                message_id = email_service.send_email(message)

                response = SendEmailResponse(
                    success=True,
                    message_id=message_id,
                    status="sent",
                    error=None,
                    attachments_processed=len(attachment_objects)
                    if attachment_objects
                    else 0,
                )

                return {
                    "success": True,
                    "message": "Email sent successfully!",
                    "message_id": message_id,
                    "recipients_count": len(to),
                    "attachments_processed": response.attachments_processed,
                    "status": "sent"
                }

            finally:
                email_service.disconnect()

        except EmailMCPServerError as e:
            error_response = format_error_response(e)
            return {
                "success": False,
                "error": error_response['error']['detail'],
                "error_code": error_response['error']['code'],
                "error_type": error_response['error']['type']
            }
        except Exception as e:
            logger.error(f"Unexpected error in send_email: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "UNKNOWN_ERROR"
            }

    @mcp.tool(
        name="check_email_config",
        title="检查邮箱配置",
        description="检查当前邮箱配置状态和连接测试"
    )
    async def check_email_config() -> dict[str, Any]:
        """
        检查邮箱配置状态工具

        Returns:
            包含邮箱配置信息和连接测试结果的字典
        """
        try:
            from .config import get_email_settings
            email_settings = get_email_settings()
            email_service = EmailService()

            # 测试连接
            connection_test = email_service.test_connection()
            connection_info = email_service.get_connection_info()

            return {
                "success": True,
                "configured": True,
                "provider": email_settings.provider.value,
                "smtp_server": connection_info.get("smtp_server"),
                "smtp_port": connection_info.get("smtp_port"),
                "use_tls": connection_info.get("use_tls"),
                "use_ssl": connection_info.get("use_ssl"),
                "connection_test": connection_test,
                "connected": connection_info.get("connected", False),
                "message": "Email configuration checked successfully"
            }

        except EmailMCPServerError as e:
            error_response = format_error_response(e)
            return {
                "success": False,
                "configured": False,
                "error": error_response['error']['detail'],
                "error_code": error_response['error']['code'],
                "error_type": error_response['error']['type']
            }
        except Exception as e:
            logger.error(f"Unexpected error in check_email_config: {e}")
            return {
                "success": False,
                "configured": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "UNKNOWN_ERROR"
            }

    @mcp.tool(
        name="validate_email",
        title="验证邮箱地址",
        description="验证单个邮箱地址的格式是否正确"
    )
    async def validate_email(email: str) -> dict[str, Any]:
        """
        验证邮箱地址格式工具

        Args:
            email: 要验证的邮箱地址字符串

        Returns:
            包含验证结果的字典
        """
        try:
            validate_email_address(email)
            return {
                "success": True,
                "valid": True,
                "email": email,
                "message": f"Email address '{email}' is valid"
            }
        except Exception as e:
            return {
                "success": True,
                "valid": False,
                "email": email,
                "message": f"Email address '{email}' is invalid: {str(e)}",
                "error": str(e)
            }

    @mcp.tool(
        name="get_supported_providers",
        title="获取支持的邮箱提供商",
        description="获取当前支持的邮箱服务提供商信息"
    )
    async def get_supported_providers() -> dict[str, Any]:
        """
        获取支持的邮箱服务提供商信息工具

        Returns:
            包含支持提供商信息和使用指南的字典
        """
        providers_info = {
            "success": True,
            "supported_providers": [
                {
                    "name": "QQ Mail",
                    "domain": "qq.com",
                    "smtp_server": "smtp.qq.com",
                    "smtp_port": 587,
                    "security": "TLS",
                    "auth_required": "Authorization code (not password)",
                    "setup_notes": "Enable SMTP service in QQ Mail settings and get authorization code"
                },
                {
                    "name": "Gmail",
                    "domain": "gmail.com",
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "security": "TLS",
                    "auth_required": "App-specific password (not regular password)",
                    "setup_notes": "Enable 2-step verification and generate app-specific password"
                }
            ],
            "configuration": {
                "environment_variables": [
                    "EMAIL_ADDRESS - Your email address",
                    "EMAIL_PASSWORD - Your password/authorization code"
                ],
                "auto_detection": "SMTP settings are auto-detected based on email domain",
                "manual_config": "Manual SMTP configuration is also supported via environment variables"
            },
            "setup_steps": [
                "Enable SMTP service in your email provider",
                "Generate authorization code/app password",
                "Configure environment variables",
                "Test connection with check_email_config tool"
            ]
        }

        return providers_info

    logger.info("Email tools registered successfully")
