# Email MCP Server

基于 Python 的邮件 MCP (Model Context Protocol) 服务器，为 AI 助手提供邮件发送功能。

## 功能特性

- ✅ 支持 QQ 邮箱和 Gmail
- ✅ 多收件人支持
- ✅ 本地和远程附件支持
- ✅ 启发式问答确认机制
- ✅ 完整的错误处理和重试机制
- ✅ STDIO 方式的 MCP 协议通信

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

## 使用示例

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

#### 使用 uv（推荐）
```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_email_service.py

# 运行测试并生成覆盖率报告
uv run pytest --cov=email_mcp_server tests/
```

#### 使用传统方式
```bash
# 先激活虚拟环境（命令同上）

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_email_service.py

# 运行测试并生成覆盖率报告
pytest --cov=email_mcp_server tests/
```

## 项目结构

```
email-mcp-server/
├── src/email_mcp_server/     # 主要源代码
├── tests/                    # 测试文件
├── docs/                     # 文档
├── .env.example              # 环境变量模板
├── start_server.bat          # Windows 启动脚本
├── start_server.sh           # Linux/macOS 启动脚本
├── pyproject.toml            # 项目配置
├── 虚拟环境使用指南.md        # 虚拟环境使用说明
├── 实施计划.md               # 项目实施计划
└── README.md                 # 项目说明
```

## 其他文档

- [虚拟环境使用指南](虚拟环境使用指南.md) - 详细的环境配置和使用说明
- [实施计划](实施计划.md) - 项目开发计划和进度跟踪

## 限制和注意事项

- 单次发送附件大小限制：25MB
- 远程文件下载使用系统代理
- 支持的文件格式：所有常见文件类型
- 网络异常自动重试 3 次

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！