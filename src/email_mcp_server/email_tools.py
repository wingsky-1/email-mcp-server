"""Email MCP tools using FastMCP decorators."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from .email_service import (
    EmailService,
    validate_email_address,
)
from .exceptions import EmailMCPServerError, format_error_response
from .logging_config import get_logger
from .models import (
    EmailValidationRequest,
    EmailValidationResponse,
    ProviderInfo,
    SendEmailResponse,
    SendEmailToolRequest,
    SupportedProvidersResponse,
)

logger = get_logger(__name__)


def register_email_tools(mcp: FastMCP) -> None:
    """注册邮件相关工具到 FastMCP 服务器."""

    @mcp.tool(
        name="send_email",
        title="发送邮件",
        description="发送邮件给指定的收件人，支持HTML内容、附件和多种邮件选项",
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
            # 使用 Pydantic 模型进行参数校验
            request = SendEmailToolRequest(
                to=to,
                subject=subject,
                body=body,
                html_body=html_body,
                cc=cc,
                bcc=bcc,
                attachments=attachments,
                reply_to=reply_to,
                priority=priority,
            )

            # 验证正文内容
            if not request.body and not request.html_body:
                return {
                    "success": False,
                    "error": "Either body or html_body is required",
                    "error_code": "VALIDATION_ERROR",
                }

            # 转换为 EmailMessage 对象
            message = request.to_email_message()

            # 发送邮件
            email_service = EmailService()
            try:
                message_id = email_service.send_email(message)

                # 计算处理的附件数量
                attachments_count = len(message.attachments) if message.attachments else 0

                response = SendEmailResponse(
                    success=True,
                    message_id=message_id,
                    status="sent",
                    error=None,
                    attachments_processed=attachments_count,
                )

                return {
                    "success": True,
                    "message": "Email sent successfully!",
                    "message_id": message_id,
                    "recipients_count": len(to),
                    "attachments_processed": response.attachments_processed,
                    "status": "sent",
                }

            finally:
                email_service.disconnect()

        except EmailMCPServerError as e:
            error_response = format_error_response(e)
            return {
                "success": False,
                "error": error_response["error"]["detail"],
                "error_code": error_response["error"]["code"],
                "error_type": error_response["error"]["type"],
            }
        except Exception as e:
            logger.error(f"Unexpected error in send_email: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "UNKNOWN_ERROR",
            }

    @mcp.tool(
        name="check_email_config",
        title="检查邮箱配置",
        description="检查当前邮箱配置状态和连接测试",
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
                "smtp_server": connection_info.smtp_server,
                "smtp_port": connection_info.smtp_port,
                "use_tls": connection_info.use_tls,
                "use_ssl": connection_info.use_ssl,
                "connection_test": connection_test,
                "connected": connection_info.connected,
                "message": "Email configuration checked successfully",
            }

        except EmailMCPServerError as e:
            error_response = format_error_response(e)
            return {
                "success": False,
                "configured": False,
                "error": error_response["error"]["detail"],
                "error_code": error_response["error"]["code"],
                "error_type": error_response["error"]["type"],
            }
        except Exception as e:
            logger.error(f"Unexpected error in check_email_config: {e}")
            return {
                "success": False,
                "configured": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "UNKNOWN_ERROR",
            }

    @mcp.tool(
        name="validate_email",
        title="验证邮箱地址",
        description="验证单个邮箱地址的格式是否正确",
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
            # 使用 Pydantic 模型进行参数校验
            request = EmailValidationRequest(email=email)
            validate_email_address(request.email)

            response = EmailValidationResponse(
                success=True,
                valid=True,
                email=request.email,
                message=f"Email address '{request.email}' is valid",
            )
            return response.model_dump()
        except Exception as e:
            response = EmailValidationResponse(
                success=True,
                valid=False,
                email=email,
                message=f"Email address '{email}' is invalid: {str(e)}",
            )
            return response.model_dump()

    @mcp.tool(
        name="get_supported_providers",
        title="获取支持的邮箱提供商",
        description="获取当前支持的邮箱服务提供商信息",
    )
    async def get_supported_providers() -> dict[str, Any]:
        """
        获取支持的邮箱服务提供商信息工具

        Returns:
            包含支持提供商信息和使用指南的字典
        """
        # 使用 Pydantic 模型构建响应
        providers = [
            ProviderInfo(
                name="QQ Mail",
                domain="qq.com",
                smtp_server="smtp.qq.com",
                smtp_port=587,
                security="TLS",
                auth_required="Authorization code (not password)",
                setup_notes="Enable SMTP service in QQ Mail settings and get authorization code",
            ),
            ProviderInfo(
                name="Gmail",
                domain="gmail.com",
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                security="TLS",
                auth_required="App-specific password (not regular password)",
                setup_notes="Enable 2-step verification and generate app-specific password",
            ),
        ]

        # 基础响应
        response_dict = SupportedProvidersResponse(
            success=True,
            supported_providers=providers,
        ).model_dump()

        # 添加额外的配置信息（保留原有的字典结构来兼容现有客户端）
        response_dict.update({
            "configuration": {
                "environment_variables": [
                    "EMAIL_ADDRESS - Your email address",
                    "EMAIL_PASSWORD - Your password/authorization code",
                ],
                "auto_detection": "SMTP settings are auto-detected based on email domain",
                "manual_config": "Manual SMTP configuration is also supported via environment variables",
            },
            "setup_steps": [
                "Enable SMTP service in your email provider",
                "Generate authorization code/app password",
                "Configure environment variables",
                "Test connection with check_email_config tool",
            ],
        })

        return response_dict

    logger.info("Email tools registered successfully")
