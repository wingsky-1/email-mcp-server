#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示 require_confirmation 功能的脚本

这个脚本展示了如何使用新的 require_confirmation 功能。
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from email_mcp_server.email_tools import _build_confirmation_message
from email_mcp_server.models import SendEmailToolRequest


async def demo_confirmation_message():
    """演示确认消息的构建"""
    print("演示确认消息构建功能")
    print("=" * 50)

    # 创建测试邮件请求
    request = SendEmailToolRequest(
        to=["recipient@example.com", "user@test.com"],
        subject="重要通知：系统更新计划",
        body="尊敬的用户，我们计划在本周末进行系统维护，请提前做好准备。",
        html_body="<p>尊敬的用户，我们计划在<strong>本周末</strong>进行系统维护，请提��做好准备。</p>",
        cc=["manager@example.com"],
        bcc=["admin@internal.com"],
        attachments=["report.pdf", "data.xlsx", "summary.docx"],
        reply_to="support@company.com",
        priority=2,  # 高优先级
    )

    # 构建确认消息
    confirmation_msg = _build_confirmation_message(request)

    print("生成的确认消息：")
    # 移除emoji字符以避免编码问题
    clean_msg = confirmation_msg.replace('📧', '[邮件]').replace('📋', '[主题]').replace('👥', '[收件人]').replace('📄', '[抄送]').replace('🔒', '[密送]').replace('↩️', '[回复]').replace('⚡', '[优先级]').replace('📝', '[内容]').replace('📎', '[附件]').replace('⚠️', '[警告]').replace('=', '=')
    print(clean_msg)
    print("\n")


async def demo_confirmation_flow():
    """演示确认流程"""
    print("演示确认流程")
    print("=" * 50)

    # 模拟用户确认
    print("场景 1: 用户确认发送")
    mock_ctx_accept = MagicMock()
    mock_ctx_accept.elicit = AsyncMock(return_value=MagicMock(action="accept"))

    confirmation_msg = "准备发送邮件\n主题: 测试邮件\n收件人: test@example.com\n请确认是否发送此邮件？"

    result = await mock_ctx_accept.elicit(confirmation_msg, response_type=None)
    print(f"用户响应: {result.action}")

    if result.action == "accept":
        print("邮件将发送")

    print("\n场景 2: 用户取消发送")
    mock_ctx_cancel = MagicMock()
    mock_ctx_cancel.elicit = AsyncMock(return_value=MagicMock(action="cancel"))

    result = await mock_ctx_cancel.elicit(confirmation_msg, response_type=None)
    print(f"用户响应: {result.action}")

    if result.action != "accept":
        print("邮件发送已取消")


def demo_config_scenarios():
    """演示不同配置场景"""
    print("演示配置场景")
    print("=" * 50)

    # 场景 1: 禁用确认
    print("场景 1: REQUIRE_CONFIRMATION=false")
    print("- 用户调用 send_email 工具")
    print("- 系统直接发送邮件")
    print("- 无需用户确认")
    print("- 适用场景: 自动化脚本、批量发送")
    print()

    # 场景 2: 启用确认
    print("场景 2: REQUIRE_CONFIRMATION=true")
    print("- 用户调用 send_email 工具")
    print("- 系统显示确认对话框")
    print("- 用户可以选择确认或取消")
    print("- 适用场景: 交互式使用、重要邮件")
    print()


def main():
    """主函数"""
    print("require_confirmation 功能演示")
    print("=" * 60)
    print()

    # 演示配置场景
    demo_config_scenarios()

    # 演示确认消息构建
    asyncio.run(demo_confirmation_message())

    # 演示确认流程
    asyncio.run(demo_confirmation_flow())

    print("如何启用 require_confirmation 功能:")
    print("在 .env 文件中设置:")
    print("REQUIRE_CONFIRMATION=true")
    print()

    print("功能特点:")
    print("1. 当启用时，每次发送邮件前都会请求用户确认")
    print("2. 确认消息包含邮件的所有重要信息")
    print("3. 用户可以选择确认发送或取消操作")
    print("4. 提供清晰的错误信息和状态反馈")
    print()

    print("技术实现:")
    print("- 使用 FastMCP 的 ctx.elicit() 方法")
    print("- 基于环境变量 REQUIRE_CONFIRMATION 控制开关")
    print("- 完整的错误处理和状态管理")
    print("- 包含全面的单元测试")


if __name__ == "__main__":
    main()