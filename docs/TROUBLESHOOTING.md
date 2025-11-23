# Email MCP 服务器故障排除指南

本指南提供了 Email MCP 服务器常见问题的详细诊断和解决方案。

## [MAGNIFY] 诊断流程

### 第一步：检查基本信息
```bash
# 1. 检查 Python 版本
python --version
# 应该是 Python 3.14+

# 2. 检查 uv 安装
uv --version

# 3. 检查项目环境
cd /path/to/email-mcp-server
uv info

# 4. 检查依赖状态
uv sync --dry-run
```

### 第二步：验证配置文件
```bash
# 1. 检查 .env 文件是否存在
ls -la .env

# 2. 验证环境变量格式
cat .env | grep -E "^(EMAIL_|LOG_|MAX_)"

# 3. 检查文件编码
file .env
# 应该显示：UTF-8 Unicode text
```

### 第三步：测试服务器启动
```bash
# 1. 尝试启动服务器
uv run python -m email_mcp_server

# 2. 检查启动日志输出
# 应该看到类似：
# Email MCP Server starting...
# Server initialized successfully
# Waiting for MCP messages...
```

## [ALERT] 常见错误及解决方案

### 错误类型 1：环境配置问题

#### [X] 错误：`ModuleNotFoundError: No module named 'email_mcp_server'`

**症状**：
```
ModuleNotFoundError: No module named 'email_mcp_server'
```

**原因分析**：
- 项目未正确安装
- Python 路径问题
- 虚拟环境未激活

**解决方案**：
```bash
# 1. 确保在项目根目录
pwd
# 应该显示：/path/to/email-mcp-server

# 2. 重新同步依赖
uv sync

# 3. 检查项目结构
ls -la src/email_mcp_server/
# 应该包含 __init__.py 等文件

# 4. 测试导入
uv run python -c "import email_mcp_server; print('Import successful')"
```

#### [X] 错误：`Email configuration not found` 或环境变量未设置

**症状**：
```
EmailValidationError: EMAIL_ADDRESS environment variable not set
```

**原因分析**：
- .env 文件不存在
- 环境变量格式错误
- 文件编码问题

**解决方案**：
```bash
# 1. 创建 .env 文件
cp .env.example .env

# 2. 编辑 .env 文件
nano .env
# 确保格式正确：
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_password

# 3. 检查文件编码
file .env
# 如果不是 UTF-8，转换编码：
iconv -f GBK -t UTF-8 .env > .env.utf8
mv .env.utf8 .env

# 4. 验证环境变量加载
uv run python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print(f'EMAIL_ADDRESS: {os.getenv(\"EMAIL_ADDRESS\")}')
print(f'EMAIL_PASSWORD: {\"SET\" if os.getenv(\"EMAIL_PASSWORD\") else \"NOT SET\"}')
"
```

#### [X] 错误：`uv command not found`

**症状**：
```
bash: uv: command not found
```

**解决方案**：
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或者使用 pip 安装
pip install uv

# 重新启动终端或刷新 PATH
source ~/.bashrc  # Linux/macOS
# 或重新打开 Windows 终端
```

### 错误类型 2：邮箱认证问题

#### [X] 错误：SMTP 认证失败

**症状**：
```
SMTPAuthenticationError: 535 Authentication failed
smtplib.SMTPAuthenticationError: (535, b'Authentication failed')
```

**原因分析**：
- 密码/授权码错误
- SMTP 服务器配置错误
- 邮箱安全策略限制

**解决方案**：

**对于 QQ 邮箱**：
1. **重新获取授权码**：
   - 登录 QQ 邮箱
   - 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
   - 关闭并重新开启 SMTP 服务
   - 生成新的授权码

2. **检查 SMTP 配置**：
```env
EMAIL_ADDRESS=your_qq@qq.com
EMAIL_PASSWORD=your_new_authorization_code
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

**对于 Gmail**：
1. **重新生成应用专用密码**：
   - 访问 Google 账户设置
   - 安全性 → 两步验证（必须开启）
   - 应用专用密码 → 生成新密码
   - 选择"邮件"和设备

2. **允许不够安全的应用**（如果使用普通密码）：
   - 访问 Google 账户设置
   - 安全性 → 不太安全的应用访问权限 → 开启

#### [X] 错误：连接超时

**症状**：
```
TimeoutError: [WinError 10060] 连接超时
socket.timeout: timed out
```

**解决方案**：
```bash
# 1. 测试网络连接
ping smtp.gmail.com
ping smtp.qq.com

# 2. 检查防火墙设置
# Windows: 控制面板 → Windows Defender 防火墙
# macOS: 系统偏好设置 → 安全性与隐私 → 防火墙
# Linux: sudo ufw status

# 3. 检查代理设置
echo $HTTP_PROXY
echo $HTTPS_PROXY

# 4. 增加超时时间（在 .env 中）
DOWNLOAD_TIMEOUT=60
```

### 错误类型 3：MCP 通信问题

#### [X] 错误：MCP 客户端无法连接

**症状**：
- Claude Code 中看不到邮件工具
- Cursor 显示连接错误
- VS Code MCP 扩展启动失败

**诊断步骤**：
```bash
# 1. 手动测试服务器
uv run python -m email_mcp_server
# 应该显示启动信息并等待连接

# 2. 检查配置中的路径
# 确保使用绝对路径
pwd  # 复制此路径到配置中

# 3. 测试 MCP 协议
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}' | uv run python -m email_mcp_server
```

**配置修正**：

**Claude Code 配置**：
```json
{
  "mcpServers": {
    "email-mcp-server": {
      "command": "uv",
      "args": ["run", "python", "-m", "email_mcp_server"],
      "cwd": "/absolute/path/to/email-mcp-server",
      "env": {
        "EMAIL_ADDRESS": "your_email@example.com",
        "EMAIL_PASSWORD": "your_password"
      }
    }
  }
}
```

**Cursor 配置**：
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
          "EMAIL_PASSWORD": "your_password"
        }
      }
    }
  }
}
```

#### [X] 错误：工具调用失败

**症状**：
```
Tool execution failed: send_email
Error: No such tool available
```

**解决方案**：
1. **重启 MCP 客户端**
2. **检查服务器日志**：
```bash
# 启用详细日志
LOG_LEVEL=DEBUG uv run python -m email_mcp_server
```
3. **验证工具注册**：
```bash
# 测试工具列表
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | uv run python -m email_mcp_server
```

### 错误类型 4：附件处理问题

#### [X] 错误：文件未找到

**症状**：
```
FileNotFoundError: [Errno 2] No such file or directory: 'attachment.pdf'
AttachmentError: File not found: attachment.pdf
```

**解决方案**：
```bash
# 1. 使用绝对路径
pwd  # 获取当前路径
ls -la /absolute/path/to/attachment.pdf

# 2. 检查文件权限
ls -l attachment.pdf
# 应该有读权限：-rw-r--r--

# 3. 验证路径格式
# 正确示例：
/home/user/documents/report.pdf
C:\\Users\\User\\Documents\\report.pdf
./attachments/report.pdf
```

#### [X] 错误：附件过大

**症状**：
```
AttachmentError: Attachment size exceeds limit (25MB)
```

**解决方案**：
```bash
# 1. 检查文件大小
ls -lh large_file.pdf

# 2. 压缩文件
zip -r compressed.zip large_file.pdf

# 3. 调整限制（在 .env 中）
MAX_ATTACHMENT_SIZE=52428800  # 50MB

# 4. 使用云存储链接替代
# 上传到 Google Drive、Dropbox 等并分享链接
```

### 错误类型 5：内存和性能问题

#### [X] 错误：内存不足

**症状**：
- 系统变慢
- 内存使用持续增长
- 进程被杀死

**解决方案**：
```bash
# 1. 监控内存使用
# Windows: 任务管理器
# macOS: Activity Monitor
# Linux: top 或 htop

# 2. 清理临时文件
rm -rf temp/
mkdir temp

# 3. 限制附件大小
echo "MAX_ATTACHMENT_SIZE=10485760" >> .env  # 10MB

# 4. 增加系统交换空间（Linux）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## [TOOLS] 调试工具和技巧

### 启用详细日志
```bash
# 1. 设置调试环境变量
export LOG_LEVEL=DEBUG
export LOG_FILE=debug.log

# 2. 启动服务器
uv run python -m email_mcp_server

# 3. 实时查看日志
tail -f debug.log
```

### 测试单个组件
```bash
# 1. 测试配置加载
uv run python -c "
from email_mcp_server.config import get_app_settings
settings = get_app_settings()
print(f'Email: {settings.email_settings.address}')
print(f'Provider: {settings.email_settings.provider}')
"

# 2. 测试邮箱验证
uv run python -c "
from email_mcp_server.email_service import EmailService
service = EmailService()
result = service.validate_email_format('test@example.com')
print(f'Validation result: {result}')
"

# 3. 测试 SMTP 连接
uv run python -c "
import asyncio
from email_mcp_server.email_service import EmailService

async def test_connection():
    service = EmailService()
    try:
        conn_info = await service.test_connection()
        print(f'Connection successful: {conn_info}')
    except Exception as e:
        print(f'Connection failed: {e}')

asyncio.run(test_connection())
"
```

### 网络诊断
```bash
# 1. 测试 SMTP 服务器连通性
telnet smtp.gmail.com 587
telnet smtp.qq.com 587

# 2. 使用 openssl 测试 TLS
openssl s_client -connect smtp.gmail.com:587 -starttls smtp
openssl s_client -connect smtp.qq.com:587 -starttls smtp

# 3. 检查 DNS 解析
nslookup smtp.gmail.com
nslookup smtp.qq.com

# 4. 跟踪网络路径
traceroute smtp.gmail.com  # Linux/macOS
tracert smtp.gmail.com    # Windows
```

##  获取帮助

### 收集诊断信息
在寻求帮助时，请提供以下信息：

```bash
# 1. 系统信息
uname -a
python --version
uv --version

# 2. 项目信息
git log -1 --oneline
git status

# 3. 配置信息（去除敏感信息）
cat .env | sed 's/EMAIL_ADDRESS=.*/EMAIL_ADDRESS=***@***.***/' | sed 's/EMAIL_PASSWORD=.*/EMAIL_PASSWORD=*****/'

# 4. 错误日志
tail -50 email_mcp.log

# 5. 测试结果
uv run pytest --tb=short
```

### 社区支持
1. **GitHub Issues**: 搜索现有问题或创建新问题
2. **GitHub Discussions**: 一般讨论和问答
3. **文档**: 查看最新文档更新

### 紧急恢复
如果服务器完全无法工作：

```bash
# 1. 备份当前配置
cp .env .env.backup

# 2. 重置到已知工作状态
git checkout HEAD -- .env
cp .env.example .env

# 3. 重新安装环境
rm -rf .venv
uv sync

# 4. 重新配置基本信息
nano .env
# 只设置必需的 EMAIL_ADDRESS 和 EMAIL_PASSWORD
```

## [SCANNER] 检查清单

### 安装问题检查清单
- [ ] Python 3.14+ 已安装
- [ ] uv 已安装并可执行
- [ ] 项目已克隆到正确路径
- [ ] `uv sync` 成功执行
- [ ] 虚拟环境已创建

### 配置问题检查清单
- [ ] .env 文件存在
- [ ] EMAIL_ADDRESS 格式正确
- [ ] EMAIL_PASSWORD 已设置
- [ ] 文件编码为 UTF-8
- [ ] 邮箱服务商设置正确

### 网络问题检查清单
- [ ] 能访问 SMTP 服务器
- [ ] 防火墙端口开放
- [ ] 代理设置正确
- [ ] DNS 解析正常

### MCP 客户端问题检查清单
- [ ] 配置文件路径正确
- [ ] 使用绝对路径
- [ ] 环境变量已传递
- [ ] 服务器能手动启动
- [ ] 客户端已重启

---

**最后更新**: 2025年11月23日
**指南版本**: v1.0.0

如果本指南没有解决您的问题，请创建 GitHub Issue 并提供详细的错误信息和诊断结果。