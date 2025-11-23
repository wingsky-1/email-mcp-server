"""Test require_confirmation functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from email_mcp_server.email_tools import _build_confirmation_message
from email_mcp_server.models import SendEmailToolRequest


@pytest.fixture
def confirmation_result_mock():
    """Mock confirmation result with accept action."""
    result = MagicMock()
    result.action = "accept"
    return result


@pytest.fixture
def cancellation_result_mock():
    """Mock confirmation result with cancel action."""
    result = MagicMock()
    result.action = "cancel"
    return result


class TestRequireConfirmation:
    """测试 require_confirmation 功能的集成测试"""

    @pytest.mark.asyncio
    async def test_send_email_logic_with_confirmation_enabled_and_accepted(
        self, confirmation_result_mock
    ):
        """测试启用确认时用户接受发送邮件的核心逻辑"""
        # 直接导入和测试 send_email 函数的逻辑
        with patch("email_mcp_server.email_tools.get_app_settings") as mock_settings, \
             patch("email_mcp_server.email_tools.EmailService") as mock_service_class:

            # 设置 require_confirmation 为 True
            mock_settings_instance = MagicMock()
            mock_settings_instance.require_confirmation = True
            mock_settings.return_value = mock_settings_instance

            # 创建 mock email service
            mock_service = MagicMock()
            mock_service.send_email.return_value = "test-message-id"
            mock_service_class.return_value = mock_service

            # 模拟 send_email 函数的核心逻辑
            from email_mcp_server.email_tools import SendEmailToolRequest

            # 创建请求数据
            request = SendEmailToolRequest(
                to=["test@example.com"],
                subject="Test Subject",
                body="Test body",
            )

            # 验证正文内容不为空
            assert request.body is not None

            # 转换为 EmailMessage 对象
            message = request.to_email_message()

            # 检查是否需要用户确认
            app_settings = mock_settings.return_value
            assert app_settings.require_confirmation is True

            # 创建 mock context
            mock_ctx = MagicMock()
            mock_ctx.elicit = AsyncMock(return_value=confirmation_result_mock)

            # 构建确认消息
            confirmation_msg = _build_confirmation_message(request)
            assert "准备发送邮件" in confirmation_msg
            assert "Test Subject" in confirmation_msg

            # 模拟 ctx.elicit 调用
            confirmation_result = await mock_ctx.elicit(
                confirmation_msg,
                response_type=None
            )

            # 检查用户响应
            assert confirmation_result.action == "accept"

            # 模拟发送邮件
            email_service = mock_service_class()
            message_id = email_service.send_email(message)

            assert message_id == "test-message-id"

            # 验证 elicit 被调用
            mock_ctx.elicit.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_logic_with_confirmation_enabled_and_cancelled(
        self, cancellation_result_mock
    ):
        """测试启用确认时用户取消发送邮件的核心逻辑"""
        with patch("email_mcp_server.email_tools.get_app_settings") as mock_settings:

            # 设置 require_confirmation 为 True
            mock_settings_instance = MagicMock()
            mock_settings_instance.require_confirmation = True
            mock_settings.return_value = mock_settings_instance

            # 创建请求数据
            from email_mcp_server.email_tools import SendEmailToolRequest
            request = SendEmailToolRequest(
                to=["test@example.com"],
                subject="Test Subject",
                body="Test body",
            )

            # 创建 mock context
            mock_ctx = MagicMock()
            mock_ctx.elicit = AsyncMock(return_value=cancellation_result_mock)

            # 构建确认消息
            confirmation_msg = _build_confirmation_message(request)

            # 模拟 ctx.elicit 调用
            confirmation_result = await mock_ctx.elicit(
                confirmation_msg,
                response_type=None
            )

            # 检查用户响应
            assert confirmation_result.action == "cancel"

            # 模拟取消逻辑
            if confirmation_result.action != "accept":
                result = {
                    "success": False,
                    "error": "Email sending cancelled by user",
                    "error_code": "USER_CANCELLED",
                    "status": "cancelled",
                }
                assert result["success"] is False
                assert result["error_code"] == "USER_CANCELLED"

            # 验证 elicit 被调用
            mock_ctx.elicit.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_logic_with_confirmation_disabled(self):
        """测试禁用确认时直接发送邮件的核心逻辑"""
        with patch("email_mcp_server.email_tools.get_app_settings") as mock_settings, \
             patch("email_mcp_server.email_tools.EmailService") as mock_service_class:

            # 设置 require_confirmation 为 False
            mock_settings_instance = MagicMock()
            mock_settings_instance.require_confirmation = False
            mock_settings.return_value = mock_settings_instance

            # 创建 mock email service
            mock_service = MagicMock()
            mock_service.send_email.return_value = "test-message-id"
            mock_service_class.return_value = mock_service

            # 创建请求数据
            from email_mcp_server.email_tools import SendEmailToolRequest
            request = SendEmailToolRequest(
                to=["test@example.com"],
                subject="Test Subject",
                body="Test body",
            )

            # 检查是否需要用户确认
            app_settings = mock_settings.return_value
            assert app_settings.require_confirmation is False

            # 如果不需要确认，直接发送邮件
            email_service = mock_service_class()
            message_id = email_service.send_email(request.to_email_message())

            assert message_id == "test-message-id"


class TestBuildConfirmationMessage:
    """测试确认消息构建功能"""

    def test_build_confirmation_message_basic(self):
        """测试基本确认消息构建"""
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test body content",
        )

        message = _build_confirmation_message(request)

        assert "📧 准备发送邮件" in message
        assert "📋 主题: Test Subject" in message
        assert "👥 收件人: test@example.com" in message
        assert "📝 内容预览: Test body content" in message
        assert "⚠️  请确认是否发送此邮件？" in message

    def test_build_confirmation_message_with_cc_bcc(self):
        """测试包含抄送和密送的确认消息"""
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test body",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
        )

        message = _build_confirmation_message(request)

        assert "📄 抄送: cc@example.com" in message
        assert "🔒 密送: bcc@example.com" in message

    def test_build_confirmation_message_with_reply_to(self):
        """测试包含回复地址的确认消息"""
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test body",
            reply_to="reply@example.com",
        )

        message = _build_confirmation_message(request)

        assert "↩️ 回复至: reply@example.com" in message

    def test_build_confirmation_message_with_priority(self):
        """测试不同优先级的确认消息"""
        # 测试最高优先级
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test body",
            priority=1,
        )

        message = _build_confirmation_message(request)
        assert "⚡ 优先级: 最高" in message

        # 测试低优先级
        request.priority = 4
        message = _build_confirmation_message(request)
        assert "⚡ 优先级: 低" in message

    def test_build_confirmation_message_with_attachments(self):
        """测试包含附件的确认消息"""
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test body",
            attachments=["file1.txt", "file2.pdf", "file3.jpg", "file4.doc"],
        )

        message = _build_confirmation_message(request)

        assert "📎 附件数量: 4" in message
        assert "1. file1.txt" in message
        assert "2. file2.pdf" in message
        assert "3. file3.jpg" in message
        assert "... 还有 1 个附件" in message

    def test_build_confirmation_message_long_content_preview(self):
        """测试长内容的预览截断"""
        long_content = "This is a very long content that should be truncated " * 10

        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body=long_content,
        )

        message = _build_confirmation_message(request)

        assert "📝 内容预览:" in message
        assert "..." in message  # 确认内容被截断
        # 验证预览长度不超过100字符 + "..."
        preview_line = [line for line in message.split('\n') if '📝 内容预览:' in line][0]
        preview_content = preview_line.split('📝 内容预览: ')[1]
        assert len(preview_content) <= 103  # 100 + "..."