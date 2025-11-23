# Email MCP 服务器 API 文档

本文档详细描述了 Email MCP 服务器的所有 API 接口和数据模型。

## 概述

Email MCP 服务器通过 MCP (Model Context Protocol) 协议提供邮件发送功能。服务器支持：

- 多种邮箱提供商（QQ邮箱、Gmail）
- 邮件发送（支持附件、HTML格式）
- 邮箱地址验证
- 配置检查和连接测试

## MCP 工具接口

### 1. send_email

发送邮件的主要工具，支持所有邮件发送功能。

#### 参数

```python
@tool()
def send_email(
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[str]] = None,
    body_format: Optional[str] = "plain",
    priority: Optional[int] = 3
) -> Dict[str, Any]
```

**参数说明:**

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `to` | List[str] | ✅ | - | 收件人邮箱地址列表 |
| `subject` | str | ✅ | - | 邮件主题 |
| `body` | str | ✅ | - | 邮件正文内容 |
| `cc` | List[str] | ❌ | None | 抄送邮箱地址列表 |
| `bcc` | List[str] | ❌ | None | 密送邮箱地址列表 |
| `attachments` | List[str] | ❌ | None | 附件路径列表（支持本地文件和远程URL） |
| `body_format` | str | ❌ | "plain" | 邮件格式：`"plain"`（纯文本）或 `"html"`（HTML） |
| `priority` | int | ❌ | 3 | 邮件优先级：1（最高）- 5（最低） |

**返回值:**

```python
{
    "success": bool,           # 是否发送成功
    "message": str,            # 状态消息
    "message_id": Optional[str], # 邮件ID（如果成功）
    "attachments": Optional[List[Dict[str, Any]]] # 附件处理结果
}
```

**使用示例:**

```json
{
    "to": ["recipient@example.com", "team@example.com"],
    "subject": "项目进度报告",
    "body": "<h1>本周进展</h1><p>项目已完成80%...</p>",
    "body_format": "html",
    "cc": ["manager@example.com"],
    "attachments": ["/path/to/report.pdf", "https://example.com/data.xlsx"],
    "priority": 2
}
```

### 2. validate_email

验证邮箱地址格式是否正确。

#### 参数

```python
@tool()
def validate_email(email: str) -> Dict[str, Any]
```

**参数说明:**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `email` | str | ✅ | 要验证的邮箱地址 |

**返回值:**

```python
{
    "valid": bool,        # 是否有效
    "email": str,         # 原始邮箱地址
    "normalized": str,    # 标准化后的邮箱地址
    "message": str        # 验证结果消息
}
```

**使用示例:**

```json
{
    "email": "user@example.com"
}
```

### 3. check_email_config

检查邮箱配置和连接状态。

#### 参数

此工具无需参数。

**返回值:**

```python
{
    "configured": bool,                   # 是否已配置
    "email_address": str,                 # 配置的邮箱地址
    "provider": str,                      # 邮箱提供商
    "connection_test": Dict[str, Any],    # 连接测试结果
    "smtp_config": Dict[str, Any]         # SMTP配置信息
}
```

**连接测试结果:**

```python
{
    "success": bool,           # 连接是否成功
    "message": str,            # 状态消息
    "response_time": float,    # 响应时间（秒）
    "error": Optional[str]     # 错误信息（如果有）
}
```

### 4. get_supported_providers

获取支持的邮箱提供商信息。

#### 参数

此工具无需参数。

**返回值:**

```python
{
    "providers": List[Dict[str, Any]]  # 提供商信息列表
}
```

**提供商信息:**

```python
{
    "name": str,              # 提供商名称
    "domains": List[str],     # 支持的域名
    "smtp_server": str,       # SMTP服务器地址
    "smtp_port": int,         # SMTP端口
    "use_tls": bool,          # 是否使用TLS
    "use_ssl": bool,          # 是否使用SSL
    "description": str        # 描述信息
}
```

## 数据模型

### SendEmailToolRequest

邮件发送工具的请求数据模型。

```python
class SendEmailToolRequest(BaseModel):
    """邮件发送工具请求模型"""

    to: List[str] = Field(..., description="收件人邮箱地址列表")
    subject: str = Field(..., min_length=1, max_length=200, description="邮件主题")
    body: str = Field(..., min_length=1, description="邮件正文内容")
    cc: Optional[List[str]] = Field(None, description="抄送邮箱地址列表")
    bcc: Optional[List[str]] = Field(None, description="密送邮箱地址列表")
    attachments: Optional[List[str]] = Field(None, description="附件路径列表")
    body_format: Optional[str] = Field("plain", regex="^(plain|html)$", description="邮件格式")
    priority: Optional[int] = Field(3, ge=1, le=5, description="邮件优先级")
```

### EmailMessage

邮件消息数据模型。

```python
class EmailMessage(BaseModel):
    """邮件消息模型"""

    to: List[str] = Field(..., description="收件人列表")
    cc: Optional[List[str]] = Field(None, description="抄送列表")
    bcc: Optional[List[str]] = Field(None, description="密送列表")
    subject: str = Field(..., description="邮件主题")
    body: str = Field(..., description="邮件正文")
    body_format: str = Field("plain", description="邮件格式")
    priority: int = Field(3, description="邮件优先级")
    attachments: List["Attachment"] = Field(default_factory=list, description="附件列表")

    def to_mime_message(self) -> MIMEMultipart:
        """转换为MIME消息对象"""
        pass
```

### Attachment

附件数据模型。

```python
class Attachment(BaseModel):
    """附件模型"""

    path: str = Field(..., description="附件路径")
    name: Optional[str] = Field(None, description="附件名称")
    size: int = Field(..., description="附件大小（字节）")
    content_type: Optional[str] = Field(None, description="内容类型")

    @classmethod
    def from_path(cls, path: str) -> "Attachment":
        """从路径创建附件对象"""
        pass
```

### EmailSettings

邮箱配置数据模型。

```python
class EmailSettings(BaseSettings):
    """邮箱配置模型"""

    address: str = Field(..., description="邮箱地址")
    password: str = Field(..., description="邮箱密码或授权码")
    provider: Optional[EmailProvider] = Field(None, description="邮箱提供商")
    smtp_server: Optional[str] = Field(None, description="SMTP服务器")
    smtp_port: Optional[int] = Field(None, description="SMTP端口")
    use_tls: Optional[bool] = Field(None, description="是否使用TLS")
    use_ssl: Optional[bool] = Field(None, description="是否使用SSL")

    class Config:
        env_prefix = "EMAIL_"
        extra = "ignore"
```

## 错误处理

### 错误代码

服务器使用标准化的错误码和错误信息：

| 错误代码 | HTTP状态码 | 描述 |
|----------|------------|------|
| `INVALID_EMAIL_FORMAT` | 400 | 邮箱地址格式无效 |
| `EMAIL_SEND_FAILED` | 500 | 邮件发送失败 |
| `ATTACHMENT_ERROR` | 400 | 附件处理错误 |
| `SMTP_CONNECTION_ERROR` | 500 | SMTP连接错误 |
| `CONFIGURATION_ERROR` | 500 | 配置错误 |
| `AUTHENTICATION_ERROR` | 401 | 认证失败 |
| `RATE_LIMIT_EXCEEDED` | 429 | 频率限制超出 |

### 错误响应格式

```python
{
    "error": {
        "code": "ERROR_CODE",
        "message": "错误描述",
        "details": Optional[Dict[str, Any]]
    }
}
```

### 错误类型

#### EmailValidationError

邮箱验证错误，继承自 `EmailMCPServerError`。

```python
class EmailValidationError(EmailMCPServerError):
    """邮箱验证错误"""
    pass
```

#### EmailServiceError

邮件服务错误，继承自 `EmailMCPServerError`。

```python
class EmailServiceError(EmailMCPServerError):
    """邮件服务错误"""
    pass
```

#### AttachmentError

附件处理错误，继承自 `EmailMCPServerError`。

```python
class AttachmentError(EmailMCPServerError):
    """附件处理错误"""
    pass
```

## 配置参数

### 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `EMAIL_ADDRESS` | ✅ | - | 邮箱地址 |
| `EMAIL_PASSWORD` | ✅ | - | 邮箱密码或授权码 |
| `SMTP_SERVER` | ❌ | 自动检测 | SMTP服务器地址 |
| `SMTP_PORT` | ❌ | 自动检测 | SMTP端口 |
| `SMTP_USE_TLS` | ❌ | True | 是否使用TLS |
| `SMTP_USE_SSL` | ❌ | False | 是否使用SSL |
| `LOG_LEVEL` | ❌ | INFO | 日志级别 |
| `LOG_FILE` | ❌ | email_mcp.log | 日志文件 |
| `MAX_ATTACHMENT_SIZE` | ❌ | 26214400 | 最大附件大小（字节） |
| `TEMP_DIR` | ❌ | temp | 临时目录 |
| `DOWNLOAD_TIMEOUT` | ❌ | 30 | 下载超时时间（秒） |
| `MAX_RETRIES` | ❌ | 3 | 最大重试次数 |
| `REQUIRE_CONFIRMATION` | ❌ | False | 是否需要确认 |

### 自动检测的邮箱提供商

#### Gmail (@gmail.com)

- **SMTP服务器**: smtp.gmail.com
- **端口**: 587 (TLS) 或 465 (SSL)
- **认证**: 应用专用密码

#### QQ邮箱 (@qq.com)

- **SMTP服务器**: smtp.qq.com
- **端口**: 587 (TLS) 或 465 (SSL)
- **认证**: 授权码

## 使用示例

### 基本邮件发送

```json
{
    "tool": "send_email",
    "arguments": {
        "to": ["recipient@example.com"],
        "subject": "测试邮件",
        "body": "这是一封测试邮件。"
    }
}
```

### HTML邮件发送

```json
{
    "tool": "send_email",
    "arguments": {
        "to": ["user@example.com"],
        "subject": "HTML邮件",
        "body": "<h1>标题</h1><p>HTML内容...</p>",
        "body_format": "html"
    }
}
```

### 带附件的邮件

```json
{
    "tool": "send_email",
    "arguments": {
        "to": ["recipient@example.com"],
        "subject": "带附件的邮件",
        "body": "请查看附件。",
        "attachments": ["/path/to/file.pdf", "https://example.com/image.png"]
    }
}
```

### 多收件人邮件

```json
{
    "tool": "send_email",
    "arguments": {
        "to": ["primary@example.com", "secondary@example.com"],
        "cc": ["manager@example.com"],
        "bcc": ["archive@example.com"],
        "subject": "团队通知",
        "body": "团队会议安排...",
        "priority": 1
    }
}
```

### 邮箱验证

```json
{
    "tool": "validate_email",
    "arguments": {
        "email": "user@example.com"
    }
}
```

### 配置检查

```json
{
    "tool": "check_email_config",
    "arguments": {}
}
```

## 性能考虑

### 附件限制

- **单次发送附件总大小**: 25MB
- **单个附件大小**: 25MB
- **附件数量**: 理论上无限制，实际受邮件服务商限制

### 连接管理

- **连接池**: 支持连接复用
- **超时时间**: 默认30秒
- **重试机制**: 自动重试3次

### 内存使用

- **附件处理**: 流式处理大文件
- **临时文件**: 自动清理
- **内存监控**: 防止内存泄漏

## 安全考虑

### 凭据安全

- **敏感信息**: 通过环境变量传递
- **日志记录**: 不记录敏感信息
- **内存清理**: 及时清理密码等敏感数据

### 附件安全

- **路径验证**: 防止路径遍历攻击
- **文件类型**: 支持所有文件类型
- **病毒扫描**: 不提供（需要外部集成）

### 网络安全

- **TLS/SSL**: 强制使用加密连接
- **证书验证**: 验证SMTP服务器证书
- **代理支持**: 使用系统代理配置

---

此API文档涵盖了Email MCP服务器的所有功能和使用方法。如有疑问，请参考[用户指南](../README.md)或提交Issue。