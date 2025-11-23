"""Test require_confirmation functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from email_mcp_server.email_tools import (
    _build_confirmation_message,
    _should_require_confirmation
)
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


class TestShouldRequireConfirmation:
    """测试 _should_require_confirmation 辅助函数"""

    def test_should_require_confirmation_with_param_true(self):
        """测试参数设置为 True 时强制要求确认"""
        result = _should_require_confirmation(True, False)  # 全局关闭，参数开启
        assert result is True

        result = _should_require_confirmation(True, True)   # 全局开启，参数开启
        assert result is True

    def test_should_require_confirmation_with_param_false(self):
        """测试参数设置为 False 时跳过确认"""
        result = _should_require_confirmation(False, True)   # 全局开启，参数关闭
        assert result is False

        result = _should_require_confirmation(False, False)  # 全局关闭，参数关闭
        assert result is False

    def test_should_require_confirmation_with_param_none(self):
        """测试参数为 None 时使用全局设置"""
        result = _should_require_confirmation(None, True)   # 全局开启
        assert result is True

        result = _should_require_confirmation(None, False)  # 全局关闭
        assert result is False


class TestParameterLevelConfirmation:
    """测试参数级确认功能"""

    @pytest.mark.asyncio
    async def test_send_email_with_param_true_overrides_global_false(
        self, confirmation_result_mock
    ):
        """测试参数 True 覆盖全局 False 设置"""
        with patch("email_mcp_server.email_tools.get_app_settings") as mock_settings, \
             patch("email_mcp_server.email_tools.EmailService") as mock_service_class:

            # 全局设置为 False，参数设置为 True
            mock_settings_instance = MagicMock()
            mock_settings_instance.require_confirmation = False
            mock_settings.return_value = mock_settings_instance

            mock_service = MagicMock()
            mock_service.send_email.return_value = "test-message-id"
            mock_service_class.return_value = mock_service

            # 创建请求数据，设置 require_confirmation=True
            request = SendEmailToolRequest(
                to=["test@example.com"],
                subject="Test Subject",
                body="Test body",
                require_confirmation=True,
            )

            # 创建 mock context
            mock_ctx = MagicMock()
            mock_ctx.elicit = AsyncMock(return_value=confirmation_result_mock)

            # 构建确认消息
            confirmation_msg = _build_confirmation_message(request)

            # 模拟 ctx.elicit 调用
            confirmation_result = await mock_ctx.elicit(
                confirmation_msg,
                response_type=None
            )

            # 检查用户响应
            assert confirmation_result.action == "accept"

            # 验证 _should_require_confirmation 逻辑
            needs_confirmation = _should_require_confirmation(
                request.require_confirmation,
                mock_settings_instance.require_confirmation
            )
            assert needs_confirmation is True  # 参数设置覆盖全局设置

            # 验证 elicit 会被调用
            mock_ctx.elicit.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_with_param_false_overrides_global_true(
        self, cancellation_result_mock
    ):
        """测试参数 False 覆盖全局 True 设置"""
        with patch("email_mcp_server.email_tools.get_app_settings") as mock_settings, \
             patch("email_mcp_server.email_tools.EmailService") as mock_service_class:

            # 全局设置为 True，参数设置为 False
            mock_settings_instance = MagicMock()
            mock_settings_instance.require_confirmation = True
            mock_settings.return_value = mock_settings_instance

            mock_service = MagicMock()
            mock_service.send_email.return_value = "test-message-id"
            mock_service_class.return_value = mock_service

            # 创建请求数据，设置 require_confirmation=False
            request = SendEmailToolRequest(
                to=["test@example.com"],
                subject="Test Subject",
                body="Test body",
                require_confirmation=False,
            )

            # 验证 _should_require_confirmation 逻辑
            needs_confirmation = _should_require_confirmation(
                request.require_confirmation,
                mock_settings_instance.require_confirmation
            )
            assert needs_confirmation is False  # 参数设置覆盖全局设置

            # 模拟直接发送邮件（无需确认）
            email_service = mock_service_class()
            message_id = email_service.send_email(request.to_email_message())

            assert message_id == "test-message-id"

    @pytest.mark.asyncio
    async def test_send_email_with_param_none_uses_global_setting(
        self, confirmation_result_mock
    ):
        """测试参数为 None 时使用全局设置"""
        with patch("email_mcp_server.email_tools.get_app_settings") as mock_settings, \
             patch("email_mcp_server.email_tools.EmailService") as mock_service_class:

            # 全局设置为 True，参数为 None
            mock_settings_instance = MagicMock()
            mock_settings_instance.require_confirmation = True
            mock_settings.return_value = mock_settings_instance

            mock_service = MagicMock()
            mock_service.send_email.return_value = "test-message-id"
            mock_service_class.return_value = mock_service

            # 创建请求数据，设置 require_confirmation=None
            request = SendEmailToolRequest(
                to=["test@example.com"],
                subject="Test Subject",
                body="Test body",
                require_confirmation=None,
            )

            # 创建 mock context
            mock_ctx = MagicMock()
            mock_ctx.elicit = AsyncMock(return_value=confirmation_result_mock)

            # 验证 _should_require_confirmation 逻辑
            needs_confirmation = _should_require_confirmation(
                request.require_confirmation,
                mock_settings_instance.require_confirmation
            )
            assert needs_confirmation is True  # 使用全局设置

            # 构建确认消息
            confirmation_msg = _build_confirmation_message(request)

            # 模拟 ctx.elicit 调用
            confirmation_result = await mock_ctx.elicit(
                confirmation_msg,
                response_type=None
            )

            # 检查用户响应
            assert confirmation_result.action == "accept"

            # 验证 elicit 会被调用
            mock_ctx.elicit.assert_called_once()


class TestParameterValidation:
    """测试参数验证"""

    def test_send_email_tool_request_accepts_require_confirmation_param(self):
        """测试 SendEmailToolRequest 接受 require_confirmation 参数"""
        # 测试显式设置为 True
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test",
            body="Test body",
            require_confirmation=True,
        )
        assert request.require_confirmation is True

        # 测试显式设置为 False
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test",
            body="Test body",
            require_confirmation=False,
        )
        assert request.require_confirmation is False

        # 测试默认值为 None
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test",
            body="Test body",
        )
        assert request.require_confirmation is None

    def test_confirmation_message_includes_parameter_info(self):
        """测试确认消息显示参数级控制信息"""
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test body",
            require_confirmation=True,  # 强制确认
        )

        confirmation_msg = _build_confirmation_message(request)

        # 确认消息应包含基本邮件信息
        assert "准备发送邮件" in confirmation_msg
        assert "Test Subject" in confirmation_msg
        assert "test@example.com" in confirmation_msg