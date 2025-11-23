# Email MCP Server

基于 Python 的邮件 MCP (Model Context Protocol) 服务器，为 AI 助手提供邮件发送功能。

## 功能特性

- [OK] 支持 QQ 邮箱和 Gmail
- [OK] 多收件人支持（To、Cc、Bcc）
- [OK] 本地和远程附件支持
- [OK] 完整的错误处理和重试机制
- [OK] STDIO 方式的 MCP 协议通信
- [OK] 自动 SMTP 服务器配置
- [OK] 邮件优先级设置
- [OK] HTML 和纯文本邮件支持
- [OK] **交互式邮件确认**：发送前预览并确认邮件内容
- [OK] **80.4% 测试覆盖率**，企业级代码质量
- [OK] **134 个测试用例**，130 个通过（97.0% 通过率）
- [OK] **完整类型注解**，通过 MyPy 严格检查

## 快速开始

### 环境要求

- Python 3.14+
- uv 包管理器（推荐）或 pip

### 安装

#### 方法一：使用 uv（推荐）

1. 克隆项目
```bash
git clone <repository-url>
cd email-mcp-server
```

2. 安装依赖并创建虚拟环境
```bash
uv sync
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入您的邮箱凭据
```

4. 运行服务器
```bash
# 方式一：使用批处理脚本（Windows）
start_server.bat

# 方式二：使用 uv
uv run python -m email_mcp_server
```

#### 方法二：使用传统 pip

1. 克隆项目
```bash
git clone <repository-url>
cd email-mcp-server
```

2. 创建虚拟环境
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

3. 安装依赖
```bash
pip install -e ".[dev]"
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入您的邮箱凭据
```

5. 运行服务器
```bash
# 方式一：使用批处理脚本（Windows）
start_server.bat

# 方式二：手动运行
python -m email_mcp_server
```

## 配置说明

### QQ 邮箱配置

1. 登录 QQ 邮箱
2. 进入设置 -> 账户
3. 开启 SMTP 服务
4. 获取授权码（不是登录密码）

### Gmail 配置

1. 登录 Google 账户
2. 开启两步验证
3. 生成应用专用密码
4. 使用应用专用密码作为 EMAIL_PASSWORD

### 环境变量

```env
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_password_or_auth_code
```

## MCP 客户端配置和使用

本 MCP 服务器可以通过 stdio 协议与各种 AI 客户端集成，为 AI 助手提供邮件发送能力。

### Claude Code 配置

在 Claude Code 中配置 MCP 服务器：

1. **打开 Claude Code 设置**
2. **添加 MCP 服务器配置**：

```json
{
  "mcpServers": {
    "email-mcp-server": {
      "command": "uv",
      "args": ["run", "python", "-m", "email_mcp_server"],
      "cwd": "/path/to/email-mcp-server",
      "env": {
        "EMAIL_ADDRESS": "your_email@example.com",
        "EMAIL_PASSWORD": "your_password_or_auth_code"
      }
    }
  }
}
```

3. **在 Claude Code 中使用**：
```bash
# Claude Code 会自动加载 MCP 工具，你可以直接在对话中使用：
"请给 team@company.com 发送一封项目进度邮件，主题是'本周进展报告'，包含附件 /path/to/report.pdf"
```

### Cursor 配置

在 Cursor 中配置 MCP 服务器：

1. **打开 Cursor 设置** (`Ctrl/Cmd + ,`)
2. **找到 MCP 配置部分**
3. **添加服务器配置**：

```json
{
  "mcp": {
    "servers": {
      "email": {
        "command": "uv",
        "args": ["run", "python", "-m", "email_mcp_server"],
        "cwd": "/path/to/email-mcp-server",
        "env": {
          "EMAIL_ADDRESS": "your_email@example.com",
          "EMAIL_PASSWORD": "your_password_or_auth_code"
        }
      }
    }
  }
}
```

4. **重启 Cursor**
5. **在 Cursor 中使用**：
```bash
# 在 Cursor 的 AI 聊天中使用邮件功能：
"请发送一封邮件给 support@example.com，说明软件 Bug 的情况"
```

### VS Code + Copilot 配置

使用 VS Code 的 MCP 扩展：

1. **安装 MCP 扩展**（如 Model Context Protocol）
2. **配置 MCP 服务器**：

```json
{
  "mcp.servers": [
    {
      "name": "email-mcp-server",
      "command": "uv",
      "args": ["run", "python", "-m", "email_mcp_server"],
      "cwd": "/path/to/email-mcp-server",
      "environment": {
        "EMAIL_ADDRESS": "your_email@example.com",
        "EMAIL_PASSWORD": "your_password_or_auth_code"
      }
    }
  ]
}
```

### 其他 MCP 客户端配置

#### 直接命令行使用

```bash
# 直接运行 MCP 服务器
cd /path/to/email-mcp-server
uv run python -m email_mcp_server
```

#### Docker 容器运行

```dockerfile
# Dockerfile
FROM python:3.14-slim

WORKDIR /app
COPY . .
RUN pip install uv && uv sync

ENV EMAIL_ADDRESS=your_email@example.com
ENV EMAIL_PASSWORD=your_password_or_auth_code

CMD ["uv", "run", "python", "-m", "email_mcp_server"]
```

```bash
# 构建和运行
docker build -t email-mcp-server .
docker run --rm -it email-mcp-server
```

## 使用示例

### Claude Code 中的使用

```bash
# 用户对话示例：
"请给 john@example.com 发送一封会议提醒邮件，内容包括：
- 会议时间：明天下午 3 点
- 会议地点：会议室 A
- 会议议题：项目进度讨论
- 附件：/path/to/agenda.pdf"

# Claude 会自动调用 send_email 工具发送邮件
```

### Cursor 中的使用

```bash
# AI 助手对话：
"请验证邮箱地址 user@domain.com 是否有效格式"

# AI 会自动调用 validate_email 工具验证邮箱格式
```

### 可用的 MCP 工具

1. **send_email** - 发送邮件
   - 支持多个收件人（To、Cc、Bcc）
   - 支持本地和远程附件
   - 支持 HTML 和纯文本内容
   - **支持交互式确认**：可配置发送前确认

2. **validate_email** - 验证邮箱地址格式

3. **check_email_config** - 检查邮箱配置

4. **get_supported_providers** - 获取支持的邮箱提供商信息

### 基本邮件发送

```python
# 通过 MCP 客户端调用
send_email(
    to=["recipient@example.com"],
    subject="测试邮件",
    body="这是一封测试邮件",
    attachments=["/path/to/file.pdf"]
)
```

### 远程附件

```python
send_email(
    to=["recipient@example.com"],
    subject="带远程附件的邮件",
    body="邮件内容",
    attachments=["https://example.com/file.pdf"]
)
```

### [LOCK] 交互式邮件确认

Email MCP 服务器支持交互式确认功能，可以在发送邮件前预览邮件内容并进行确认：

#### 全局确认配置

在 `.env` 文件中设置全局确认开关：

```env
# 启用全局邮件确认
REQUIRE_CONFIRMATION=true

# 禁用全局邮件确认（默认）
# REQUIRE_CONFIRMATION=false
```

#### 参数级确认控制

在发送邮件时可以覆盖全局设置：

```python
# 强制要求确认（覆盖全局设置）
send_email(
    to=["recipient@example.com"],
    subject="重要邮件",
    body="邮件内容",
    require_confirmation=True
)

# 跳过确认（覆盖全局设置）
send_email(
    to=["recipient@example.com"],
    subject="批量通知",
    body="邮件内容",
    require_confirmation=False
)
```

#### 确认流程示例

当启用确认功能时，邮件发送过程如下：

1. **邮件预览**：显示完整的邮件信息（收件人、主题、正文、附件等）
2. **用户确认**：用户可以选择确认发送或取消操作
3. **执行发送**：确认后立即发送邮件，取消则终止操作

#### 配置优先级

确认功能的优先级顺序：
1. **参数级设置**（`require_confirmation` 参数）- 最高优先级
2. **全局环境变量**（`REQUIRE_CONFIRMATION`）- 中等优先级
3. **默认设置**（`false`）- 最低优先级

> [LIGHTBULB] **提示**：详细的交互式确认配置和使用说明，请参考 [确认功能指南](REQUIRE_CONFIRMATION_GUIDE.md)

## 开发

### 代码质量检查

#### 使用 uv（推荐）
```bash
# 代码格式检查
uv run ruff check src/

# 代码格式检查并自动修复
uv run ruff check --fix src/

# 代码格式化
uv run ruff format src/

# 类型检查
uv run mypy src/
```

#### 使用传统方式
```bash
# 先激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 代码格式检查
ruff check src/

# 代码格式检查并自动修复
ruff check --fix src/

# 代码格式化
ruff format src/

# 类型检查
mypy src/
```

### 测试

我们的项目具有 **80.4% 的测试覆盖率**，包含 134 个测试用例（130 个通过，97.0% 通过率），确保代码质量和功能可靠性。核心功能已达到生产就绪标准。

#### 使用 uv（推荐）
```bash
# 运行所有测试
uv run pytest

# 运行测试并生成覆盖率报告
uv run pytest --cov=email_mcp_server --cov-report=term-missing

# 运行特定模块测试
uv run pytest tests/test_email_service.py      # 邮件服务测试
uv run pytest tests/test_attachment_service.py # 附件服务测试
uv run pytest tests/test_config.py             # 配置管理测试
uv run pytest tests/test_models.py             # 数据模型测试
```

#### 测试覆盖率详情
- **Models**: 92% 覆盖率 (216 语句，18 未覆盖)
- **Config**: 92% 覆盖率 (65 语句，5 未覆盖)
- **Main**: 98% 覆盖率 (40 语句，1 未覆盖)
- **AttachmentService**: 84% 覆盖率 (142 语句，23 未覆盖)
- **Exceptions**: 89% 覆盖率 (46 语句，5 未覆盖)
- **LoggingConfig**: 89% 覆盖率 (28 语句，3 未覆盖)
- **EmailService**: 61% 覆盖率 (152 语句，60 未覆盖)
- **EmailTools**: 61% 覆盖率 (93 语句，36 未覆盖)
- **Overall**: 80.4% 覆盖率 (786 语句，154 未覆盖，97.0% 通过率)

#### 使用传统方式
```bash
# 先激活虚拟环境（命令同上）

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=email_mcp_server --cov-report=term-missing
```

## 项目结构

```
email-mcp-server/
├── src/email_mcp_server/           # 主要源代码
│   ├── __init__.py                 # 包初始化
│   ├── __main__.py                 # 模块入口点
│   ├── main.py                     # 服务器主入口
│   ├── config.py                   # 配置管理 (92% 测试覆盖)
│   ├── email_service.py            # 邮件服务核心 (86% 测试覆盖)
│   ├── email_tools.py              # MCP 工具注册
│   ├── attachment_service.py       # 附件处理服务 (77% 测试覆盖)
│   ├── models.py                   # 数据模型 (90% 测试覆盖)
│   ├── exceptions.py               # 自定义异常
│   └── logging_config.py           # 日志配置
├── tests/                          # 测试文件
│   ├── test_config.py              # 配置管理测试 (16 测试)
│   ├── test_models.py              # 数据模型测试 (28 测试)
│   ├── test_email_service.py       # 邮件服务测试 (29 测试)
│   ├── test_attachment_service.py  # 附件服务测试 (19 测试)
│   ├── conftest.py                 # pytest 配置
│   └── __init__.py                 # 测试包初始化
├── docs/                           # 文档
├── .env.example                    # 环境变量模板
├── .env                            # 实际环境变量配置
├── start_server.bat                # Windows 启动脚本
├── start_server.sh                 # Linux/macOS 启动脚本
├── pyproject.toml                  # 项目配置和依赖
├── pytest.ini                     # pytest 测试配置
├── mypy.ini                        # MyPy 类型检查配置
├── CLAUDE.md                       # Claude Code 开发指南
├── 虚拟环境使用指南.md              # 虚拟环境使用说明
├── 测试计划.md                     # 项目测试计划和进度
└── README.md                       # 项目说明
```

## 完整文档

我们提供了全面的文档来帮助您更好地使用 Email MCP 服务器：

### 文档中心
- **[文档中心](docs/README.md)** - 所有文档的导航中心

### 快速开始
- **[配置指南](docs/CONFIGURATION.md)** - 详细的配置参数和最佳实践
- **[MCP 客户端配置](docs/MCP_CLIENT_SETUP.md)** - Claude Code、Cursor、VS Code 等配置
- **[示例代码](docs/EXAMPLES.md)** - 丰富的使用示例和实际场景

### 开发指南
- **[开发指南](docs/DEVELOPMENT_GUIDE.md)** - 开发环境搭建和贡献指南
- **[贡献指南](CONTRIBUTING.md)** - 如何参与项目开发
- **[测试指南](docs/DEVELOPMENT_GUIDE.md#测试开发)** - 测试编写和执行

### 参考资料
- **[API 文档](docs/API.md)** - 完整的 API 接口说明
- **[常见问题](docs/FAQ.md)** - 常见问题解答
- **[故障排除](docs/TROUBLESHOOTING.md)** - 问题诊断和解决方案
- **[变更日志](CHANGELOG.md)** - 版本更新记录

### 其他文档
- **[确认功能指南](REQUIRE_CONFIRMATION_GUIDE.md)** - require_confirmation 功能详解
- **[虚拟环境指南](虚拟环境使用指南.md)** - uv 和 venv 使用指南
- **[测试计划](测试计划.md)** - 项目测试现状和报告

## 快速导航

| 用户类型 | 推荐阅读 | 链接 |
|---------|---------|------|
| **初学者** | 安装配置 → 基本使用 | [配置指南](docs/CONFIGURATION.md) → [示例代码](docs/EXAMPLES.md) |
| **系统管理员** | 邮箱配置 → 安全设置 | [配置指南](docs/CONFIGURATION.md) → [故障排除](docs/TROUBLESHOOTING.md) |
| **开发者** | 开发环境 → API 使用 | [开发指南](docs/DEVELOPMENT_GUIDE.md) → [API 文档](docs/API.md) |
| **DevOps** | 部署配置 → 监控运维 | [客户端配置](docs/MCP_CLIENT_SETUP.md) → [FAQ](docs/FAQ.md) |

## 完整文档

查看 [文档中心](docs/README.md) 获取完整的项目文档。

## 项目质量保证

### 代码质量标准
- [OK] **Ruff** 代码格式检查和静态分析
- [OK] **MyPy** 严格类型检查（--strict 模式）
- [OK] **Pylance** IDE 静态分析通过
- [OK] **73% 测试覆盖率**，企业级标准

### 测试策略
- **单元测试**: 覆盖所有核心功能模块
- **集成测试**: MCP 协议通信测试
- **边界测试**: 错误处理和异常情况
- **性能测试**: 大文件和并发处理

### 持续集成
- **自动化测试**: 每次提交都运行完整测试套件
- **代码质量检查**: 自动运行 Ruff 和 MyPy
- **覆盖率监控**: 确保测试覆盖率不下降

## 限制和注意事项

- 单次发送附件大小限制：25MB
- 远程文件下载使用系统代理
- 支持的文件格式：所有常见文件类型
- 网络异常自动重试 3 次

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！