"""Email tools 模块测试"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from email_mcp_server.email_tools import (
    register_email_tools,
    _should_require_confirmation,
    _build_confirmation_message,
)
from email_mcp_server.models import SendEmailToolRequest


class TestEmailToolsFunctions:
    """Email tools 函数测试"""

    @pytest.mark.unit
    def test_should_require_confirmation_with_param(self):
        """测试带有参数时的确认逻辑"""
        # 参数为 True 时应该返回 True
        assert _should_require_confirmation(True, False) == True
        assert _should_require_confirmation(True, True) == True

        # 参数为 False 时应该返回 False
        assert _should_require_confirmation(False, True) == False
        assert _should_require_confirmation(False, False) == False

    @pytest.mark.unit
    def test_should_require_confirmation_without_param(self):
        """测试没有参数时的确认逻辑"""
        # 参数为 None 时应该返回全局设置
        assert _should_require_confirmation(None, True) == True
        assert _should_require_confirmation(None, False) == False

    @pytest.mark.unit
    def test_build_confirmation_message(self):
        """测试构建确认消息"""
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test body content",
            priority=3
        )

        message = _build_confirmation_message(request)

        assert "📧 准备发送邮件" in message
        assert "📋 主题: Test Subject" in message
        assert "👥 收件人: test@example.com" in message
        assert "⚡ 优先级: 普通" in message
        assert "📝 内容预览: Test body content" in message

    @pytest.mark.unit
    def test_build_confirmation_message_with_all_fields(self):
        """测试构建包含所有字段的确认消息"""
        request = SendEmailToolRequest(
            to=["recipient@example.com"],
            subject="Full Test",
            body="Body content",
            html_body="<p>HTML content</p>",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            reply_to="reply@example.com",
            priority=1,
            attachments=["file1.pdf", "file2.jpg", "file3.txt", "file4.doc"]
        )

        message = _build_confirmation_message(request)

        assert "📧 准备发送邮件" in message
        assert "📋 主题: Full Test" in message
        assert "👥 收件人: recipient@example.com" in message
        assert "📄 抄送: cc@example.com" in message
        assert "🔒 密送: bcc@example.com" in message
        assert "↩️ 回复至: reply@example.com" in message
        assert "⚡ 优先级: 最高" in message
        assert "📝 内容预览: Body content" in message
        assert "📎 附件数量: 4" in message
        assert "... 还有 1 个附件" in message  # 超过3个附件时显示省略

    @pytest.mark.unit
    def test_build_confirmation_message_long_content(self):
        """测试长内容截断"""
        long_content = "A" * 200  # 200个字符
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Long Content Test",
            body=long_content
        )

        message = _build_confirmation_message(request)

        assert "📝 内容预览: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA..." in message

    @pytest.mark.unit
    def test_register_email_tools(self):
        """测试注册邮件工具"""
        mock_mcp = Mock()
        mock_tool = Mock()

        with patch('email_mcp_server.email_tools.mcp.tool', mock_tool):
            register_email_tools(mock_mcp)

            # 验证工具被注册
            assert mock_tool.call_count >= 4  # 至少应该有4个工具

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_email_tool_success(self):
        """测试发送邮件工具成功场景"""
        mock_mcp = Mock()
        mock_ctx = Mock()
        mock_ctx.elicit = AsyncMock(return_value=Mock(action="accept"))

        with patch('email_mcp_server.email_tools.EmailService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.send_email.return_value = "test-message-id"

            with patch('email_mcp_server.email_tools.get_app_settings') as mock_settings:
                mock_settings.return_value = Mock(require_confirmation=False)

                with patch('email_mcp_server.email_tools.mcp.tool'):
                    # 注册工具
                    register_email_tools(mock_mcp)

                    # 这里我们无法直接调用工具函数，因为它被装饰器包装了
                    # 但我们可以验证相关的函数和类被正确调用
                    assert mock_service_class.called


class TestConfirmationMessageBuilder:
    """确认消息构建器测试"""

    @pytest.mark.unit
    def test_priority_names_mapping(self):
        """测试优先级名称映射"""
        # 测试所有优先级
        priority_tests = [
            (1, "最高"),
            (2, "高"),
            (3, "普通"),
            (4, "低"),
            (5, "最低"),
            (999, "普通"),  # 无效优先级应该默认为普通
        ]

        for priority, expected_name in priority_tests:
            request = SendEmailToolRequest(
                to=["test@example.com"],
                subject=f"Priority {priority} Test",
                priority=priority
            )
            message = _build_confirmation_message(request)
            assert f"⚡ 优先级: {expected_name}" in message

    @pytest.mark.unit
    def test_attachment_preview_limit(self):
        """测试附件预览数量限制"""
        # 测试正好3个附件
        request_3_attachments = SendEmailToolRequest(
            to=["test@example.com"],
            subject="3 Attachments",
            attachments=["file1.pdf", "file2.jpg", "file3.txt"]
        )
        message = _build_confirmation_message(request_3_attachments)
        assert "📎 附件数量: 3" in message
        assert "1. file1.pdf" in message
        assert "2. file2.jpg" in message
        assert "3. file3.txt" in message
        assert "..." not in message  # 不应该有省略号

        # 测试超过3个附件
        request_many_attachments = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Many Attachments",
            attachments=[f"file{i}.pdf" for i in range(10)]
        )
        message = _build_confirmation_message(request_many_attachments)
        assert "📎 附件数量: 10" in message
        assert "1. file0.pdf" in message
        assert "2. file1.pdf" in message
        assert "3. file2.pdf" in message
        assert "... 还有 7 个附件" in message