# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个基于 Python 实现的邮件 MCP (Model Context Protocol) 服务器，通过 MCP 协议提供邮件发送功能。

## 技术栈

- **Python**: 3.14 (通过 uv 管理)
- **框架**: Pydantic + FastMCP
- **环境**: UTF-8 无 BOM 编码
- **进程**: MCP 服务器通过 stdio 运行
- **版本控制**: Git

## 项目结构

基于 `list.md` 中的项目规范，这是一个新项目，将实现：

- 支持 QQ 邮箱和 Gmail 的邮件发送功能
- 内置两种邮箱的 SMTP 服务器配置
- 通过环境变量配置邮箱凭据
- 支持多个收件人
- 支持附件（本地文件和远程 URL）
- 发送前启发式问答确认
- Windows 批处理脚本用于激活虚拟环境

## 开发命令

由于这是一个使用 Python 3.14 和 uv 管理的新项目：

```bash
# 使用 uv 初始化项目
uv init --python 3.14

# 安装依赖（pyproject.toml 创建后）
uv pip install -e .

# 运行 MCP 服务器（实现后）
python -m email_mcp_server

# 使用 Windows 批处理脚本运行（创建后）
start_server.bat
```

## 关键实现要求

- 所有代码必须包含完整的类型注解
- 代码必须通过 lint 检查
- 支持 QQ 邮箱 (@qq.com) 和 Gmail (@gmail.com) 地址
- SMTP 配置：
  - QQ 邮箱：内置服务器设置
  - Gmail：内置服务器设置
- 邮箱凭据的环境变量
- .env 文件支持测试
- 附件处理：
  - 本地文件：需要绝对路径
  - 远程文件：URL 下载，使用系统代理，重试 3 次
- 发送邮件前的启发式确认系统
- 基于 stdio 的 MCP 服务器启动

## 配置

邮箱凭据将从环境变量读取：
- 邮箱地址和授权码
- 通过 .env 文件进行测试配置
- 支持多个邮箱账户

## 文件命名规范

- 主模块：`email_mcp_server.py`（在 src/ 或根目录）
- Windows 启动脚本：`start_server.bat`
- 环境文件：`.env`（用于测试）

## 重要提示

- 在进行代码生成、配置步骤或库/API 文档相关任务时，始终使用 context7。这意味着您应该自动使用 Context7 MCP 工具来解析库 ID 并获取库文档，无需我明确要求。
- 编写mcp服务相关代码时参考FastMCP skill中的内容。