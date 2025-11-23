# require_confirmation 功能使用指南

## 概述

`require_confirmation` 功能为邮件 MCP 服务器添加了用户确认机制。支持全局环境变量配置和单次调用参数级控制，为不同使用场景提供灵活的确认策略。

## 功能特点

- ✅ 基于环境变量的全局确认开关
- ✅ 参数级确认控制，可覆盖全局设置
- ✅ 使用 FastMCP 的 `ctx.elicit()` 实现用户交互
- ✅ 详细的邮件信息预览
- ✅ 支持用户确认或取消操作
- ✅ 完整的错误处理和状态反馈
- ✅ 全面的单元测试覆盖

## 配置方法

### 1. 全局环境变量配置

在 `.env` 文件中添加或修改：

```env
# 启用邮件发送确认（全局设置）
REQUIRE_CONFIRMATION=true

# 禁用邮件发送确认（默认值）
# REQUIRE_CONFIRMATION=false
```

### 2. 参数级确认控制

在调用 `send_email` 工具时，可以通过 `require_confirmation` 参数覆盖全局设置：

```python
# 强制要求确认（覆盖全局设置）
send_email(
    to=["recipient@example.com"],
    subject="重要邮件",
    body="邮件内容",
    require_confirmation=True  # 强制确认
)

# 跳过确认（覆盖全局设置）
send_email(
    to=["recipient@example.com"],
    subject="批量通知",
    body="邮件内容",
    require_confirmation=False  # 跳过确认
)

# 使用全局设置（默认行为）
send_email(
    to=["recipient@example.com"],
    subject="普通邮件",
    body="邮件内容"
    # require_confirmation 参数未设置，使用全局配置
)
```

### 3. 重启服务器

修改环境变量配置后需要重启 MCP 服务器：

```bash
# 使用 uv 重启
uv run python -m email_mcp_server

# 或使用启动脚本
start_server.bat  # Windows
./start_server.sh  # Linux/macOS
```

## 使用场景

### 场景 1: 混合使用（推荐策略）

```env
REQUIRE_CONFIRMATION=true  # 全局启用确认作为安全默认
```

**适用情况：**
- 大部分邮件需要确认保护
- 特定邮件需要跳过确认（如系统通知）
- 关键邮件需要强制确认

**策略：**
```python
# 普通邮件使用全局确认设置
send_email(
    to=["user@example.com"],
    subject="会议通知",
    body="请准时参加会议"
)

# 系统通知跳过确认
send_email(
    to=["admin@company.com"],
    subject="系统监控报告",
    body="自动生成的监控报告",
    require_confirmation=False  # 覆盖全局设置
)

# 合同等重要邮件强制确认
send_email(
    to=["partner@company.com"],
    subject="合同文件",
    body="请查收附件中的合同文件",
    attachments=["contract.pdf"],
    require_confirmation=True  # 明确强制确认
)
```

### 场景 2: 交互式使用（全局启用）

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

### 场景 3: 自动化脚本（全局禁用，参数级控制）

```env
REQUIRE_CONFIRMATION=false  # 全局禁用确认
```

**适用情况：**
- 主要用于批量邮件发送
- 自动化工作流
- 定时任务
- 程序化邮件发送

**策略：**
```python
# 批量通知使用全局设置（跳过确认）
for recipient in email_list:
    send_email(
        to=[recipient],
        subject="批量通知",
        body="系统通知内容"
    )

# 但关键邮件仍然可以强制确认
send_email(
    to=["ceo@company.com"],
    subject="重要报告",
    body="请查收重要的业务报告",
    require_confirmation=True  # 强制确认
)
```

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

- **主功能实现**: `src/email_mcp_server/email_tools.py:93-115`
- **确认消息构建**: `src/email_mcp_server/email_tools.py:346-400`
- **辅助函数**: `src/email_mcp_server/email_tools.py:316-329`
- **配置管理**: `src/email_mcp_server/config.py:115`
- **模型扩展**: `src/email_mcp_server/models.py:217-220`
- **测试文件**:
  - `tests/test_require_confirmation.py` (全局功能测试)
  - `tests/test_parameter_confirmation.py` (参数级功能测试)

### 关键函数

#### `_should_require_confirmation(request_param: bool | None, global_setting: bool) -> bool`

确定是否需要用户确认的核心逻辑函数。

**参数：**
- `request_param`: 请求参数中的确认设置
- `global_setting`: 全局确认设置

**返回：**
- `bool`: 是否需要确认

**逻辑：**
- 参数级设置优先于全局设置
- `None` 参数表示使用全局设置

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

### 确认决策逻辑

```python
def _should_require_confirmation(request_param, global_setting):
    """
    确认决策逻辑：
    1. 如果参数明确设置，优先使用参数设置
    2. 如果参数为 None，使用全局设置
    """
    return request_param if request_param is not None else global_setting

# 在 send_email 工具中的应用
if _should_require_confirmation(request.require_confirmation, app_settings.require_confirmation):
    # 执行确认流程
    confirmation_result = await ctx.elicit(confirmation_msg, response_type=None)
    # 处理用户响应...
```

### 参数级���制实现

在 `SendEmailToolRequest` 模型中添加了可选的 `require_confirmation` 参数：

```python
class SendEmailToolRequest(BaseModel):
    # ... 其他字段 ...
    require_confirmation: bool | None = Field(
        default=None,
        description="是否需要用户确认发送。None表示使用全局设置，True表示强制要求确认，False表示跳过确认"
    )
```

## 测试

运行 `require_confirmation` 功能的测试：

```bash
# 运行全局功能测试
uv run pytest tests/test_require_confirmation.py -v

# 运行参数级功能测试
uv run pytest tests/test_parameter_confirmation.py -v

# 运行所有确认功能测试
uv run pytest tests/test_require_confirmation.py tests/test_parameter_confirmation.py -v

# 运行测试并生成覆盖率报告
uv run pytest tests/test_require_confirmation.py tests/test_parameter_confirmation.py --cov=email_mcp_server.email_tools --cov-report=term-missing
```

### 测试覆盖

**全局功能测试 (`test_require_confirmation.py`)：**
- ✅ 确认启用时的接受流程
- ✅ 确认启用时的取消流程
- ✅ 确认禁用时的直接发送
- ✅ 确认消息格式验证
- ✅ 不同邮件字段的处理
- ✅ 长内容的截断处理
- ✅ 附件信息的展示

**参数级功能测试 (`test_parameter_confirmation.py`)：**
- ✅ `_should_require_confirmation` 函数逻辑测试
- ✅ 参数 True 覆盖全局 False 设置
- ✅ 参数 False 覆盖全局 True 设置
- ✅ 参数 None 使用全局设置
- ✅ `SendEmailToolRequest` 模型参数验证
- ✅ 参数与全局设置的各种组合测试

## 故障排除

### 常见问题

1. **确认对话框不显示**
   - 检查全局设置 `REQUIRE_CONFIRMATION=true` 是否正确设置
   - 检查是否在调用时设置了 `require_confirmation=False`
   - 确认环境变量已加载
   - 重启 MCP 服务器

2. **邮件发送被意外取消**
   - 确认用户是否选择了"取消"操作
   - 检查客户端的确认界面是否正常工作
   - 验证参数设置是否符合预期

3. **参数级确认控制不生效**
   - 确认在调用 `send_email` 时正确传递了 `require_confirmation` 参数
   - 检查参数类型是否为 `bool` 类型
   - 验证 `_should_require_confirmation` 函数逻辑

4. **环境变量不生效**
   - 确认 `.env` 文件在项目根目录
   - 检查文件编码为 UTF-8
   - 重启服务器重新加载配置

### 调试技巧

1. **查看配置状态**
   ```python
   from email_mcp_server.config import get_app_settings
   settings = get_app_settings()
   print(f"全局 require_confirmation: {settings.require_confirmation}")
   ```

2. **测试确认消息构建**
   ```python
   from email_mcp_server.email_tools import _build_confirmation_message
   from email_mcp_server.models import SendEmailToolRequest

   request = SendEmailToolRequest(
       to=["test@example.com"],
       subject="Test",
       body="Test body",
       require_confirmation=True
   )
   print(_build_confirmation_message(request))
   ```

3. **调试确认决策逻辑**
   ```python
   from email_mcp_server.email_tools import _should_require_confirmation
   from email_mcp_server.config import get_app_settings

   settings = get_app_settings()

   # 测试不同的参数组合
   test_cases = [
       (True, True),   # 参数True, 全局True -> True
       (True, False),  # 参数True, 全局False -> True (参数优先)
       (False, True),  # 参数False, 全局True -> False (参数优先)
       (False, False), # 参数False, 全局False -> False
       (None, True),   # 参数None, 全局True -> True (使用全局)
       (None, False),  # 参数None, 全局False -> False (使用全局)
   ]

   for param, global_setting in test_cases:
       result = _should_require_confirmation(param, global_setting)
       print(f"参数: {param}, 全局: {global_setting} -> 结果: {result}")
   ```

## 安全考虑

- 启用确认功能可以有效防止误发邮件
- 建议在交互式环境中启用此功能
- 自动化脚本中应禁用以避免流程中断
- 确认消息包含敏感信息时应注意客户端环境的安全

## 版本信息

- **功能版本**: v1.2.0
- **兼容性**: FastMCP v0.4.0+
- **Python 版本**: 3.14+
- **测试覆盖率**: 100% (17个测试用例)
- **新增功能**: 参数级确认控制，支持单次调用覆盖全局设置

## 相关文档

- [项目 README](README.md)
- [CLAUDE.md](CLAUDE.md) - 开发指南
- [虚拟环境使用指南](虚拟环境使用指南.md)
- [测试计划](测试计划.md)