"""EmailService 测试 - 使用真实配置"""

import pytest
from unittest.mock import Mock, patch
from typing import Generator
from pathlib import Path

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

from email_mcp_server.email_service import EmailService
from email_mcp_server.config import EmailSettings


@pytest.fixture
def email_service_real_config() -> Generator[EmailService, None, None]:
    """使用真实配置的EmailService实例"""
    import os
    from dotenv import load_dotenv

    # 加载.env.test文件
    env_test_path = Path(__file__).parent.parent / ".env.test"
    if env_test_path.exists():
        load_dotenv(env_test_path)

    with patch('email_mcp_server.email_service.get_email_settings') as mock_get_settings:
        # 使用真实配置创建Mock对象
        try:
            real_settings = EmailSettings()

            # 创建Mock对象，但使用真实配置的值
            settings_mock = Mock()
            settings_mock.address = real_settings.address
            settings_mock.password = real_settings.password
            settings_mock.provider = real_settings.provider
            settings_mock.smtp_config = real_settings.smtp_config

            mock_get_settings.return_value = settings_mock

            # 创建EmailService实例
            service = EmailService()
            yield service

        except Exception as e:
            pytest.skip(f"无法加载真实配置: {e}")


class TestEmailServiceRealConfig:
    """使用真实配置的EmailService测试"""

    @pytest.mark.unit
    def test_service_initialization_with_real_config(self, email_service_real_config):
        """测试使用真实配置的服务初始化"""
        service = email_service_real_config

        # 验证配置已正确加载
        assert service.settings is not None
        assert service.settings.address is not None
        assert service.settings.password is not None
        assert service.settings.provider is not None
        assert service.settings.smtp_config is not None

        print(f"加载的邮箱: {service.settings.address}")
        print(f"提供商: {service.settings.provider.value}")
        print(f"SMTP: {service.settings.smtp_config.server}:{service.settings.smtp_config.port}")
        print(f"TLS: {service.settings.smtp_config.use_tls}")

    @pytest.mark.unit
    def test_real_config_values(self, email_service_real_config):
        """测试真实配置值"""
        service = email_service_real_config

        # 验证配置值
        assert service.settings.address == "tangyi060320@gmail.com"
        assert service.settings.smtp_config.server == "smtp.gmail.com"
        assert service.settings.smtp_config.port == 587
        assert service.settings.smtp_config.use_tls is True
        assert service.settings.smtp_config.use_ssl is False

    @pytest.mark.unit
    def test_mock_smtp_success_with_real_config(self, email_service_real_config):
        """测试使用真实配置的SMTP连接Mock"""
        service = email_service_real_config

        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_smtp.return_value = mock_conn

            # 模拟连接成功
            service.connect()

            # 验证使用了正确的参数
            mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
            mock_conn.ehlo.assert_called()
            mock_conn.starttls.assert_called_once()
            mock_conn.ehlo.assert_called()  # TLS后的ehlo

            # 验证登录被调用
            mock_conn.login.assert_called_once_with("tangyi060320@gmail.com", "qnbxkavrbjbilmgi")

            service.disconnect()

    @pytest.mark.unit
    def test_mock_smtp_ssl_success_with_real_config(self, email_service_real_config):
        """测试SSL连接（如果配置支持）"""
        service = email_service_real_config

        with patch('smtplib.SMTP_SSL') as mock_smtp_ssl:
            mock_conn = Mock()
            mock_smtp_ssl.return_value = mock_conn

            # 临时修改配置为SSL（仅用于测试）
            original_use_tls = service.settings.smtp_config.use_tls
            original_use_ssl = service.settings.smtp_config.use_ssl
            service.settings.smtp_config.use_tls = False
            service.settings.smtp_config.use_ssl = True

            try:
                service.connect()

                # 验证使用SSL连接
                mock_smtp_ssl.assert_called_once_with("smtp.gmail.com", 587)

                # 验证登录被调用
                mock_conn.login.assert_called_once_with("tangyi060320@gmail.com", "qnbxkavrbjbilmgi")

            finally:
                service.disconnect()
                # 恢复原始配置
                service.settings.smtp_config.use_tls = original_use_tls
                service.settings.smtp_config.use_ssl = original_use_ssl

    @pytest.mark.unit
    def test_send_email_mock_with_real_config(self, email_service_real_config):
        """测试使用真实配置的邮件发送Mock"""
        from email_mcp_server.models import EmailMessage

        service = email_service_real_config

        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_smtp.return_value = mock_conn
            mock_conn.sendmail.return_value = {}

            # 连接
            service.connect()

            # 创建测试邮件
            message = EmailMessage(
                to=["test@example.com"],
                subject="测试邮件",
                body="测试内容"
            )

            # 发送邮件
            message_id = service.send_email(message)

            # 验证发送调用
            assert mock_conn.sendmail.called
            call_args = mock_conn.sendmail.call_args[0]

            # 验证参数
            assert call_args[0] == service.settings.address  # from_addr
            assert call_args[1] == ["test@example.com"]  # to_addrs

            service.disconnect()


if __name__ == "__main__":
    # 可以直接运行这个测试文件
    pytest.main([__file__, "-v"])