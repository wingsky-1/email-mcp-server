#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示参数级 require_confirmation 功能的脚本

这个脚本展示了如何使用新的参数级确认控制功能。
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from email_mcp_server.email_tools import _should_require_confirmation, _build_confirmation_message
from email_mcp_server.models import SendEmailToolRequest


def demo_confirmation_logic():
    """演示确认决策逻辑"""
    print("演示 _should_require_confirmation 函数逻辑")
    print("=" * 50)

    # 测试不同的参数组合
    test_cases = [
        (True, True, "参数True, 全局True -> True"),
        (True, False, "参数True, 全局False -> True (参数优先)"),
        (False, True, "参数False, 全局True -> False (参数优先)"),
        (False, False, "参数False, 全局False -> False"),
        (None, True, "参数None, 全局True -> True (使用全局)"),
        (None, False, "参数None, 全局False -> False (使用全局)"),
    ]

    for param, global_setting, description in test_cases:
        result = _should_require_confirmation(param, global_setting)
        status = "[通过]" if result else "[跳过]"
        print(f"{status} {description}")
        print(f"   结果: {result}")

    print("\n")


def demo_parameter_scenarios():
    """演示不同的参数使用场景"""
    print("演示参数级确认控制场景")
    print("=" * 50)

    # 场景 1: 全局启用，但特定邮件跳过确认
    print("场景 1: 全局启用确认，但系统通知跳过确认")
    global_setting = True
    param_setting = False

    needs_confirmation = _should_require_confirmation(param_setting, global_setting)
    print(f"全局设置: {global_setting}, 参数设置: {param_setting}")
    print(f"最终结果: {'需要确认' if needs_confirmation else '跳过确认'}")
    print("[适用] 系统通知、自动化报告等")
    print()

    # 场景 2: 全局禁用，但重要邮件强制确认
    print("场景 2: 全局禁用确认，但重要邮件强制确认")
    global_setting = False
    param_setting = True

    needs_confirmation = _should_require_confirmation(param_setting, global_setting)
    print(f"全局设置: {global_setting}, 参数设置: {param_setting}")
    print(f"最终结果: {'需要确认' if needs_confirmation else '跳过确认'}")
    print("适用: 合同文件、重要通知等")
    print()

    # 场景 3: 使用全局设置
    print("场景 3: 普通邮件使用全局设置")
    global_setting = True
    param_setting = None

    needs_confirmation = _should_require_confirmation(param_setting, global_setting)
    print(f"全局设置: {global_setting}, 参数设置: {param_setting}")
    print(f"最终结果: {'需要确认' if needs_confirmation else '跳过确认'}")
    print("[适用] 日常邮件、普通通知等")
    print()


async def demo_email_requests():
    """演示不同确认设置的邮件请求"""
    print("演示不同确认设置的邮件请求")
    print("=" * 50)

    # 创建基础邮件请求
    base_request_data = {
        "to": ["user@example.com"],
        "subject": "测试邮件",
        "body": "这是一封测试邮件",
    }

    # 场景 1: 强制确认
    print("场景 1: 强制确认的邮件")
    request1 = SendEmailToolRequest(**base_request_data, require_confirmation=True)
    print(f"require_confirmation: {request1.require_confirmation}")
    print(f"邮件主题: {request1.subject}")
    print("用途: 合同、重要通知、财务报告等")
    print()

    # 场景 2: 跳过确认
    print("场景 2: 跳过确认的邮件")
    request2 = SendEmailToolRequest(**base_request_data, require_confirmation=False)
    print(f"require_confirmation: {request2.require_confirmation}")
    print(f"邮件主题: {request2.subject}")
    print("用途: 系统通知、自动报告、批量邮件等")
    print()

    # 场景 3: 使用全局设置
    print("场景 3: 使用全局设置的邮件")
    request3 = SendEmailToolRequest(**base_request_data)  # 默认为 None
    print(f"require_confirmation: {request3.require_confirmation}")
    print(f"邮件主题: {request3.subject}")
    print("用途: 日常邮件、普通沟通等")
    print()


def demo_mixed_usage_strategy():
    """演示混合使用策略"""
    print("推荐的混合使用策略")
    print("=" * 50)

    print("环境配置:")
    print("REQUIRE_CONFIRMATION=true  # 全局启用确认作为安全默认")
    print()

    print("代码策略:")
    print("# 1. 普通邮件 - 使用全局设置")
    print("send_email(to=['user@example.com'], subject='会议通知', body='...')")
    print()

    print("# 2. 系统通知 - 跳过确认")
    print("send_email(to=['admin@company.com'], subject='监控报告', body='...', require_confirmation=False)")
    print()

    print("# 3. 重要邮件 - 强制确认（明确表达意图）")
    print("send_email(to=['partner@company.com'], subject='合同文件', body='...', require_confirmation=True)")
    print()

    print("优势:")
    print("[1] 安全默认: 大部分邮件需要确认保护")
    print("[2] 灵活控制: 特定邮件可以跳过确认")
    print("[3] 明确意图: 重要邮件可以强制确认")
    print("[4] 向后兼容: 不影响现有代码")
    print()


def main():
    """主函数"""
    print("参数级 require_confirmation 功能演示")
    print("=" * 60)
    print()

    # 演示确认逻辑
    demo_confirmation_logic()

    # 演示参数场景
    demo_parameter_scenarios()

    # 演示邮件请求
    asyncio.run(demo_email_requests())

    # 演示混合使用策略
    demo_mixed_usage_strategy()

    print("参数级控制的优势:")
    print("1. 灵活性: 可以在单次调用中覆盖全局设置")
    print("2. 安全性: 全局启用确认作为安全默认")
    print("3. 效率: 特定场景可以跳过确认提升效率")
    print("4. 明确性: 重要操作可以强制确认表达意图")
    print("5. 兼容性: 完全向后兼容现有代码")


if __name__ == "__main__":
    main()