"""Email service implementation."""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from typing import List, Optional
import logging
import re

from .config import get_email_settings
from .models import EmailMessage, SMTPConfig
from .exceptions import (
    EmailServiceError,
    SMTPConnectionError,
    AuthenticationError,
    ValidationError,
)
from .logging_config import get_logger

logger = get_logger(__name__)


class EmailService:
    """邮件服务类."""

    def __init__(self) -> None:
        """初始化邮件服务."""
        self.settings = get_email_settings()
        self._connection: Optional[smtplib.SMTP] = None

    def connect(self) -> None:
        """连接到 SMTP 服务器."""
        if self._connection:
            return

        smtp_config = self.settings.smtp_config

        try:
            logger.info(
                f"Connecting to SMTP server: {smtp_config.server}:{smtp_config.port}"
            )

            if smtp_config.use_ssl:
                # 使用 SSL 连接
                self._connection = smtplib.SMTP_SSL(
                    smtp_config.server, smtp_config.port
                )
                logger.info("Connected using SSL")
            else:
                # 使用普通连接，然后启动 TLS
                self._connection = smtplib.SMTP(smtp_config.server, smtp_config.port)
                self._connection.ehlo()

                if smtp_config.use_tls:
                    context = ssl.create_default_context()
                    self._connection.starttls(context=context)
                    self._connection.ehlo()
                    logger.info("Connected with TLS")

            # 登录认证
            try:
                self._connection.login(self.settings.address, self.settings.password)
                logger.info(f"Successfully authenticated as {self.settings.address}")
            except smtplib.SMTPAuthenticationError as e:
                error_msg = str(e)
                if "535" in error_msg:  # 认证失败
                    raise AuthenticationError(
                        "Authentication failed. Check your email address and password."
                    )
                elif "530" in error_msg:  # 需要认证
                    raise AuthenticationError(
                        "Authentication required. Please enable SMTP service for your email."
                    )
                else:
                    raise AuthenticationError(f"Authentication error: {error_msg}")

        except smtplib.SMTPConnectError as e:
            raise SMTPConnectionError(f"Failed to connect to SMTP server: {e}")
        except smtplib.SMTPServerDisconnected as e:
            raise SMTPConnectionError(f"SMTP server disconnected: {e}")
        except Exception as e:
            raise SMTPConnectionError(f"Connection error: {e}")

    def disconnect(self) -> None:
        """断开 SMTP 连接."""
        if self._connection:
            try:
                self._connection.quit()
                logger.info("Disconnected from SMTP server")
            except Exception as e:
                logger.warning(f"Error while disconnecting: {e}")
            finally:
                self._connection = None

    def test_connection(self) -> bool:
        """测试连接."""
        try:
            self.connect()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
        finally:
            self.disconnect()

    def send_email(self, message: EmailMessage) -> str:
        """发送邮件."""
        if not self._connection:
            self.connect()

        try:
            # 创建邮件消息
            msg = self._create_email_message(message)

            # 发送邮件
            recipients = message.to.copy()
            if message.cc:
                recipients.extend(message.cc)
            if message.bcc:
                recipients.extend(message.bcc)

            logger.info(f"Sending email to {len(recipients)} recipients")
            result = self._connection.sendmail(
                self.settings.address, recipients, msg.as_string()
            )

            # 检查发送结果
            if result:
                # 部分邮件发送失败
                failed_recipients = list(result.keys())
                logger.error(f"Failed to send to recipients: {failed_recipients}")
                raise EmailServiceError(
                    f"Failed to send to {len(failed_recipients)} recipients"
                )

            logger.info("Email sent successfully")
            return "sent"  # 返回消息ID或状态

        except smtplib.SMTPRecipientsRefused as e:
            raise EmailServiceError("All recipients were refused")
        except smtplib.SMTPSenderRefused as e:
            raise EmailServiceError("Sender address refused")
        except smtplib.SMTPDataError as e:
            raise EmailServiceError(f"Message data refused: {e}")
        except Exception as e:
            raise EmailServiceError(f"Failed to send email: {e}")

    def _create_email_message(self, message: EmailMessage) -> MIMEMultipart:
        """创建邮件消息对象."""
        # 创建邮件对象
        msg = MIMEMultipart("alternative")

        # 设置邮件头
        msg["Subject"] = message.subject
        msg["From"] = formataddr(
            (self.settings.address.split("@")[0], self.settings.address)
        )
        msg["To"] = ", ".join(message.to)

        if message.cc:
            msg["Cc"] = ", ".join(message.cc)

        if message.reply_to:
            msg["Reply-To"] = message.reply_to

        if message.priority != 3:
            # 设置优先级（1=最高, 5=最低）
            priority_headers = {1: "Highest", 2: "High", 4: "Low", 5: "Lowest"}
            if message.priority in priority_headers:
                msg["X-Priority"] = str(message.priority)
                msg["X-MSMail-Priority"] = priority_headers[message.priority]

        # 添加邮件正文
        if message.body:
            text_part = MIMEText(message.body, "plain", "utf-8")
            msg.attach(text_part)

        if message.html_body:
            html_part = MIMEText(message.html_body, "html", "utf-8")
            msg.attach(html_part)

        # 添加附件（将在阶段四实现）
        # TODO: 实现附件处理

        return msg

    def get_connection_info(self) -> dict:
        """获取连接信息（隐藏敏感信息）。"""
        smtp_config = self.settings.smtp_config
        return {
            "provider": self.settings.provider.value,
            "smtp_server": smtp_config.server,
            "smtp_port": smtp_config.port,
            "use_tls": smtp_config.use_tls,
            "use_ssl": smtp_config.use_ssl,
            "connected": self._connection is not None,
        }


def validate_email_format(email: str) -> bool:
    """验证邮箱地址格式."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_email_address(email: str) -> None:
    """验证邮箱地址并抛出异常."""
    if not email or not isinstance(email, str):
        raise ValidationError("Email address is required")

    email = email.strip()
    if not email:
        raise ValidationError("Email address cannot be empty")

    if not validate_email_format(email):
        raise ValidationError(f"Invalid email format: {email}")


def validate_multiple_emails(emails: List[str]) -> None:
    """验证多个邮箱地址."""
    if not emails:
        raise ValidationError("Email list cannot be empty")

    for email in emails:
        validate_email_address(email)
