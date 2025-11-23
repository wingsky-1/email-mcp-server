# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个基于 Python 实现的邮件 MCP (Model Context Protocol) 服务器，通过 MCP 协议提供邮件发送功能。项目已完成核心功能实现，包括完整的邮件发送、附件处理和配置管理。

## 技术栈

- **Python**: 3.14 (通过 uv 管理)
- **框架**: Pydantic + FastMCP
- **环境**: UTF-8 无 BOM 编码
- **进程**: MCP 服务器通过 stdio 运行
- **版本控制**: Git
- **代码质量**: Ruff + MyPy + Pylance

## 已实现功能

### 核心功能
- [OK] 支持 QQ 邮箱和 Gmail 的邮件发送功能
- [OK] 内置两种邮箱的 SMTP 服务器配置（自动检测）
- [OK] 通过环境变量配置邮箱凭据
- [OK] 支持多个收件人、抄送、密送
- [OK] 支持附件（本地文件和远程 URL）
- [OK] 完整的错误处理和重试机制
- [OK] 基于 stdio 的 MCP 服务器启动

### 高级功能
- [OK] 完整的日志系统
- [OK] 配置管理和验证
- [OK] 邮箱地址验证
- [OK] 连接测试功能
- [OK] 远程附件下载（带重试机制）
- [OK] 邮件优先级设置
- [OK] HTML 和纯文本邮件支持

### 代码质量
- [OK] 完整的类型注解（Python 3.14+ 语法）
- [OK] Ruff 代码格式检查和静态分析
- [OK] MyPy 严格类型检查（--strict 模式）
- [OK] Pylance IDE 静态分析通过
- [OK] **73% 测试覆盖率**，企业级标准
- [OK] **99 个测试用例**，覆盖核心功能
- [OK] 完整的 CI/CD 质量保证流程

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
│   ├── exceptions.py               # 自定义异常 (83% 测试覆盖)
│   └── logging_config.py           # 日志配置
├── tests/                          # 测试文件 (73% 总覆盖率)
│   ├── test_config.py              # 配置管理测试 (16/16 通过)
│   ├── test_models.py              # 数据模型测试 (28/28 通过)
│   ├── test_email_service.py       # 邮件服务测试 (22/29 通过)
│   ├── test_attachment_service.py  # 附件服务测试 (9/19 通过)
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

## 开发命令

### 环境管理
```bash
# 使用 uv 同步依赖（推荐）
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 运行服务器
```bash
# 使用 uv 运行（推荐）
uv run python -m email_mcp_server

# 使用启动脚本
start_server.bat            # Windows
./start_server.sh          # Linux/macOS

# 直接运行 Python 模块
python -m email_mcp_server
```

### 代码质量检查
```bash
# Ruff 代码检查
uv run ruff check src/

# Ruff 自动修复
uv run ruff check --fix src/

# Ruff 格式化
uv run ruff format src/

# MyPy 类型检查
uv run mypy src/

# Pylance 检查（通过 VS Code 或编辑器集成）
# 确保所有代码通过 Pylance 静态分析
```

### 测试
```bash
# 运行所有测试（73% 覆盖率，99 个测试）
uv run pytest

# 运行测试并生成覆盖率报告
uv run pytest --cov=email_mcp_server --cov-report=term-missing

# 运行特定模块测试
uv run pytest tests/test_config.py             # 配置管理 (100% 通过)
uv run pytest tests/test_models.py             # 数据模型 (100% 通过)
uv run pytest tests/test_email_service.py       # 邮件服务 (76% 通过)
uv run pytest tests/test_attachment_service.py  # 附件服务 (47% 通过)

# 运行测试并生成 HTML 覆盖率报告
uv run pytest --cov=email_mcp_server --cov-report=html tests/
```

## 已实现的关键要求

### 邮箱支持
- 支持 QQ 邮箱 (@qq.com) 和 Gmail (@gmail.com) 地址
- SMTP 配置自动检测：
  - QQ 邮箱：smtp.qq.com:587 (TLS)
  - Gmail：smtp.gmail.com:587 (TLS)
- 手动 SMTP 配置支持（通过环境变量）

### 附件处理
- 本地文件：支持绝对和相对路径
- 远程文件：URL 下载，使用系统代理，重试 3 次
- 单次发送附件大小限制：25MB
- 支持所有常见文件类型

### 配置管理
- 邮箱凭据从环境变量读取：
  - `EMAIL_ADDRESS`: 邮箱地址
  - `EMAIL_PASSWORD`: 密码或授权码
- .env 文件支持测试配置
- 支持手动 SMTP 配置覆盖
- 完整的配置验证和错误提示

### MCP 工具
- `send_email`: 发送邮件（支持所有功能）
- `check_email_config`: 检查邮箱配置和连接测试
- `validate_email`: 验证邮箱地址格式
- `get_supported_providers`: 获取支持的邮箱提供商信息

## 代码质量标准

### 必须通过的质量检查
1. **Pylance 静态分析**: 所有代码必须通过 Pylance 检查，无警告和错误
2. **Ruff 代码检查**: 遵循 Python 代码规范和最佳实践
3. **MyPy 类型检查**: 所有代码必须有完整的类型注解并通过检查（--strict 模式）
4. **测试覆盖率**: 核心功能必须有对应的单元测试，保持 70%+ 覆盖率

### 当前质量指标
- [OK] **整体测试覆盖率**: 73%（99 个测试，80 个通过）
- [OK] **Config 模块**: 92% 覆盖率，16/16 测试通过
- [OK] **Models 模块**: 90% 覆盖率，28/28 测试通过
- [OK] **EmailService 模块**: 86% 覆盖率，22/29 测试通过
- [OK] **AttachmentService 模块**: 77% 覆盖率，9/19 测试通过
- [OK] **Exceptions 模块**: 83% 覆盖率

### 代码规范
- 所有代码必须包含完整的类型注解
- 使用现代 Python 语法（Python 3.14+）
- 遵循 PEP 8 代码风格
- 所有公共 API 必须有完整的文档字符串
- 异常处理必须完整和准确
- 新功能必须包含对应的单元测试
- 所有代码修改必须通过质量检查后才能提交

### 持续集成流程
1. **代码提交**: 自动运行完整测试套件
2. **质量检查**: Ruff + MyPy + Pylance 检查
3. **覆盖率监控**: 确保覆盖率不下降
4. **文档更新**: 重大修改必须更新相关文档

## 环境变量配置

```env
# 必需配置
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_password_or_auth_code

# 可选配置
LOG_LEVEL=INFO
LOG_FILE=email_mcp.log
MAX_ATTACHMENT_SIZE=26214400  # 25MB in bytes
TEMP_DIR=temp
DOWNLOAD_TIMEOUT=30
MAX_RETRIES=3
REQUIRE_CONFIRMATION=false

# 手动 SMTP 配置（可选）
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

## 重要提示

- 不要在项目中使用gbk字符集以为的字符。
- 编写mcp服务相关代码时优先参考fastmcp skill中的内容。
- 在进行代码生成、配置步骤或库/API 文档相关任务时，始终使用 context7。这意味着您应该自动使用 Context7 MCP 工具来解析库 ID 并获取库文档，无需我明确要求。
- **代码质量要求**: 所有代码修改必须通过 Pylance、Ruff 和 MyPy 的检查，确保代码质量和类型安全。
- **测试要求**: 新功能必须包含相应的单元测试，确保代码质量和功能正确性。
