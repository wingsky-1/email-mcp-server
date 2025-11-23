"""Email MCP tools registration."""


from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from .config import get_email_settings
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
    EmailStatusResponse,
    SendEmailResponse,
)

logger = get_logger(__name__)


def register_email_tools(mcp: FastMCP) -> None:
    """注册邮件相关工具."""

    @mcp.tool()
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
    ) -> TextContent:
        """
        发送邮件

        Args:
            to: 收件人邮箱列表
            subject: 邮件主题
            body: 邮件正文（纯文本）
            html_body: 邮件正文（HTML格式）
            cc: 抄送邮箱列表
            bcc: 密送邮箱列表
            attachments: 附件路径列表（本地路径或远程URL）
            reply_to: 回复邮箱
            priority: 邮件优先级 (1-5, 1=最高, 5=最低)

        Returns:
            发送结果信息
        """
        try:
            # 验证必需参数
            if not to:
                return TextContent(
                    type="text", text="Error: At least one recipient is required"
                )

            if not subject:
                return TextContent(type="text", text="Error: Subject is required")

            if not body and not html_body:
                return TextContent(
                    type="text", text="Error: Either body or html_body is required"
                )

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
                return TextContent(
                    type="text", text=f"Email validation error: {str(e)}"
                )

            # 处理附件
            attachment_objects = []
            if attachments:
                for att_path in attachments:
                    try:
                        attachment = Attachment.from_path(att_path)
                        attachment_objects.append(attachment)
                    except Exception as e:
                        return TextContent(
                            type="text",
                            text=f"Attachment error for {att_path}: {str(e)}",
                        )

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
                    attachments_processed=len(attachment_objects)
                    if attachment_objects
                    else 0,
                )

                return TextContent(
                    type="text",
                    text=f"Email sent successfully!\n\nMessage ID: {message_id}\nRecipients: {len(to)} sent\nAttachments processed: {response.attachments_processed}",
                )

            finally:
                email_service.disconnect()

        except EmailMCPServerError as e:
            error_response = format_error_response(e)
            return TextContent(
                type="text",
                text=f"Email service error: {error_response['error']['detail']}\nError code: {error_response['error']['code']}",
            )
        except Exception as e:
            logger.error(f"Unexpected error in send_email: {e}")
            return TextContent(type="text", text=f"Unexpected error: {str(e)}")

    @mcp.tool()
    async def check_email_config() -> TextContent:
        """
        检查邮箱配置状态

        Returns:
            邮箱配置信息
        """
        try:
            email_settings = get_email_settings()
            email_service = EmailService()

            # 测试连接
            connection_test = email_service.test_connection()
            connection_info = email_service.get_connection_info()

            response = EmailStatusResponse(
                configured=True,
                provider=email_settings.provider.value,
                smtp_config=connection_info,
                test_connection=connection_test,
            )

            result_text = f"""Email Configuration Status:
✅ Configured: Yes
📧 Provider: {response.provider}
🖥️  SMTP Server: {response.smtp_config["smtp_server"]}:{response.smtp_config["smtp_port"]}
🔒 Security: TLS={response.smtp_config["use_tls"]}, SSL={response.smtp_config["use_ssl"]}
🔗 Connection Test: {"✅ Success" if response.test_connection else "❌ Failed"}
"""

            if response.smtp_config["connected"]:
                result_text += "🟢 Status: Connected\n"
            else:
                result_text += "🔴 Status: Disconnected\n"

            return TextContent(type="text", text=result_text)

        except EmailMCPServerError as e:
            error_response = format_error_response(e)
            return TextContent(
                type="text",
                text=f"Configuration error: {error_response['error']['detail']}\nError code: {error_response['error']['code']}",
            )
        except Exception as e:
            logger.error(f"Unexpected error in check_email_config: {e}")
            return TextContent(type="text", text=f"Unexpected error: {str(e)}")

    @mcp.tool()
    async def validate_email(email: str) -> TextContent:
        """
        验证邮箱地址格式

        Args:
            email: 要验证的邮箱地址

        Returns:
            验证结果
        """
        try:
            validate_email_address(email)
            return TextContent(type="text", text=f"✅ Email address '{email}' is valid")
        except Exception as e:
            return TextContent(
                type="text", text=f"❌ Email address '{email}' is invalid: {str(e)}"
            )

    @mcp.tool()
    async def get_supported_providers() -> TextContent:
        """
        获取支持的邮箱服务提供商

        Returns:
            支持的邮箱提供商列表
        """
        providers_info = """
📧 Supported Email Providers:

1. **QQ Mail (@qq.com)**
   - SMTP Server: smtp.qq.com
   - Port: 587 (TLS)
   - Requires: Authorization code (not password)

2. **Gmail (@gmail.com)**
   - SMTP Server: smtp.gmail.com
   - Port: 587 (TLS)
   - Requires: App-specific password (not regular password)

🔧 Configuration:
- Set EMAIL_ADDRESS and EMAIL_PASSWORD in environment variables
- SMTP settings are auto-detected based on email domain
- Manual SMTP configuration is also supported via environment variables

📋 Setup Steps:
1. Enable SMTP service in your email provider
2. Generate authorization code/app password
3. Configure environment variables
4. Test connection with check_email_config tool
"""

        return TextContent(type="text", text=providers_info.strip())
