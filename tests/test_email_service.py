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
def email_service() -> Generator[EmailService, None, None]:
    """使用统一配置的EmailService实例 - 重命名以保持兼容性"""
    # conftest.py中的email_service fixture已经提供了统一配置
    # 这个fixture为了保持向后兼容性而存在
    from email_mcp_server.email_service import EmailService

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


class TestEmailService:
    """EmailService 测试 - 使用统一Mock配置"""

    @pytest.mark.unit
    def test_service_initialization(self, email_service):
        """测试使用真实配置的服务初始化"""
        # 验证配置已正确加载
        assert email_service.settings is not None
        assert email_service.settings.address is not None
        assert email_service.settings.password is not None
        assert email_service.settings.provider is not None
        assert email_service.settings.smtp_config is not None

        print(f"加载的邮箱: {email_service.settings.address}")
        print(f"提供商: {email_service.settings.provider.value}")
        print(f"SMTP: {email_service.settings.smtp_config.server}:{email_service.settings.smtp_config.port}")
        print(f"TLS: {email_service.settings.smtp_config.use_tls}")

    @pytest.mark.unit
    def test_real_config_values(self, email_service):
        """测试真实配置值"""
        # 验证配置值存在且有效
        assert email_service.settings.address is not None
        assert "@" in email_service.settings.address
        assert email_service.settings.smtp_config.server is not None
        assert email_service.settings.smtp_config.port is not None
        assert isinstance(email_service.settings.smtp_config.use_tls, bool)
        assert isinstance(email_service.settings.smtp_config.use_ssl, bool)

    @pytest.mark.unit
    def test_mock_smtp_success_with_real_config(self, email_service):
        """测试使用真实配置的SMTP连接Mock"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_smtp.return_value = mock_conn

            # 模拟连接成功
            email_service.connect()

            # 验证使用了正确的参数
            mock_smtp.assert_called_once_with(
                email_service.settings.smtp_config.server,
                email_service.settings.smtp_config.port
            )
            mock_conn.ehlo.assert_called()
            mock_conn.starttls.assert_called_once()
            mock_conn.ehlo.assert_called()  # TLS后的ehlo

            # 验证登录被调用
            mock_conn.login.assert_called_once_with(
                email_service.settings.address,
                email_service.settings.password
            )

            email_service.disconnect()

    @pytest.mark.unit
    def test_mock_smtp_ssl_success_with_real_config(self, email_service):
        """测试SSL连接（如果配置支持）"""
        with patch('smtplib.SMTP_SSL') as mock_smtp_ssl:
            mock_conn = Mock()
            mock_smtp_ssl.return_value = mock_conn

            # 临时修改配置为SSL（仅用于测试）
            original_use_tls = email_service.settings.smtp_config.use_tls
            original_use_ssl = email_service.settings.smtp_config.use_ssl
            email_service.settings.smtp_config.use_tls = False
            email_service.settings.smtp_config.use_ssl = True

            try:
                email_service.connect()

                # 验证使用SSL连接
                mock_smtp_ssl.assert_called_once_with(
                    email_service.settings.smtp_config.server,
                    email_service.settings.smtp_config.port
                )

                # 验证登录被调用
                mock_conn.login.assert_called_once_with(
                    email_service.settings.address,
                    email_service.settings.password
                )

            finally:
                email_service.disconnect()
                # 恢复原始配置
                email_service.settings.smtp_config.use_tls = original_use_tls
                email_service.settings.smtp_config.use_ssl = original_use_ssl

    @pytest.mark.unit
    def test_send_email_mock_with_real_config(self, email_service):
        """测试使用真实配置的邮件发送Mock"""
        from email_mcp_server.models import EmailMessage

        with patch('smtplib.SMTP') as mock_smtp:
            mock_conn = Mock()
            mock_smtp.return_value = mock_conn
            mock_conn.sendmail.return_value = {}

            # 连接
            email_service.connect()

            # 创建测试邮件
            message = EmailMessage(
                to=["test@example.com"],
                subject="测试邮件",
                body="测试内容"
            )

            # 发送邮件
            message_id = email_service.send_email(message)

            # 验证发送调用
            assert mock_conn.sendmail.called
            call_args = mock_conn.sendmail.call_args[0]

            # 验证参数
            assert call_args[0] == email_service.settings.address  # from_addr
            assert call_args[1] == ["test@example.com"]  # to_addrs

            email_service.disconnect()


if __name__ == "__main__":
    # 可以直接运行这个测试文件
    pytest.main([__file__, "-v"])