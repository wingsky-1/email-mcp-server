"""Configuration management for the Email MCP Server."""

from enum import Enum

from pydantic import BaseSettings, Field, validator

from .exceptions import ConfigurationError


class EmailProvider(str, Enum):
    """支持的邮箱服务提供商."""

    QQ = "qq"
    GMAIL = "gmail"


class SMTPConfig(BaseSettings):
    """SMTP 服务器配置."""

    server: str
    port: int
    use_tls: bool = True
    use_ssl: bool = False


class EmailSettings(BaseSettings):
    """邮件设置."""

    address: str = Field(..., env="EMAIL_ADDRESS")
    password: str = Field(..., env="EMAIL_PASSWORD")

    # 可选的 SMTP 配置（如果不提供将自动检测）
    smtp_server: str | None = Field(None, env="SMTP_SERVER")
    smtp_port: int | None = Field(None, env="SMTP_PORT")
    smtp_use_tls: bool | None = Field(None, env="SMTP_USE_TLS")
    smtp_use_ssl: bool | None = Field(None, env="SMTP_USE_SSL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("address")
    def validate_email_address(cls, v: str) -> str:
        """验证邮箱地址格式."""
        if not v or "@" not in v:
            raise ValueError("Invalid email address format")
        return v.lower()

    @property
    def provider(self) -> EmailProvider:
        """根据邮箱地址确定服务提供商."""
        domain = self.address.split("@")[-1].lower()
        if domain.endswith("qq.com"):
            return EmailProvider.QQ
        elif domain.endswith("gmail.com"):
            return EmailProvider.GMAIL
        else:
            raise ConfigurationError(f"Unsupported email provider: {domain}")

    @property
    def smtp_config(self) -> SMTPConfig:
        """获取 SMTP 配置."""
        # 如果用户手动配置了 SMTP 设置，优先使用
        if self.smtp_server and self.smtp_port:
            return SMTPConfig(
                server=self.smtp_server,
                port=self.smtp_port,
                use_tls=self.smtp_use_tls if self.smtp_use_tls is not None else True,
                use_ssl=self.smtp_use_ssl if self.smtp_use_ssl is not None else False,
            )

        # 根据邮箱提供商自动配置
        if self.provider == EmailProvider.QQ:
            return SMTPConfig(
                server="smtp.qq.com", port=587, use_tls=True, use_ssl=False
            )
        elif self.provider == EmailProvider.GMAIL:
            return SMTPConfig(
                server="smtp.gmail.com", port=587, use_tls=True, use_ssl=False
            )
        else:
            raise ConfigurationError(
                f"No SMTP configuration for provider: {self.provider}"
            )


class AppSettings(BaseSettings):
    """应用设置."""

    # 日志设置
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str | None = Field(None, env="LOG_FILE")

    # 文件处理设置
    max_attachment_size: int = Field(
        25 * 1024 * 1024, env="MAX_ATTACHMENT_SIZE"
    )  # 25MB
    temp_dir: str = Field("temp", env="TEMP_DIR")
    download_timeout: int = Field(30, env="DOWNLOAD_TIMEOUT")  # 秒
    max_retries: int = Field(3, env="MAX_RETRIES")

    # 确认设置
    require_confirmation: bool = Field(False, env="REQUIRE_CONFIRMATION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局设置实例
_email_settings: EmailSettings | None = None
_app_settings: AppSettings | None = None


def get_email_settings() -> EmailSettings:
    """获取邮件设置."""
    global _email_settings
    if _email_settings is None:
        _email_settings = EmailSettings()
    return _email_settings


def get_app_settings() -> AppSettings:
    """获取应用设置."""
    global _app_settings
    if _app_settings is None:
        _app_settings = AppSettings()
    return _app_settings


def get_settings() -> tuple[EmailSettings, AppSettings]:
    """获取所有设置."""
    return get_email_settings(), get_app_settings()


def reload_settings() -> None:
    """重新加载设置（主要用于测试）."""
    global _email_settings, _app_settings
    _email_settings = None
    _app_settings = None
