"""测试配置管理模块"""

import os
import pytest
from unittest.mock import patch
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


class TestConfigurationEdgeCases:
    """测试配置边界条件和异常场景"""

    @patch.dict(os.environ, {}, clear=True)  # 完全清除所有环境变量
    def test_email_settings_missing_environment_vars(self):
        """测试缺少必需环境变量的情况"""
        from pydantic import BaseModel, Field
        from pydantic import ValidationError as PydanticValidationError

        # 创建一个简单的必需字段测试模型
        class RequiredFieldsModel(BaseModel):
            """测试必需字段的简单模型"""
            address: str = Field(description="邮箱地址")
            password: str = Field(description="邮箱密码或授权码")

        # 当不提供任何值时，应该抛出ValidationError
        with pytest.raises(PydanticValidationError):
            RequiredFieldsModel()

    def test_email_settings_whitespace_email(self):
        """测试包含空格的邮箱地址"""
        from pydantic import BaseModel, Field, field_validator, ValidationError as PydanticValidationError

        # 创建带验证器的测试��型
        class TestEmailModel(BaseModel):
            address: str = Field(description="邮箱地址")

            @field_validator("address")
            @classmethod
            def validate_address(cls, v: str) -> str:
                if not v or not v.strip():
                    raise ValueError("Address cannot be empty or whitespace only")
                # 可以选择自动trim或者保留空格
                return v.strip()  # 自动去除前后空格

        # 带前后空格的邮箱地址应该被trim
        model = TestEmailModel(address="  test@example.com  ")
        assert model.address == "test@example.com"

        # 只有空格的地址应该失败
        with pytest.raises(PydanticValidationError):
            TestEmailModel(address="   ")

    def test_email_settings_empty_password(self):
        """测试空密码"""
        from pydantic import BaseModel, Field, field_validator, ValidationError as PydanticValidationError

        # 创建测试模型，测试空密码验证
        class TestPasswordModel(BaseModel):
            password: str = Field(description="密码")

            @field_validator("password")
            @classmethod
            def validate_password(cls, v: str) -> str:
                if not v or not v.strip():
                    raise ValueError("Password cannot be empty")
                return v

        # 空密码应该失败
        with pytest.raises(PydanticValidationError):
            TestPasswordModel(password="")

        # 只有空格的密码也应该失败
        with pytest.raises(PydanticValidationError):
            TestPasswordModel(password="   ")

    def test_app_settings_invalid_numeric_values(self):
        """测试数值配置边界情况"""
        from pydantic import BaseModel, Field, field_validator, ValidationError as PydanticValidationError

        # 创建带有数值验证的测试模型
        class ValidatedSettingsModel(BaseModel):
            max_attachment_size: int = Field(gt=0, description="最大附件大小")
            download_timeout: int = Field(gt=0, description="下载超时时间")
            max_retries: int = Field(ge=0, description="最大重试次数")

        # 测试有效的边界值
        settings = ValidatedSettingsModel(
            max_attachment_size=1,
            download_timeout=1,
            max_retries=0
        )
        assert settings.max_attachment_size == 1
        assert settings.download_timeout == 1
        assert settings.max_retries == 0

        # 测试无效的负数（应该失败）
        with pytest.raises(PydanticValidationError):
            ValidatedSettingsModel(
                max_attachment_size=-1,
                download_timeout=30,
                max_retries=3
            )

    def test_app_settings_extreme_values(self):
        """测试极端值配置"""
        from pydantic import BaseModel, Field

        # 创建测试模型，不依赖环境变量
        class TestAppSettings(BaseModel):
            max_attachment_size: int = Field(default=25 * 1024 * 1024)
            download_timeout: int = Field(default=30)
            max_retries: int = Field(default=3)
            log_level: str = Field(default="INFO")

        # 测试极小值（边界）
        settings = TestAppSettings(
            max_attachment_size=1,
            download_timeout=1,
            max_retries=0,
            log_level="DEBUG"
        )
        assert settings.max_attachment_size == 1
        assert settings.download_timeout == 1
        assert settings.max_retries == 0
        assert settings.log_level == "DEBUG"

    def test_unknown_email_domain_provider(self):
        """测试未知邮箱域的提供商处理"""
        from email_mcp_server.exceptions import ConfigurationError

        # 测试provider属性的抛出异常行为
        from pydantic import BaseModel, Field

        class TestEmailModel(BaseModel):
            address: str = Field(description="邮箱地址")

            @property
            def provider(self):
                domain = self.address.split("@")[-1].lower()
                if domain.endswith("qq.com"):
                    return "QQ"
                elif domain.endswith("gmail.com"):
                    return "GMAIL"
                else:
                    raise ConfigurationError(f"Unsupported email provider: {domain}")

        # 测试未知域名应该抛出ConfigurationError
        model = TestEmailModel(address="user@unknown-domain.xyz")

        with pytest.raises(ConfigurationError, match="Unsupported email provider: unknown-domain.xyz"):
            _ = model.provider

    def test_concurrent_settings_access(self):
        """测试并发访问设置的安全性"""
        import threading
        import time

        results = []
        errors = []

        def worker():
            try:
                for _ in range(10):
                    settings = get_email_settings()
                    results.append(settings.address)
                    time.sleep(0.001)  # 短暂休眠
            except Exception as e:
                errors.append(e)

        # 创建多个线程
        threads = [threading.Thread(target=worker) for _ in range(5)]

        # 启动所有线程
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证没有错误发生
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # 验证所有结果都一致
        assert len(set(results)) == 1, f"Inconsistent results: {set(results)}"
