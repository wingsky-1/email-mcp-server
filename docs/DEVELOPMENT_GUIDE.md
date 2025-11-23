# Email MCP 服务器开发指南

本指南面向希望参与 Email MCP 服务器开发的开发者，包含开发环境搭建、代码结构、开发流程和最佳实践。

## 📋 目录

- [开发环境搭建](#开发环境搭建)
- [项目结构](#项目结构)
- [代码架构](#代码架构)
- [开发流程](#开发流程)
- [测试开发](#测试开发)
- [调试技巧](#调试技巧)
- [性能优化](#性能优化)
- [发布流程](#发布流程)
- [开发最佳实践](#开发最佳实践)

## 🚀 开发环境搭建

### 系统要求
- **Python**: 3.14+
- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **内存**: 最少 1GB，推荐 2GB
- **存储**: 最少 1GB 可用空间

### 环境准备

#### 1. 克隆项目
```bash
# 克隆项目仓库
git clone https://github.com/your-org/email-mcp-server.git
cd email-mcp-server

# 或者 Fork 后克隆
git clone https://github.com/YOUR_USERNAME/email-mcp-server.git
cd email-mcp-server
```

#### 2. 安装 uv（推荐）
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证安装
uv --version
```

#### 3. 设置开发环境
```bash
# 同步依赖（包括开发依赖）
uv sync --dev

# 激活虚拟环境
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 验证环境
uv run python -c "import email_mcp_server; print('导入成功')"
```

#### 4. 配置开发环境变量
```bash
# 复制配置文件
cp .env.example .env

# 编辑配置（使用测试邮箱）
nano .env
```

```env
# 开发环境配置示例
EMAIL_ADDRESS=dev@example.com
EMAIL_PASSWORD=dev_password
LOG_LEVEL=DEBUG
REQUIRE_CONFIRMATION=true
```

#### 5. 验证开发环境
```bash
# 运行测试套件
uv run pytest

# 检查代码质量
uv run ruff check src/
uv run mypy src/

# 启动开发服务器
uv run python -m email_mcp_server
```

### IDE 配置

#### VS Code 配置
创建 `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".mypy_cache": true,
        ".ruff_cache": true
    }
}
```

创建 `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "启动 Email MCP 服务器",
            "type": "python",
            "request": "launch",
            "program": "-m",
            "args": ["email_mcp_server"],
            "console": "integratedTerminal",
            "env": {
                "LOG_LEVEL": "DEBUG"
            }
        }
    ]
}
```

#### PyCharm 配置
1. **设置 Python 解释器**:
   - File → Settings → Project → Python Interpreter
   - 选择 `.venv/bin/python`

2. **配置代码检查**:
   - Settings → Tools → External Tools
   - 添加 Ruff 和 MyPy

3. **配置测试运行器**:
   - Settings → Tools → Python Integrated Tools
   - Default test runner: pytest

## 🏗️ 项目结构

### 目录结构详解
```
email-mcp-server/
├── src/email_mcp_server/           # 主要源代码
│   ├── __init__.py                 # 包初始化，版本信息
│   ├── __main__.py                 # 模块入口点
│   ├── main.py                     # 服务器主入口，MCP 协议处理
│   ├── config.py                   # 配置管理 (92% 测试覆盖)
│   ├── email_service.py            # 邮件服务核心 (86% 测试覆盖)
│   ├── email_tools.py              # MCP 工具注册和实现
│   ├── attachment_service.py       # 附件处理服务 (77% 测试覆盖)
│   ├── models.py                   # 数据模型和验证 (90% 测试覆盖)
│   ├── exceptions.py               # 自定义异常定义
│   └── logging_config.py           # 日志配置
├── tests/                          # 测试文件 (73% 总覆盖率)
│   ├── __init__.py                 # 测试包初始化
│   ├── conftest.py                 # pytest 配置和 fixtures
│   ├── test_config.py              # 配置管理测试 (16/16 通过)
│   ├── test_models.py              # 数据模型测试 (28/28 通过)
│   ├── test_email_service.py       # 邮件服务测试 (22/29 通过)
│   ├── test_attachment_service.py  # 附件服务测试 (9/19 通过)
│   ├── test_require_confirmation.py # 确认功能测试
│   └── test_parameter_confirmation.py # 参数确认测试
├── docs/                           # 文档
│   ├── README.md                   # 文档中心
│   ├── API.md                      # API 文档
│   ├── MCP_CLIENT_SETUP.md         # 客户端配置
│   ├── CONFIGURATION.md            # 配置指南
│   ├── EXAMPLES.md                 # 示例代码
│   ├── FAQ.md                      # 常见问题
│   ├── TROUBLESHOOTING.md          # 故障排除
│   └── DEVELOPMENT_GUIDE.md        # 开发指南
├── .env.example                    # 环境变量模板
├── .env                            # 实际环境变量（不提交到版本控制）
├── pyproject.toml                  # 项目配置和依赖
├── pytest.ini                     # pytest 测试配置
├── mypy.ini                        # MyPy 类型检查配置
├── ruff.toml                       # Ruff 代码检查配置
├── CHANGELOG.md                    # 变更日志
├── CONTRIBUTING.md                 # 贡献指南
├── README.md                       # 项目主文档
├── start_server.bat                # Windows 启动脚本
└── start_server.sh                 # Linux/macOS 启动脚本
```

### 核心模块说明

#### `config.py` - 配置管理
```python
# 配置管理的核心类
class EmailSettings(BaseSettings):
    """邮箱配置模型"""
    address: str
    password: str
    provider: Optional[EmailProvider]
    smtp_server: Optional[str]
    # ...

class AppSettings(BaseSettings):
    """应用配置模型"""
    email_settings: EmailSettings
    log_level: str = "INFO"
    max_attachment_size: int = 26214400
    require_confirmation: bool = False
    # ...

# 主要函数
def get_email_settings() -> EmailSettings
def get_app_settings() -> AppSettings
def reload_settings() -> None
```

#### `email_service.py` - 邮件服务核心
```python
# 邮件服务的核心类
class EmailService:
    """邮件服务核心类"""

    def __init__(self):
        self._connection = None
        self._settings = get_email_settings()

    async def send_email(self, message: EmailMessage) -> str
    async def test_connection(self) -> ConnectionInfo
    def validate_email_format(self, email: str) -> EmailValidationResponse
    def get_supported_providers(self) -> List[ProviderInfo]

    # 私有方法
    async def _connect(self) -> None
    async def _disconnect(self) -> None
    def _build_mime_message(self, message: EmailMessage) -> MIMEMultipart
```

#### `models.py` - 数据模型
```python
# 核心数据模型
class EmailMessage(BaseModel):
    """邮件消息模型"""
    to: List[str]
    cc: Optional[List[str]]
    bcc: Optional[List[str]]
    subject: str
    body: str
    body_format: str = "plain"
    priority: int = 3
    attachments: List["Attachment"] = Field(default_factory=list)

class Attachment(BaseModel):
    """附件模型"""
    path: str
    name: Optional[str]
    size: int
    content_type: Optional[str]

class SendEmailToolRequest(BaseModel):
    """MCP工具请求模型"""
    to: List[str]
    subject: str
    body: str
    cc: Optional[List[str]]
    bcc: Optional[List[str]]
    attachments: Optional[List[str]]
    body_format: str = "plain"
    priority: int = 3
    require_confirmation: Optional[bool]
```

#### `email_tools.py` - MCP 工具实现
```python
# MCP 工具注册和实现
from fastmcp import Context

@mcp.tool()
async def send_email(
    ctx: Context,
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[str]] = None,
    body_format: str = "plain",
    priority: int = 3,
    require_confirmation: Optional[bool] = None
) -> Dict[str, Any]:
    """发送邮件工具"""
    # 实现邮件发送逻辑

@mcp.tool()
def validate_email(email: str) -> Dict[str, Any]:
    """验证邮箱地址格式"""
    # 实现邮箱验证逻辑

@mcp.tool()
def check_email_config() -> Dict[str, Any]:
    """检查邮箱配置"""
    # 实现配置检查逻辑
```

## 🔧 开发流程

### Git 工作流

#### 1. 创建功能分支
```bash
# 确保主分支是最新的
git checkout main
git pull upstream main

# 创建功能分支
git checkout -b feature/new-feature-name

# 或者修复 bug 分支
git checkout -b fix/bug-description
```

#### 2. 开发过程中
```bash
# 定期保存进度
git add .
git commit -m "feat: implement basic functionality"

# 查看变更
git status
git diff

# 同步上游更新
git fetch upstream
git rebase upstream/main
```

#### 3. 提交规范
```bash
# 提交消息格式
<type>(<scope>): <description>

[optional body]

[optional footer(s)]

# 示例
git commit -m "feat(email): add email priority support

Add support for setting email priority levels (1-5) in the send_email tool.
This allows users to mark emails as high priority or low priority.

Closes: #45"

# 提交类型
feat: 新功能
fix: Bug修复
docs: 文档更新
style: 代码格式化（不影响功能）
refactor: 代码重构
test: 测试相关
chore: 构建过程或工具变更
perf: 性能优化
```

### 代码开发流程

#### 1. 编写代码
```bash
# 创建新文件或修改现有文件
touch src/email_mcp_server/new_feature.py

# 遵循代码规范
uv run ruff format src/
uv run ruff check --fix src/
```

#### 2. 编写测试
```bash
# 创建测试文件
touch tests/test_new_feature.py

# 运行测试
uv run pytest tests/test_new_feature.py -v

# 生成覆盖率报告
uv run pytest tests/test_new_feature.py --cov=src/email_mcp_server/new_feature --cov-report=html
```

#### 3. 类型检查
```bash
# 运行类型检查
uv run mypy src/

# 检查特定模块
uv run mypy src/email_mcp_server/new_feature.py
```

### 代码审查流程

#### 提交前检查清单
```bash
# 1. 代码质量检查
uv run ruff check src/
uv run mypy src/

# 2. 运行测试
uv run pytest

# 3. 检查覆盖率
uv run pytest --cov=email_mcp_server --cov-report=term-missing

# 4. 格式化代码
uv run ruff format src/

# 5. 检查文档更新
git diff --name-only HEAD^ HEAD | grep -E "\\.md$"
```

#### Pull Request 模板
```markdown
## 变更描述
简要描述此PR的目的和实现的功能。

## 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 重构
- [ ] 文档更新
- [ ] 性能优化
- [ ] 其他: ___________

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试完成
- [ ] 测试覆盖率没有下降

## 检查清单
- [ ] 代码符合项目规范
- [ ] 所有测试通过
- [ ] 文档已更新（如需要）
- [ ] 变更日志已更新（如需要）
- [ ] 提交消息遵循规范

## 相关 Issue
Closes: #issue_number

## 测试环境
- Python 版本: ___________
- 操作系统: ___________
- MCP 客户端: ___________
```

## 🧪 测试开发

### 测试架构
```python
# 测试基础配置 (conftest.py)
import pytest
from unittest.mock import Mock, patch
from email_mcp_server.config import get_email_settings

@pytest.fixture
def mock_email_settings():
    """模拟邮箱配置"""
    with patch('email_mcp_server.config.get_email_settings') as mock:
        mock.return_value = Mock(
            address="test@example.com",
            password="test_password",
            provider=Mock(value="gmail"),
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            use_tls=True
        )
        yield mock

@pytest.fixture
def temp_attachment_file(tmp_path):
    """临时附件文件"""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test attachment content")
    return test_file
```

### 单元测试示例
```python
# tests/test_email_service.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from email_mcp_server.email_service import EmailService
from email_mcp_server.models import EmailMessage

class TestEmailService:
    """邮件服务测试类"""

    def test_validate_email_format_valid(self, mock_email_settings):
        """测试有效邮箱格式验证"""
        service = EmailService()
        result = service.validate_email_format("test@example.com")

        assert result.valid is True
        assert result.email == "test@example.com"
        assert result.normalized == "test@example.com"

    def test_validate_email_format_invalid(self, mock_email_settings):
        """测试无效邮箱格式验证"""
        service = EmailService()
        result = service.validate_email_format("invalid-email")

        assert result.valid is False
        assert result.message == "Invalid email format"

    @pytest.mark.asyncio
    async def test_send_email_success(self, mock_email_settings):
        """测试成功发送邮件"""
        service = EmailService()
        message = EmailMessage(
            to=["recipient@example.com"],
            subject="Test Subject",
            body="Test Body"
        )

        with patch.object(service, '_connection') as mock_conn:
            mock_conn.sendmail.return_value = {}
            mock_conn.getresponse.return_value.status = 250

            result = await service.send_email(message)

            assert result == "sent"
            mock_conn.sendmail.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_with_attachments(self, mock_email_settings, temp_attachment_file):
        """测试带附件邮件发送"""
        service = EmailService()
        message = EmailMessage(
            to=["recipient@example.com"],
            subject="Test with attachment",
            body="Test Body",
            attachments=[str(temp_attachment_file)]
        )

        with patch.object(service, '_connection') as mock_conn:
            mock_conn.sendmail.return_value = {}

            result = await service.send_email(message)

            assert result == "sent"
            # 验证附件被正确处理
            mock_conn.sendmail.assert_called_once()
```

### 集成测试示例
```python
# tests/test_integration.py
import pytest
from email_mcp_server.email_tools import send_email, validate_email
from email_mcp_server.models import SendEmailToolRequest

class TestMCPIntegration:
    """MCP 工具集成测试"""

    def test_validate_email_integration(self):
        """测试邮箱验证集成"""
        result = validate_email("test@example.com")

        assert result["valid"] is True
        assert "test@example.com" in result["normalized"]

    @pytest.mark.asyncio
    async def test_send_email_integration(self):
        """测试邮件发送集成"""
        request = SendEmailToolRequest(
            to=["test@example.com"],
            subject="Integration Test",
            body="This is an integration test"
        )

        # 使用 mock SMTP 服务器进行集成测试
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_server.sendmail.return_value = {}
            mock_smtp.return_value = mock_server

            result = await send_email(None, **request.dict())

            assert result["success"] is True
            mock_smtp.assert_called_once()
```

### 测试运行命令
```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_email_service.py

# 运行特定测试函数
uv run pytest tests/test_email_service.py::TestEmailService::test_send_email_success

# 生成覆盖率报告
uv run pytest --cov=email_mcp_server --cov-report=html

# 运行带标记的测试
uv run pytest -m "not slow"

# 并行运行测试（需要安装 pytest-xdist）
uv run pytest -n auto
```

## 🐛 调试技巧

### 日志调试
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 或者使用环境变量
# LOG_LEVEL=DEBUG uv run python -m email_mcp_server
```

### 断点调试
```python
# 使用 pdb 进行调试
import pdb; pdb.set_trace()

# 或者使用 IDE 调试器（VS Code, PyCharm）
```

### 性能调试
```python
# 使用 cProfile 进行性能分析
python -m cProfile -o profile.stats -m email_mcp_server

# 分析结果
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative')
p.print_stats(20)
"
```

### 内存调试
```python
# 使用 tracemalloc 进行内存调试
import tracemalloc

tracemalloc.start()

# ... 运行代码 ...

current, peak = tracemalloc.get_traced_memory()
print(f"当前内存使用: {current / 1024 / 1024:.1f} MB")
print(f"峰值内存使用: {peak / 1024 / 1024:.1f} MB")

tracemalloc.stop()
```

## ⚡ 性能优化

### 代码优化
```python
# 1. 使用缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def get_smtp_config(provider: str):
    """缓存 SMTP 配置"""
    return load_smtp_config(provider)

# 2. 异步优化
import asyncio
import aiofiles

async def process_attachments_async(attachments):
    """异步处理附件"""
    tasks = []
    for attachment in attachments:
        task = process_single_attachment(attachment)
        tasks.append(task)

    return await asyncio.gather(*tasks)

# 3. 内存优化
def process_large_file(file_path):
    """流式处理大文件"""
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            yield chunk
```

### 测试性能
```python
# 使用 pytest-benchmark 进行性能测试
import pytest

@pytest.mark.benchmark
def test_email_validation_performance(benchmark):
    """测试邮箱验证性能"""
    email = "test@example.com"
    result = benchmark(validate_email, email)
    assert result["valid"] is True
```

## 🚀 发布流程

### 版本管理
```bash
# 1. 更新版本号
# 编辑 pyproject.toml
version = "0.3.0"

# 2. 更新变更日志
# 编辑 CHANGELOG.md

# 3. 创建 Git 标签
git tag -a v0.3.0 -m "Release version 0.3.0"
git push origin v0.3.0
```

### 质量检查
```bash
# 完整的质量检查流程
uv run ruff check src/
uv run mypy src/
uv run pytest --cov=email_mcp_server --cov-fail-under=70
uv run pytest --cov=email_mcp_server --cov-report=html
```

### 发布检查清单
- [ ] 所有测试通过
- [ ] 代码覆盖率 ≥ 70%
- [ ] 文档已更新
- [ ] 变更日志已更新
- [ ] 版本号已更新
- [ ] Git 标签已创建
- [ ] 性能测试通过

## 📝 开发最佳实践

### 代码风格
1. **遵循 PEP 8**: 使用 `ruff format` 自动格式化
2. **类型注解**: 所有公共函数必须有类型注解
3. **文档字符串**: 使用 Google 风格的文档字符串
4. **常量定义**: 使用大写命名常量

### 命名规范
```python
# 类名：PascalCase
class EmailService:
    pass

# 函数和变量：snake_case
def send_email_message():
    email_address = "user@example.com"

# 常量：UPPER_SNAKE_CASE
MAX_ATTACHMENT_SIZE = 26214400
DEFAULT_SMTP_PORT = 587
```

### 文档字符串规范
```python
def send_email(
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[str]] = None,
    body_format: str = "plain",
    priority: int = 3
) -> Dict[str, Any]:
    """发送邮件。

    Args:
        to: 收件人邮箱地址列表
        subject: 邮件主题
        body: 邮件正文内容
        cc: 抄送邮箱地址列表
        bcc: 密送邮箱地址列表
        attachments: 附件路径列表
        body_format: 邮件格式，'plain' 或 'html'
        priority: 邮件优先级，1-5

    Returns:
        包含发送结果的字典

    Raises:
        EmailValidationError: 邮箱格式错误
        EmailServiceError: 邮件服务错误
        AttachmentError: 附件处理错误

    Example:
        >>> result = send_email(
        ...     to=["user@example.com"],
        ...     subject="Test",
        ...     body="Test message"
        ... )
        >>> print(result["success"])
        True
    """
```

### 错误处理
```python
# 自定义异常
class EmailMCPServerError(Exception):
    """基础异常类"""
    pass

class EmailValidationError(EmailMCPServerError):
    """邮箱验证错误"""
    pass

# 错误处理模式
def safe_operation():
    try:
        # 可能失败的操作
        result = risky_operation()
        return {"success": True, "data": result}
    except SpecificError as e:
        logger.error(f"特定错误: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.exception(f"未预期错误: {e}")
        return {"success": False, "error": "内部错误"}
```

### 测试驱动开发
1. **先写测试**: 在实现功能前先编写测试
2. **小步前进**: 每次只实现一个小功能
3. **重构友好**: 编写易于重构的代码
4. **覆盖率监控**: 保持高测试覆盖率

---

**最后更新**: 2025年11月23日
**开发指南版本**: v1.0.0

如有开发相关的问题，欢迎查看 [贡献指南](../CONTRIBUTING.md) 或提交 GitHub Issue！