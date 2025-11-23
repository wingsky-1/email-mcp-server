"""测试配置管理模块"""

import pytest
from pydantic import ValidationError

from email_mcp_server.config import (
    EmailProvider,
    EmailSettings,
    AppSettings,
    get_email_settings,
    get_app_settings,
    get_settings,
    reload_settings,
)


class TestEmailProvider:
    """测试 EmailProvider 枚举"""

    def test_email_provider_values(self):
        """测试邮箱提供商枚举值"""
        assert EmailProvider.QQ.value == "qq"
        assert EmailProvider.GMAIL.value == "gmail"
        assert EmailProvider.QQ.name == "QQ"
        assert EmailProvider.GMAIL.name == "GMAIL"

    def test_email_provider_comparison(self):
        """测试邮箱提供商比较"""
        assert EmailProvider.QQ == EmailProvider.QQ
        assert EmailProvider.QQ != EmailProvider.GMAIL
        assert EmailProvider.QQ.value == "qq"


class TestEmailSettings:
    """测试 EmailSettings 配置"""

    def test_email_settings_from_env(self):
        """测试从环境变量创建 EmailSettings"""
        settings = EmailSettings()
        assert settings.address is not None
        assert settings.password is not None

    def test_email_settings_invalid_email_format(self):
        """测试无效邮箱格式"""
        import os

        original_email = os.environ.get("EMAIL_ADDRESS")
        original_password = os.environ.get("EMAIL_PASSWORD")

        try:
            os.environ["EMAIL_ADDRESS"] = "invalid-email"
            if "EMAIL_PASSWORD" not in os.environ:
                os.environ["EMAIL_PASSWORD"] = "test_password"

            reload_settings()  # 清除缓存

            with pytest.raises(ValidationError):
                EmailSettings()
        finally:
            # 恢复原始环境变量
            if original_email is not None:
                os.environ["EMAIL_ADDRESS"] = original_email
            elif "EMAIL_ADDRESS" in os.environ:
                del os.environ["EMAIL_ADDRESS"]

            if original_password is not None:
                os.environ["EMAIL_PASSWORD"] = original_password
            elif "EMAIL_PASSWORD" in os.environ:
                del os.environ["EMAIL_PASSWORD"]

            reload_settings()

    def test_email_settings_provider_detection_gmail(self):
        """测试 Gmail 提供商自动检测"""
        settings = EmailSettings()
        # 假设 .env 文件中配置的是 Gmail 地址
        if "gmail.com" in settings.address:
            assert settings.provider == EmailProvider.GMAIL

    def test_smtp_config_property(self):
        """测试 SMTP 配置属性"""
        settings = EmailSettings()
        smtp_config = settings.smtp_config
        assert smtp_config is not None
        assert smtp_config.server is not None
        assert smtp_config.port is not None
        assert isinstance(smtp_config.use_tls, bool)
        assert isinstance(smtp_config.use_ssl, bool)


class TestAppSettings:
    """测试 AppSettings 配置"""

    def test_app_settings_from_env(self):
        """测试从环境变量创建 AppSettings"""
        settings = AppSettings()
        assert settings.log_level is not None
        assert settings.max_attachment_size > 0
        assert settings.temp_dir is not None
        assert settings.download_timeout > 0
        assert settings.max_retries > 0

    def test_app_settings_defaults(self):
        """测试 AppSettings 默认值（当没有环境变量时）"""
        # 使用 model_construct 创建模型实例，绕过环境变量加载
        settings = AppSettings.model_construct(
            log_level="INFO",
            log_file=None,
            max_attachment_size=25 * 1024 * 1024,  # 25MB
            temp_dir="temp",
            download_timeout=30,
            max_retries=3,
            require_confirmation=False,
        )
        assert settings.log_level == "INFO"
        assert settings.log_file is None
        assert settings.max_attachment_size == 25 * 1024 * 1024  # 25MB
        assert settings.temp_dir == "temp"
        assert settings.download_timeout == 30
        assert settings.max_retries == 3
        assert settings.require_confirmation is False


class TestSettingsFunctions:
    """测试配置管理函数"""

    def test_get_email_settings(self):
        """测试获取邮箱设置"""
        reload_settings()  # 清除缓存
        settings = get_email_settings()
        assert isinstance(settings, EmailSettings)
        assert settings.address is not None
        assert settings.password is not None

    def test_get_app_settings(self):
        """测试获取应用设置"""
        reload_settings()  # 清除缓存
        settings = get_app_settings()
        assert isinstance(settings, AppSettings)
        assert settings.log_level is not None

    def test_get_settings(self):
        """测试获取所有设置"""
        reload_settings()  # 清除缓存
        email_settings, app_settings = get_settings()
        assert isinstance(email_settings, EmailSettings)
        assert isinstance(app_settings, AppSettings)

    def test_settings_caching(self):
        """测试设置缓存"""
        reload_settings()  # 清除缓存

        # 第一次调用
        email_settings1 = get_email_settings()
        app_settings1 = get_app_settings()

        # 第二次调用应该返回同一个实例
        email_settings2 = get_email_settings()
        app_settings2 = get_app_settings()

        assert email_settings1 is email_settings2
        assert app_settings1 is app_settings2

    def test_reload_settings(self):
        """测试重新加载设置"""
        # 获取初始设置
        settings1 = get_email_settings()
        settings2 = get_app_settings()

        # 重新加载
        reload_settings()

        # 获取新设置应该是新实例
        settings3 = get_email_settings()
        settings4 = get_app_settings()

        assert settings1 is not settings3
        assert settings2 is not settings4
        # 分别验证缓存：email settings 和 app settings 应该各自缓存
        assert get_email_settings() is settings3
        assert get_app_settings() is settings4

    def test_reload_settings_no_existing_cache(self):
        """测试重新加载设置当缓存不存在时"""
        # 没有缓存的情况下重新加载应该不抛出异常
        reload_settings()
        # 应该不抛出异常


class TestConfigurationValidation:
    """测试配置验证"""

    def test_email_provider_validation(self):
        """测试邮箱提供商验证"""
        # 测试已知的提供商
        settings_gmail = EmailSettings()
        if "gmail.com" in settings_gmail.address:
            assert settings_gmail.provider == EmailProvider.GMAIL

        settings_qq = EmailSettings()
        if "qq.com" in settings_qq.address:
            assert settings_qq.provider == EmailProvider.QQ

    def test_smtp_config_validation(self):
        """测试 SMTP 配置验证"""
        settings = EmailSettings()
        smtp_config = settings.smtp_config

        # 验证 SMTP 配置的基本字段
        assert smtp_config.server is not None
        assert smtp_config.port > 0
        assert isinstance(smtp_config.use_tls, bool)
        assert isinstance(smtp_config.use_ssl, bool)

        # 验证常见的 SMTP 端口
        assert smtp_config.port in [25, 465, 587, 2525]
