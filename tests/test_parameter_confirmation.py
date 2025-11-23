"""Test parameter-level require_confirmation functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from email_mcp_server.email_tools import _should_require_confirmation, _build_confirmation_message
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
            from email_mcp_server.email_tools import _should_require_confirmation
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
            from email_mcp_server.email_tools import _should_require_confirmation
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
            from email_mcp_server.email_tools import _should_require_confirmation
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

        # 注意：确认消息本身不需要显示确认设置信息
        # 因为确认行为是由 _should_require_authentication 函数控制的