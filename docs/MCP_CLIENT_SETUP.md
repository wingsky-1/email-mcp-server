# MCP 客户端配置指南

本指南详细说明如何在各种 AI 开发环境中配置和使用 Email MCP 服务器。

## 📋 前置条件

1. **已完成 Email MCP 服务器安装**
2. **已配置邮箱凭据**（.env 文件）
3. **已安装 Python 3.14+ 和 uv**

## 🔧 环境配置

### 1. 邮箱凭据配置

确保项目根目录下的 `.env` 文件包含正确的邮箱配置：

```env
# 必需配置
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_password_or_auth_code

# 可选配置
LOG_LEVEL=INFO
MAX_ATTACHMENT_SIZE=26214400  # 25MB
TEMP_DIR=temp
DOWNLOAD_TIMEOUT=30
MAX_RETRIES=3
```

### 2. 邮箱提供商设置

#### QQ 邮箱
1. 登录 QQ 邮箱
2. 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
3. 开启 SMTP 服务
4. 获取授权码（不是登录密码）

#### Gmail
1. 登录 Google 账户
2. 开启两步验证
3. 生成应用专用密码
4. 使用应用专用密码作为 EMAIL_PASSWORD

## 🤖 Claude Code 配置

### 方法一：通过设置界面

1. **打开 Claude Code 设置**
2. **导航到 MCP 服务器配置**
3. **添加新的 MCP 服务器**

```json
{
  "mcpServers": {
    "email-mcp-server": {
      "command": "uv",
      "args": ["run", "python", "-m", "email_mcp_server"],
      "cwd": "/absolute/path/to/email-mcp-server",
      "env": {
        "EMAIL_ADDRESS": "your_email@example.com",
        "EMAIL_PASSWORD": "your_password_or_auth_code"
      }
    }
  }
}
```

### 方法二：通过配置文件

在 Claude Code 配置目录创建 `mcp-servers.json`：

```json
{
  "email-mcp-server": {
    "command": "uv",
    "args": ["run", "python", "-m", "email_mcp_server"],
    "cwd": "/absolute/path/to/email-mcp-server"
  }
}
```

环境变量可以在系统级别设置。

### 验证配置

在 Claude Code 中输入：

```
请检查当前的邮件配置状态
```

Claude 应该能够调用 `check_email_config` 工具并返回配置信息。

## 🎯 Cursor 配置

### 步骤 1：打开设置

1. 按 `Ctrl/Cmd + ,` 打开设置
2. 搜索 "MCP" 或 "Model Context Protocol"

### 步骤 2：添加服务���配置

```json
{
  "mcp": {
    "servers": {
      "email": {
        "command": "uv",
        "args": ["run", "python", "-m", "email_mcp_server"],
        "cwd": "/absolute/path/to/email-mcp-server",
        "env": {
          "EMAIL_ADDRESS": "your_email@example.com",
          "EMAIL_PASSWORD": "your_password_or_auth_code"
        }
      }
    }
  }
}
```

### 步骤 3：重启 Cursor

配置完成后，重启 Cursor 以加载 MCP 服务器。

### 步骤 4：验证配置

在 Cursor 的 AI 聊天中测试：

```
请验证邮箱地址 test@example.com 的格式是否正确
```

## 💻 VS Code 配置

### 安装必要扩展

1. **Model Context Protocol** 扩展
2. **Python** 扩展（如果尚未安装）

### 配置步骤

1. 打开 VS Code 设置 (`Ctrl/Cmd + ,`)
2. 搜索 "mcp servers"
3. 添加配置：

```json
{
  "mcp.servers": [
    {
      "name": "email-mcp-server",
      "command": "uv",
      "args": ["run", "python", "-m", "email_mcp_server"],
      "cwd": "/absolute/path/to/email-mcp-server",
      "environment": {
        "EMAIL_ADDRESS": "your_email@example.com",
        "EMAIL_PASSWORD": "your_password_or_auth_code"
      }
    }
  ]
}
```

### 工作区配置

在项目根目录创建 `.vscode/settings.json`：

```json
{
  "mcp.servers": [
    {
      "name": "email-mcp-server",
      "command": "uv",
      "args": ["run", "python", "-m", "email_mcp_server"],
      "cwd": "${workspaceFolder}",
      "environment": {
        "EMAIL_ADDRESS": "${env:EMAIL_ADDRESS}",
        "EMAIL_PASSWORD": "${env:EMAIL_PASSWORD}"
      }
    }
  ]
}
```

## 🐳 Docker 部署配置

### 创建 Dockerfile

```dockerfile
FROM python:3.14-slim

WORKDIR /app

# 安装 uv
RUN pip install uv

# 复制项目文件
COPY . .

# 安装依赖
RUN uv sync

# 设置环境变量
ENV EMAIL_ADDRESS=your_email@example.com
ENV EMAIL_PASSWORD=your_password_or_auth_code

# 暴露端口（如果需要健康检查）
EXPOSE 8000

# 运行 MCP 服务器
CMD ["uv", "run", "python", "-m", "email_mcp_server"]
```

### 构建和运行

```bash
# 构建镜像
docker build -t email-mcp-server .

# 运行容器
docker run --rm -it \
  -e EMAIL_ADDRESS=your_email@example.com \
  -e EMAIL_PASSWORD=your_password_or_auth_code \
  email-mcp-server
```

### Docker Compose 配置

```yaml
version: '3.8'

services:
  email-mcp-server:
    build: .
    environment:
      - EMAIL_ADDRESS=your_email@example.com
      - EMAIL_PASSWORD=your_password_or_auth_code
      - LOG_LEVEL=INFO
    volumes:
      - ./attachments:/app/temp
    restart: unless-stopped
```

## 🔌 其他 MCP 客户端

### 直接 stdio 连接

```python
import subprocess
import json

# 直接与 MCP 服务器通信
process = subprocess.Popen(
    ["uv", "run", "python", "-m", "email_mcp_server"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd="/path/to/email-mcp-server"
)

# 发送初始化消息
init_message = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    }
}

process.stdin.write(json.dumps(init_message) + "\n")
process.stdin.flush()

# 读取响应
response = process.stdout.readline()
print(response)
```

### Node.js 客户端示例

```javascript
const { spawn } = require('child_process');
const path = require('path');

class EmailMCPClient {
  constructor(serverPath) {
    this.serverPath = serverPath;
    this.process = null;
  }

  async connect() {
    this.process = spawn('uv', ['run', 'python', '-m', 'email_mcp_server'], {
      cwd: this.serverPath,
      stdio: ['pipe', 'pipe', 'pipe']
    });

    // 初始化连接
    const initMessage = {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2024-11-05",
        capabilities: {},
        clientInfo: {
          name: "nodejs-client",
          version: "1.0.0"
        }
      }
    };

    this.process.stdin.write(JSON.stringify(initMessage) + '\n');

    return new Promise((resolve, reject) => {
      this.process.stdout.on('data', (data) => {
        try {
          const response = JSON.parse(data.toString());
          resolve(response);
        } catch (error) {
          reject(error);
        }
      });
    });
  }

  async sendEmail(to, subject, body, attachments = []) {
    const message = {
      jsonrpc: "2.0",
      id: Date.now(),
      method: "tools/call",
      params: {
        name: "send_email",
        arguments: {
          to,
          subject,
          body,
          attachments
        }
      }
    };

    this.process.stdin.write(JSON.stringify(message) + '\n');

    return new Promise((resolve) => {
      this.process.stdout.once('data', (data) => {
        const response = JSON.parse(data.toString());
        resolve(response);
      });
    });
  }
}

// 使用示例
const client = new EmailMCPClient('/path/to/email-mcp-server');

(async () => {
  await client.connect();

  const result = await client.sendEmail(
    ['recipient@example.com'],
    'Test Email',
    'This is a test email sent via MCP',
    []
  );

  console.log('Email sent:', result);
})();
```

## 🧪 测试 MCP 连接

### 验证服务器启动

```bash
# 直接运行服务器
cd /path/to/email-mcp-server
uv run python -m email_mcp_server

# 应该看到类似输出：
# Email MCP Server starting...
# Server initialized successfully
# Waiting for MCP messages...
```

### 测试基本功能

在任何配置好的 MCP 客户端中测试：

1. **测试邮箱验证**：
   ```
   请验证邮箱地址 user@example.com
   ```

2. **测试配置检查**：
   ```
   请检查当前的邮件配置状态
   ```

3. **测试邮件发送**：
   ```
   请给 test@example.com 发送一封测试邮件，主题是"MCP 测试"
   ```

## 🔧 故障排除

### 常见问题

1. **服务器无法启动**
   - 检查 Python 版本（需要 3.14+）
   - 确保依赖已安装：`uv sync`
   - 检查环境变量配置

2. **MCP 客户端无法连接**
   - 确认服务器路径正确
   - 检查环境变量是否传递
   - 查看 MCP 客户端日志

3. **邮件发送失败**
   - 验证邮箱凭据
   - 检查 SMTP 配置
   - 确认网络连接

### 调试模式

启用详细日志：

```bash
# 设置环境变量
export LOG_LEVEL=DEBUG

# 运行服务器
uv run python -m email_mcp_server
```

### 日志文件

检查日志文件以获取详细信息：

```bash
# 查看日志
tail -f email_mcp.log

# 或在代码中指定日志文件
export LOG_FILE=/path/to/debug.log
```

## 📚 进一步资源

- [MCP 协议规范](https://spec.modelcontextprotocol.io/)
- [Claude Code 文档](https://docs.anthropic.com/claude/docs/claude-code)
- [Cursor 文档](https://www.cursor.sh/docs)
- [FastMCP 文档](https://fastmcp.readthedocs.io/)

---

如有问题，请查看项目的 GitHub Issues 或创建新的 Issue。