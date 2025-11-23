# require_confirmation 功能使用指南

## 概述

`require_confirmation` 功能为邮件 MCP 服务器添加了用户确认机制。当启用此功能时，每次发送邮件前都会请求用户确认，防止误发重要邮件。

## 功能特点

- ✅ 基于环境变量控制的确认开关
- ✅ 使用 FastMCP 的 `ctx.elicit()` 实现用户交互
- ✅ 详细的邮件信息预览
- ✅ 支持用户确认或取消操作
- ✅ 完整的错误处理和状态反馈
- ✅ 全面的单元测试覆盖

## 配置方法

### 1. 环境变量配置

在 `.env` 文件中添加或修改：

```env
# 启用邮件发送确认
REQUIRE_CONFIRMATION=true

# 禁用邮件发送确认（默认值）
# REQUIRE_CONFIRMATION=false
```

### 2. 重启服务器

修改配置后需要重启 MCP 服务器：

```bash
# 使用 uv 重启
uv run python -m email_mcp_server

# 或使用启动脚本
start_server.bat  # Windows
./start_server.sh  # Linux/macOS
```

## 使用场景

### 场景 1: 交互式使用（推荐启用）

```env
REQUIRE_CONFIRMATION=true
```

**适用情况：**
- 手动发送重要邮件
- 开发和测试环境
- 需要额外安全确认的场景
- 防止误操作

**流程：**
1. 用户调用 `send_email` 工具
2. 系统显示确认对话框
3. 用户确认邮件信息
4. 选择"发送"或"取消"
5. 系统执行相应操作

### 场景 2: 自动化脚本（推荐禁用）

```env
REQUIRE_CONFIRMATION=false
```

**适用情况：**
- 批量邮件发送
- 自动化工作流
- 定时任务
- 程序化邮件发送

**流程：**
1. 程序调用 `send_email` 工具
2. 系统直接发送邮件
3. 无需用户干预

## 确认消息格式

当启用确认功能时，系统会显示包含以下信息的确认消息：

```
📧 准备发送邮件
========================================
📋 主题: 邮件主题
👥 收件人: recipient1@example.com, recipient2@example.com
📄 抄送: cc@example.com
🔒 密送: bcc@example.com
↩️ 回复至: reply@example.com
⚡ 优先级: 高
📝 内容预览: 邮件内容的前100个字符...
📎 附件数量: 2
   1. file1.pdf
   2. file2.doc
========================================
⚠️  请确认是否发送此邮件？
```

## API 响应

### 用户确认发送

```json
{
    "success": true,
    "message": "Email sent successfully!",
    "message_id": "unique-message-id",
    "recipients_count": 2,
    "attachments_processed": 1,
    "status": "sent"
}
```

### 用户取消发送

```json
{
    "success": false,
    "error": "Email sending cancelled by user",
    "error_code": "USER_CANCELLED",
    "status": "cancelled"
}
```

## 技术实现

### 核心代码位置

- **主功能实现**: `src/email_mcp_server/email_tools.py:90-109`
- **确认消息构建**: `src/email_mcp_server/email_tools.py:307-358`
- **配置管理**: `src/email_mcp_server/config.py:115`
- **测试文件**: `tests/test_require_confirmation.py`

### 关键函数

#### `_build_confirmation_message(request: SendEmailToolRequest) -> str`

构建用户友好的确认消息，包含邮件的所有重要信息。

**参数：**
- `request`: 邮件发送请求对象

**返回：**
- 格式化的确认消息字符串

### FastMCP 集成

使用 FastMCP 的 `ctx.elicit()` 方法实现用户交互：

```python
# 请求用户确认
confirmation_result = await ctx.elicit(
    confirmation_msg,
    response_type=None  # 不需要特定响应类型，只需要确认/拒绝
)

# 检查用户响应
if confirmation_result.action != "accept":
    return {
        "success": False,
        "error": "Email sending cancelled by user",
        "error_code": "USER_CANCELLED",
        "status": "cancelled",
    }
```

## 测试

运行 `require_confirmation` 功能的测试：

```bash
# 运行特定测试
uv run pytest tests/test_require_confirmation.py -v

# 运行测试并生成覆盖率报告
uv run pytest tests/test_require_confirmation.py --cov=email_mcp_server.email_tools --cov-report=term-missing
```

### 测试覆盖

- ✅ 确认启用时的接受流程
- ✅ 确认启用时的取消流程
- ✅ 确认禁用时的直接发送
- ✅ 确认消息格式验证
- ✅ 不同邮件字段的处理
- ✅ 长内容的截断处理
- ✅ 附件信息的展示

## 故障排除

### 常见问题

1. **确认对话框不显示**
   - 检查 `REQUIRE_CONFIRMATION=true` 是否正确设置
   - 确认环境变量已加载
   - 重启 MCP 服务器

2. **邮件发送被意外取消**
   - 确认用户是否选择了"取消"操作
   - 检查客户端的确认界面是否正常工作

3. **环境变量不生效**
   - 确认 `.env` 文件在项目根目录
   - 检查文件编码为 UTF-8
   - 重启服务器重新加载配置

### 调试技巧

1. **查看配置状态**
   ```python
   from email_mcp_server.config import get_app_settings
   settings = get_app_settings()
   print(f"require_confirmation: {settings.require_confirmation}")
   ```

2. **测试确认消息构建**
   ```python
   from email_mcp_server.email_tools import _build_confirmation_message
   from email_mcp_server.models import SendEmailToolRequest

   request = SendEmailToolRequest(
       to=["test@example.com"],
       subject="Test",
       body="Test body"
   )
   print(_build_confirmation_message(request))
   ```

## 安全考虑

- 启用确认功能可以有效防止误发邮件
- 建议在交互式环境中启用此功能
- 自动化脚本中应禁用以避免流程中断
- 确认消息包含敏感信息时应注意客户端环境的安全

## 版本信息

- **功能版本**: v1.1.0
- **兼容性**: FastMCP v0.4.0+
- **Python 版本**: 3.14+
- **测试覆盖率**: 100%

## 相关文档

- [项目 README](README.md)
- [CLAUDE.md](CLAUDE.md) - 开发指南
- [虚拟环境使用指南](虚拟环境使用指南.md)
- [测试计划](测试计划.md)