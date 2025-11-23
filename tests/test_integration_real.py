"""集成测试 - 使用真实邮箱配置"""

import os
import pytest
from unittest.mock import patch

from email_mcp_server.email_service import EmailService
from email_mcp_server.models import EmailMessage, Attachment, AttachmentType


@pytest.mark.integration
class TestRealEmailService:
    """使用真实邮箱配置的集成测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """检查是否有真实配置"""
        if not os.getenv("EMAIL_ADDRESS") or not os.getenv("EMAIL_PASSWORD"):
            pytest.skip("需要设置 EMAIL_ADDRESS 和 EMAIL_PASSWORD 环境变量")

    @pytest.mark.integration
    def test_real_config_loading(self):
        """测试真实配置加载"""
        # 不使用mock，直接测试真实配置
        service = EmailService()

        # 验证配置被正确加载
        assert service.settings.address is not None
        assert service.settings.password is not None
        assert service.settings.smtp_config is not None

        print(f"Loaded config for: {service.settings.address}")
        print(f"SMTP Server: {service.settings.smtp_config.server}:{service.settings.smtp_config.port}")
        print(f"Use TLS: {service.settings.smtp_config.use_tls}")
        print(f"Use SSL: {service.settings.smtp_config.use_ssl}")

    @pytest.mark.integration
    def test_real_connection(self):
        """测试真实SMTP连接"""
        service = EmailService()

        try:
            # 测试连接
            service.connect()

            # 验证连接信息
            info = service.get_connection_info()
            assert info.connected is True
            assert info.smtp_server is not None
            assert info.smtp_port is not None

            print(f"连接成功: {info.smtp_server}:{info.smtp_port}")
            print(f"Provider: {info.provider}")
            print(f"TLS: {info.use_tls}, SSL: {info.use_ssl}")

        except Exception as e:
            pytest.fail(f"真实连接测试失败: {e}")
        finally:
            service.disconnect()

    @pytest.mark.integration
    def test_send_real_email(self):
        """测试发送真实邮件（发送给自己）"""
        service = EmailService()

        try:
            # 连接SMTP服务器
            service.connect()

            # 创建测试邮件
            message = EmailMessage(
                to=[service.settings.address],  # 发送给自己
                subject="Email MCP Server 集成测试",
                body="这是一封来自Email MCP Server的集成测试邮件。\n\n测试时间: " + str(pytest.__version__),
                html_body=None
            )

            # 发送邮件
            message_id = service.send_email(message)

            # 验证发送结果
            assert message_id is not None
            assert isinstance(message_id, str)
            assert len(message_id) > 0

            print(f"邮件发送成功! Message ID: {message_id}")
            print(f"收件人: {service.settings.address}")

        except Exception as e:
            pytest.fail(f"发送真实邮件失败: {e}")
        finally:
            service.disconnect()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_send_email_with_attachment(self):
        """测试发送带附件的邮件"""
        import tempfile

        service = EmailService()

        try:
            # 创建临时测试文件
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write("这是一个测试附件文件。\n\nEmail MCP Server 集成测试")
                temp_file_path = f.name

            # 连接SMTP服务器
            service.connect()

            # 创建带附件的邮件
            message = EmailMessage(
                to=[service.settings.address],
                subject="Email MCP Server 带附件测试",
                body="测试邮件包含附件。",
                attachments=[Attachment(path=temp_file_path, type=AttachmentType.LOCAL)]
            )

            # 发送邮件
            message_id = service.send_email(message)

            # 验证发送结果
            assert message_id is not None
            print(f"带附件邮件发送成功! Message ID: {message_id}")

        except Exception as e:
            pytest.fail(f"发送带附件邮件失败: {e}")
        finally:
            service.disconnect()
            # 清理临时文件
            try:
                os.unlink(temp_file_path)
            except:
                pass

    @pytest.mark.integration
    def test_connection_test_method(self):
        """测试连接测试方法"""
        service = EmailService()

        try:
            # 使用test_connection方法
            result = service.test_connection()

            # 验证结果
            assert result is True
            print(f"连接测试通过")

        except Exception as e:
            pytest.fail(f"连接测试方法失败: {e}")


@pytest.mark.integration
class TestRealAttachmentService:
    """真实的附件服务测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """检查是否有真实配置"""
        if not os.getenv("EMAIL_ADDRESS") or not os.getenv("EMAIL_PASSWORD"):
            pytest.skip("需要设置 EMAIL_ADDRESS 和 EMAIL_PASSWORD 环境变量")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_download_real_remote_file(self):
        """测试下载真实远程文件"""
        from email_mcp_server.attachment_service import AttachmentService

        attachment_service = AttachmentService()

        # 使用一个真实的测试文件URL（小文件，稳定可用）
        test_url = "https://httpbin.org/bytes/1024"  # 返回1KB的随机数据

        try:
            # 处理远程附件
            attachment = Attachment(path=test_url, type=AttachmentType.REMOTE)
            result = attachment_service.process_attachment(attachment)

            # 验证结果
            assert result.filename is not None
            assert result.data is not None
            assert result.size == 1024  # 应该是1KB
            assert result.content_type is not None
            assert result.is_temp is True

            print(f"远程文件下载成功!")
            print(f"文件名: {result.filename}")
            print(f"大小: {result.size} 字节")
            print(f"类型: {result.content_type}")

        except Exception as e:
            pytest.fail(f"下载真实远程文件失败: {e}")
        finally:
            # 清理临时文件
            attachment_service.cleanup_temp_files()


@pytest.mark.integration
class TestRealEmailTools:
    """真实的Email工具测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """检查是否有真实配置"""
        if not os.getenv("EMAIL_ADDRESS") or not os.getenv("EMAIL_PASSWORD"):
            pytest.skip("需要设置 EMAIL_ADDRESS 和 EMAIL_PASSWORD 环境变量")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_send_email_tool_real(self):
        """测试真实的邮件发送工具"""
        from email_mcp_server.email_tools import register_email_tools
        from mcp.server.fastmcp import FastMCP

        # 创建临时MCP服务器
        mcp = FastMCP(name="Test Email MCP Server")

        try:
            # 注册工具
            register_email_tools(mcp)

            # 获取send_email工具
            send_email_tool = None
            for tool in mcp.tools:
                if tool.name == "send_email":
                    send_email_tool = tool
                    break

            assert send_email_tool is not None, "send_email工具未找到"

            # 创建模拟的Context
            class MockContext:
                async def elicit(self, message, response_type=None):
                    # 自动确认，用于测试
                    class MockResponse:
                        action = "accept"
                    return MockResponse()

            # 调用工具（发送给自己）
            result = await send_email_tool.handler(
                ctx=MockContext(),
                to=[os.getenv("EMAIL_ADDRESS")],
                subject="真实邮件工具集成测试",
                body="这是通过Email MCP工具发送的测试邮件。",
                require_confirmation=False  # 跳过确认
            )

            # 验证结果
            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True

            print(f"Email工具测试成功!")
            print(f"结果: {result}")

        except Exception as e:
            pytest.fail(f"Email工具测试失败: {e}")


if __name__ == "__main__":
    # 可以直接运行集成测试
    import sys
    sys.exit(pytest.main([__file__, "-v", "-m", "integration"]))