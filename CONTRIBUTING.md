# 贡献指南

感谢您对 Email MCP 服务器项目的关注！我们欢迎所有形式的贡献，包括但不限于：

-  Bug 报告
- [SPARKLE] 新功能建议
- [EDIT] 文档改进
- [TOOLS] 代码贡献
-  测试用例

## 开始之前

### 前置条件

1. **Python 环境**: Python 3.14+
2. **包管理器**: 推荐使用 uv（或传统 pip + venv）
3. **开发工具**:
   - Git
   - 代码编辑器（推荐 VS Code + Pylance）
   - 支持现代 Python 语法的 IDE

### 项目结构理解

在贡献之前，请熟悉项目的核心架构：

```
email-mcp-server/
├── src/email_mcp_server/           # 主要源代码
│   ├── config.py                   # 配置管理（92%测试覆盖）
│   ├── email_service.py            # 邮件服务核心（86%测试覆盖）
│   ├── attachment_service.py       # 附件处理（77%测试覆盖）
│   ├── models.py                   # 数据模型（90%测覆盖）
│   ├── email_tools.py              # MCP工具注册
│   └── exceptions.py               # 自定义异常
├── tests/                          # 测试文件（73%总体覆盖率）
└── docs/                           # 项目文档
```

## 开发环境搭建

### 1. Fork 和克隆

```bash
# Fork 项目到您的 GitHub 账户，然后克隆
git clone https://github.com/YOUR_USERNAME/email-mcp-server.git
cd email-mcp-server

# 添加上游仓库
git remote add upstream https://github.com/original-owner/email-mcp-server.git
```

### 2. 环境设置

**使用 uv（推荐）:**
```bash
# 同步依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

**使用传统方式:**
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -e ".[dev]"
```

### 3. 配置开发环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件（测试时可以使用虚拟凭据）
EMAIL_ADDRESS=test@example.com
EMAIL_PASSWORD=test_password
```

### 4. 验证环境

```bash
# 运行测试确保环境正常
uv run pytest

# 检查代码质量
uv run ruff check src/
uv run mypy src/
```

## 开发工作流

### 1. 创建功能分支

```bash
# 确保主分支是最新的
git checkout main
git pull upstream main

# 创建功能分支
git checkout -b feature/your-feature-name

# 或者修复bug分支
git checkout -b fix/bug-description
```

### 2. 开发和测试

**代码质量标准:**
- [OK] **Ruff 检查通过**: `uv run ruff check src/`
- [OK] **MyPy 类型检查通过**: `uv run mypy src/`
- [OK] **Pylance 静态分析通过**: IDE中无警告和错误
- [OK] **测试覆盖率不下降**: 目标维持 73%+ 覆盖率

**开发过程中定期运行:**
```bash
# 代码格式检查和自动修复
uv run ruff check --fix src/
uv run ruff format src/

# 运行相关测试
uv run pytest tests/test_related_module.py

# 运行所有测试
uv run pytest --cov=email_mcp_server
```

### 3. 提交规范

**提交消息格式:**
```
类型(范围): 简短描述

详细描述（可选）

关联Issue: #123
```

**提交类型:**
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或工具变更

**示例:**
```bash
git commit -m "feat(email): add email priority support

Add support for setting email priority levels (1-5) in the send_email tool.
This allows users to mark emails as high priority or low priority.

Closes: #45"
```

## 测试指南

### 测试要求

1. **新功能必须包含测试**
2. **测试覆盖率不能低于当前标准（73%）**
3. **所有测试必须通过**

### 编写测试

**测试文件命名:**
```
tests/test_module_name.py
```

**测试用例命名:**
```python
def test_function_name_scenario():
    """测试功能在特定场景下的行为"""
    pass

def test_class_name_method_name():
    """测试类方法的行为"""
    pass
```

**测试结构示例:**
```python
import pytest
from unittest.mock import Mock, patch
from email_mcp_server.email_service import EmailService

def test_send_email_success():
    """测试成功发送邮件"""
    # Arrange
    email_service = EmailService()
    message = create_test_email_message()

    # Act
    with patch.object(email_service, '_connection') as mock_conn:
        mock_conn.sendmail.return_value = {}
        result = email_service.send_email(message)

    # Assert
    assert result == "sent"
    mock_conn.sendmail.assert_called_once()
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_email_service.py

# 运行特定测试函数
uv run pytest tests/test_email_service.py::test_send_email_success

# 生成覆盖率报告
uv run pytest --cov=email_mcp_server --cov-report=html

# 运行带标记的测试
uv run pytest -m "not slow"
```

## 代码审查

### 提交前检查清单

在提交 Pull Request 前，请确保：

- [ ] 代码遵循项目代码风格（通过 Ruff 检查）
- [ ] 所有类型注解正确（通过 MyPy 检查）
- [ ] 包含适当的测试用例
- [ ] 测试覆盖率不下降
- [ ] 文档已更新（如需要）
- [ ] 提交消息遵循规范
- [ ] 没有合并冲突

### Pull Request 流程

1. **创建 Pull Request**
   ```markdown
   ## 变更描述
   简要描述此PR的目的和实现的功能。

   ## 测试
   - [ ] 单元测试通过
   - [ ] 集成测试通过
   - [ ] 手动测试完成

   ## 检查清单
   - [ ] 代码符合项目规范
   - [ ] 测试覆盖率达标
   - [ ] 文档已更新
   ```

2. **代码审查**
   - 维护者会审查您的代码
   - 请及时回应反馈和建议
   - 根据反馈进行必要的修改

3. **合并**
   - 审查通过后，PR会被合并到主分支
   - 请保持分支更新，避免合并冲突

## 特殊贡献类型

###  Bug 报告

使用 GitHub Issues 报告 bug，请包含：

1. **环境信息**:
   - Python 版本
   - 操作系统
   - 项目版本

2. **重现步骤**:
   - 详细的重现步骤
   - 期望行为
   - 实际行为

3. **错误信息**:
   - 完整的错误堆栈
   - 相关日志

4. **其他信息**:
   - 配置文件（去除敏感信息）
   - 相关截图

### [SPARKLE] 功能建议

1. **问题描述**: 清晰描述要解决的问题
2. **建议方案**: 详细的解决方案
3. **替代方案**: 考虑的其他方案
4. **附加信息**: 任何相关的上下文

### [EDIT] 文档贡献

1. **文档类型**:
   - API 文档
   - 用户指南
   - 开发文档
   - 示例代码

2. **文档标准**:
   - 使用清晰的 Markdown 格式
   - 包含适当的代码示例
   - 保持与项目风格一致

## 开发工具推荐

### IDE 配置

**VS Code 扩展推荐:**
- Pylance（类型检查和智能提示）
- Python（官方Python扩展）
- GitLens（Git 增强）
- Python Docstring Generator（文档字符串生成）

**配置文件 (.vscode/settings.json):**
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
    }
}
```

### 代码质量工具

项目使用以下工具确保代码质量：

```bash
# 代码检查和格式化
uv run ruff check src/          # 代码检查
uv run ruff check --fix src/    # 自动修复
uv run ruff format src/         # 代码格式化

# 类型检查
uv run mypy src/                # 静态类型检查

# 测试
uv run pytest                   # 运行测试
uv run pytest --cov=email_mcp_server  # 测试覆盖率
```

## 社区准则

### 行为准则

1. **尊重他人**: 保持友善和专业的交流
2. **建设性反馈**: 提供有帮助的、具体的反馈
3. **包容性**: 欢迎不同背景和经验水平的贡献者
4. **耐心**: 对新手贡献者保持耐心和指导

### 沟通渠道

- **GitHub Issues**: 报告bug和功能建议
- **GitHub Discussions**: 一般讨论和问答
- **Pull Requests**: 代码贡献和审查

## 发布流程

### 版本管理

项目遵循[语义化版本](https://semver.org/lang/zh-CN/)：

- **主版本号**: 不兼容的API修改
- **次版本号**: 向后兼容的功能性新增
- **修订号**: 向后兼容的问题修正

### 发布检查清单

1. **代码质量**: 所有检查通过
2. **测试**: 测试覆盖率和所有测试通过
3. **文档**: 文档更新完整
4. **变更日志**: 更新 CHANGELOG.md
5. **版本号**: 更新版本号
6. **标记**: 创建 Git 标签

## 获得帮助

如果您在贡献过程中遇到问题：

1. **查看文档**:
   - [README.md](README.md)
   - [虚拟环境使用指南](虚拟环境使用指南.md)
   - [测试计划](测试计划.md)

2. **搜索 Issues**: 查看是否有相关讨论

3. **创建 Issue**: 如有新问题，创建 GitHub Issue

4. **联系维护者**: 通过 GitHub 联系项目维护者

---

感谢您的贡献！[STAR]