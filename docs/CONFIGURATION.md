# Email MCP 服务器配置指南

本指南详细说明了 Email MCP 服务器的所有配置选项和最佳实践。

## [SCANNER] 目录

- [快速配置](#快速配置)
- [环境变量详解](#环境变量详解)
- [邮箱提供商配置](#邮箱提供商配置)
- [SMTP 服务器配置](#smtp-服务器配置)
- [性能配置](#性能配置)
- [安全配置](#安全配置)
- [日志配置](#日志配置)
- [高级配置](#高级配置)
- [配置验证](#配置验证)
- [故障排除](#故障排除)

## [ROCKET] 快速配置

### 最小配置
创建 `.env` 文件并设置基本配置：

```env
# 必需配置 - 邮箱地址和密码
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_password_or_auth_code
```

### 完整配置示例
```env
# ===== 基本邮箱配置 =====
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_app_password

# ===== SMTP 服务器配置（可选，自动检测） =====
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USE_SSL=false

# ===== 日志配置 =====
LOG_LEVEL=INFO
LOG_FILE=email_mcp.log

# ===== 性能配置 =====
MAX_ATTACHMENT_SIZE=26214400      # 25MB
TEMP_DIR=temp
DOWNLOAD_TIMEOUT=30
MAX_RETRIES=3

# ===== 安全配置 =====
REQUIRE_CONFIRMATION=false

# ===== 应用配置 =====
APP_NAME=Email MCP Server
APP_VERSION=1.0.0
```

## 邮件 邮箱提供商配置

### Gmail 配置

#### 前置条件
1. **开启两步验证**
   - 访问 [Google 账户设置](https://myaccount.google.com/)
   - 安全性 → 两步验证 → 开启

2. **生成应用专用密码**
   - 安全性 → 应用专用密码
   - 选择"邮件"和设备
   - 生成16位密码

#### 配置文件
```env
# Gmail 配置
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_16_digit_app_password

# 可选：显式设置 SMTP 配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

#### Gmail 特殊注意事项
```env
# 如果使用普通密码（不推荐），需要开启"不够安全的应用访问"
# 访问：https://myaccount.google.com/lesssecureapps

# 推荐使用应用专用密码，更安全可靠
```

### QQ 邮箱配置

#### 前置条件
1. **开启 SMTP 服务**
   - 登录 QQ 邮箱网页版
   - 设置 → 账户
   - POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
   - 开启 IMAP/SMTP 服务

2. **获取授权码**
   - 点击"生成授权码"
   - 发送短信验证
   - 复制生成的授权码

#### 配置文件
```env
# QQ 邮箱配置
EMAIL_ADDRESS=your_qq@qq.com
EMAIL_PASSWORD=your_authorization_code

# 可选：显式设置 SMTP 配置
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### 企业邮箱配置

#### 通用企业邮箱
```env
# 企业邮箱配置示例
EMAIL_ADDRESS=your_name@company.com
EMAIL_PASSWORD=your_password

# SMTP 服务器配置（根据企业设置）
SMTP_SERVER=smtp.company.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

#### Outlook/Exchange 配置
```env
# Outlook 配置
EMAIL_ADDRESS=your_email@outlook.com
EMAIL_PASSWORD=your_app_password

# Outlook SMTP 配置
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

#### Microsoft 365 配置
```env
# Microsoft 365 配置
EMAIL_ADDRESS=your_email@company.onmicrosoft.com
EMAIL_PASSWORD=your_password

# Microsoft 365 SMTP 配置
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

## [TOOLS] SMTP 服务器配置

### 自动检新增机制
Email MCP 服务器支持自动检测常见的邮箱提供商：

```python
# 自动检测逻辑（内部实现）
def auto_detect_smtp(email_domain):
    smtp_configs = {
        'gmail.com': {
            'server': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False
        },
        'qq.com': {
            'server': 'smtp.qq.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False
        }
        # ... 更多配置
    }
    return smtp_configs.get(email_domain)
```

### 手动 SMTP 配置
当自动检测不够时，可以手动指定：

```env
# 自定义 SMTP 服务器
SMTP_SERVER=smtp.your-provider.com
SMTP_PORT=465               # 常用端口：25, 465, 587
SMTP_USE_TLS=false          # SSL 连接
SMTP_USE_SSL=true           # TLS 连接

# SSL vs TLS 对比：
# SSL (SMTPS): 端口 465，直接加密连接
# TLS (STARTTLS): 端口 587，先连接后加密
```

### 常见 SMTP 端口
```env
# 端口 25: 传统 SMTP，通常需要 STARTTLS
# 端口 587: SMTP + STARTTLS，推荐用于邮件提交
# 端口 465: SMTPS，已弃用但仍广泛使用
# 端口 2525: 部分提供商的替代端口
```

### SMTP 连接测试
```bash
# 测试 SMTP 连接（使用 openssl）
# TLS 连接测试
openssl s_client -connect smtp.gmail.com:587 -starttls smtp

# SSL 连接测试
openssl s_client -connect smtp.gmail.com:465

# 或者使用 telnet
telnet smtp.gmail.com 587
```

## [BOLT] 性能配置

### 附件大小限制
```env
# 限制单个邮件的附件总大小（字节）
MAX_ATTACHMENT_SIZE=26214400    # 25MB（默认）
# MAX_ATTACHMENT_SIZE=52428800  # 50MB
# MAX_ATTACHMENT_SIZE=104857600 # 100MB
```

### 网络配置
```env
# 下载超时时间（秒）
DOWNLOAD_TIMEOUT=30             # 默认30秒
# DOWNLOAD_TIMEOUT=60          # 60秒，适用于慢速网络

# 最大重试次数
MAX_RETRIES=3                   # 默认重试3次
# MAX_RETRIES=5                # 重试5次

# 临时文件目录
TEMP_DIR=temp                   # 默认temp目录
# TEMP_DIR=/var/tmp/email_mcp  # 指定系统目录
# TEMP_DIR=C:\\temp\\email_mcp # Windows路径
```

### 内存优化配置
```env
# 大文件处理阈值（字节）
LARGE_FILE_THRESHOLD=10485760   # 10MB以上的文件使用特殊处理

# 附件压缩开关
ENABLE_ATTACHMENT_COMPRESSION=true  # 启用附件压缩

# 清理策略
AUTO_CLEANUP_TEMP=true         # 自动清理临时文件
CLEANUP_INTERVAL=3600          # 清理间隔（秒）
```

## [LOCK] 安全配置

### 确认机制
```env
# 全局确认开关
REQUIRE_CONFIRMATION=false     # 默认不启用
# REQUIRE_CONFIRMATION=true    # 启用发送确认

# 确认级别
CONFIRMATION_LEVEL=full        # full: 完整确认, minimal: 最小确认
```

### 日志安全
```env
# 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO                 # 生产环境建议 WARNING

# 日志文件权限（Linux/macOS）
LOG_FILE_PERMISSION=600        # 只有所有者可读写

# 敏感信息过滤
FILTER_SENSITIVE_DATA=true     # 过滤日志中的敏感信息
```

### 网络安全
```env
# 代理配置
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=https://proxy.company.com:8080
NO_PROXY=localhost,127.0.0.1   # 不使用代理的地址

# SSL/TLS 验证
SSL_VERIFY=true                # 验证SSL证书（推荐）
# SSL_VERIFY=false            # 禁用SSL验证（仅用于测试）
```

### 访问控制
```env
# IP 白名单（未来功能）
ALLOWED_IPS=192.168.1.0/24,10.0.0.0/8

# 速率限制（未来功能）
RATE_LIMIT_PER_MINUTE=60       # 每分钟最多60封邮件
```

## [EDIT] 日志配置

### 日志级别详解
```env
# DEBUG: 详细的调试信息，包括所有内部操作
LOG_LEVEL=DEBUG

# INFO: 一般信息，包括成功操作和配置信息
LOG_LEVEL=INFO

# WARNING: 警告信息，可能的问题但不影响正常运行
LOG_LEVEL=WARNING

# ERROR: 错误信息，操作失败但不影响系统运行
LOG_LEVEL=ERROR

# CRITICAL: 严重错误，可能导致系统停止
LOG_LEVEL=CRITICAL
```

### 日志文件配置
```env
# 日志文件路径
LOG_FILE=email_mcp.log         # 相对路径
# LOG_FILE=/var/log/email_mcp.log  # 绝对路径
# LOG_FILE=C:\\logs\\email_mcp.log # Windows路径

# 日志轮转
LOG_MAX_SIZE=10485760          # 10MB
LOG_BACKUP_COUNT=5             # 保留5个备份文件
LOG_ROTATION=daily             # 每天轮转
```

### 日志格式
```env
# 日志格式
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# 详细格式（包含文件和行号）
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s
```

## [MAGNIFY] 高级配置

### 应用配置
```env
# 应用基本信息
APP_NAME=Email MCP Server
APP_VERSION=1.0.0
APP_DESCRIPTION=Model Context Protocol Email Server

# 环境标识
ENVIRONMENT=production          # development, testing, staging, production
DEBUG=false                    # 调试模式
```

### 提供商扩展
```env
# 自定义提供商配置（未来功能）
CUSTOM_PROVIDERS=/path/to/providers.json
ENABLE_CUSTOM_PROVIDER=false
```

### 缓存配置
```env
# 缓存设置（未来功能）
ENABLE_CACHE=true
CACHE_TTL=3600                 # 缓存1小时
CACHE_MAX_SIZE=1000             # 最大缓存条目
```

### 监控配置
```env
# 健康检查（未来功能）
ENABLE_HEALTH_CHECK=true
HEALTH_CHECK_INTERVAL=60       # 每分钟检查一次

# 性能监控
ENABLE_PERFORMANCE_MONITORING=true
METRICS_EXPORT_INTERVAL=300    # 每5分钟导出指标
```

## [OK] 配置验证

### 验证命令
```bash
# 1. 检查环境变量
uv run python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('EMAIL_ADDRESS:', os.getenv('EMAIL_ADDRESS'))
print('EMAIL_PASSWORD:', 'SET' if os.getenv('EMAIL_PASSWORD') else 'NOT SET')
print('LOG_LEVEL:', os.getenv('LOG_LEVEL', 'INFO'))
"

# 2. 测试配置加载
uv run python -c "
from email_mcp_server.config import get_app_settings
settings = get_app_settings()
print('配置加载成功')
print('邮箱地址:', settings.email_settings.address)
print('SMTP服务器:', settings.email_settings.smtp_server)
"

# 3. 验证邮箱配置
uv run python -c "
from email_mcp_server.email_tools import check_email_config
result = check_email_config()
print('配置检查结果:', result)
"
```

### 配置文件模板
```bash
# 创建生产环境配置
cp .env.example .env.production

# 创建开发环境配置
cp .env.example .env.development

# 创建测试环境配置
cp .env.example .env.testing
```

### 环境特定配置
```bash
# 开发环境
export ENVIRONMENT=development
export LOG_LEVEL=DEBUG
export REQUIRE_CONFIRMATION=true

# 生产环境
export ENVIRONMENT=production
export LOG_LEVEL=WARNING
export REQUIRE_CONFIRMATION=false
```

## [TOOLS] 配置管理最佳实践

### 1. 环境分离
```bash
# 使用不同的配置文件
.env.local      # 本地开发
.env.development # 开发环境
.env.staging    # 测试环境
.env.production # 生产环境

# 启动时指定环境
export ENVIRONMENT=production
uv run python -m email_mcp_server
```

### 2. 敏感信息管理
```bash
# 1. 使用密钥管理服务（推荐）
export EMAIL_PASSWORD=$(aws secretsmanager get-secret-value --secret-id email-password --query SecretString --output text)

# 2. 使用环境变量文件（确保权限正确）
chmod 600 .env
chown $USER:$USER .env

# 3. 使用 Docker secrets
docker run --secret email_password email-mcp-server
```

### 3. 配置验证脚本
```bash
#!/bin/bash
# config-check.sh - 配置检查脚本

echo "=== Email MCP 服务器配置检查 ==="

# 检查必需环境变量
required_vars=("EMAIL_ADDRESS" "EMAIL_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "[X] 错误: $var 未设置"
        exit 1
    else
        echo "[OK] $var 已设置"
    fi
done

# 检查邮箱格式
if [[ $EMAIL_ADDRESS =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
    echo "[OK] 邮箱地址格式正确"
else
    echo "[X] 错误: 邮箱地址格式无效"
    exit 1
fi

# 测试服务器启动
echo "=== 测试服务器启动 ==="
timeout 10 uv run python -m email_mcp_server > /dev/null 2>&1 &
SERVER_PID=$!
sleep 2

if kill -0 $SERVER_PID 2>/dev/null; then
    echo "[OK] 服务器启动成功"
    kill $SERVER_PID
else
    echo "[X] 错误: 服务器启动失败"
    exit 1
fi

echo "=== 配置检查完成 ==="
```

### 4. Docker 配置
```dockerfile
# Dockerfile
FROM python:3.14-slim

WORKDIR /app

# 复制配置文件
COPY .env.example .env.template

# 安装依赖
RUN pip install uv && uv sync

# 设置环境变量
ENV EMAIL_ADDRESS=${EMAIL_ADDRESS}
ENV EMAIL_PASSWORD=${EMAIL_PASSWORD}
ENV LOG_LEVEL=INFO

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from email_mcp_server.config import get_app_settings; get_app_settings()" || exit 1

CMD ["uv", "run", "python", "-m", "email_mcp_server"]
```

## [ALERT] 故障排除

### 常见配置问题

#### 1. 环境变量未生效
```bash
# 检查文件位置
ls -la .env

# 检查文件权限
chmod 644 .env

# 检查文件编码
file .env  # 应该显示 UTF-8

# 重新加载配置
unset EMAIL_ADDRESS EMAIL_PASSWORD
source .env
```

#### 2. SMTP 连接失败
```bash
# 测试网络连接
ping smtp.gmail.com
telnet smtp.gmail.com 587

# 检查防火墙设置
# Windows: 控制面板 → 防火墙
# Linux: sudo ufw status
# macOS: 系统偏好设置 → 安全性与隐私

# 检查代理设置
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

#### 3. 认证失败
```bash
# 1. 重新生成应用专用密码
# Gmail: 访问 Google 账户设置
# QQ邮箱: 重新生成授权码

# 2. 检查邮箱安全设置
# Gmail: 检查两步验证和应用专用密码设置
# QQ邮箱: 确认 SMTP 服务已开启

# 3. 测试认证
uv run python -c "
import smtplib
from email_mcp_server.config import get_email_settings

settings = get_email_settings()
server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
server.starttls()
try:
    server.login(settings.address, settings.password)
    print('认证成功')
except Exception as e:
    print(f'认证失败: {e}')
finally:
    server.quit()
"
```

### 配置调试技巧

#### 启用详细日志
```env
LOG_LEVEL=DEBUG
LOG_FILE=debug.log
```

#### 测试单个配置项
```python
# test_config.py
import os
from dotenv import load_dotenv

def test_config():
    load_dotenv()

    print("=== 配置信息 ===")
    print(f"EMAIL_ADDRESS: {os.getenv('EMAIL_ADDRESS')}")
    print(f"EMAIL_PASSWORD: {'SET' if os.getenv('EMAIL_PASSWORD') else 'NOT SET'}")
    print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER', 'AUTO_DETECT')}")
    print(f"SMTP_PORT: {os.getenv('SMTP_PORT', 'AUTO_DETECT')}")
    print(f"LOG_LEVEL: {os.getenv('LOG_LEVEL', 'INFO')}")
    print(f"MAX_ATTACHMENT_SIZE: {os.getenv('MAX_ATTACHMENT_SIZE', '25MB')}")

if __name__ == "__main__":
    test_config()
```

---

**最后更新**: 2025年11月23日
**配置指南版本**: v1.0.0

如有配置相关的问题，请查看 [故障排除指南](TROUBLESHOOTING.md) 或提交 GitHub Issue！