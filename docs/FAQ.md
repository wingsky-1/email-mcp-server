# Email MCP 服务器 - 常见问题解答 (FAQ)

本文档收集了用户在使用 Email MCP 服务器过程中遇到的常见问题及其解决方案。

## 🚀 安装和环境问题

### Q1: 系统要求是什么？
**A**: Email MCP 服务器需要以下环境：
- **Python**: 3.14 或更高版本
- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **内存**: 最少 512MB，推荐 1GB
- **网络**: 需要访问 SMTP 服务器的网络连接

### Q2: 推荐使用 uv 还是 pip？
**A**: 强烈推荐使用 `uv`：
- 🚀 **更快的安装速度**：比 pip 快 10-100 倍
- 🔒 **更好的依赖管理**：自动解决依赖冲突
- 📦 **项目导向**：自动管理虚拟环境
- 🛠️ **现代化工具**：支持最新的 Python 特性

参考：[虚拟环境使用指南](../虚拟环境使用指南.md)

### Q3: 安装时出现 Python 版本不兼容错误
**A**: Email MCP 服务器需要 Python 3.14+：
```bash
# 检查 Python 版本
python --version

# 如果版本过低，升级 Python
# Windows: 从 python.org 下载最新版本
# macOS: brew install python@3.14
# Ubuntu: sudo apt update && sudo apt install python3.14
```

### Q4: 在 Windows 上安装 uv 失败
**A**: 尝试以下方法：
```powershell
# 方法一：使用 PowerShell (推荐)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 方法二：使用 pip 安装
pip install uv

# 方法三：手动下载二进制文件
# 从 https://github.com/astral-sh/uv/releases 下载
```

## ⚙️ 配置问题

### Q5: 如何正确配置 QQ 邮箱？
**A**: QQ 邮箱配置步骤：
1. **登录 QQ 邮箱**网页版
2. **进入设置** → **账户** → **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务**
3. **开启 SMTP 服务**
4. **获取授权码**（不是登录密码！）
5. **配置环境变量**：
```env
EMAIL_ADDRESS=your_qq@qq.com
EMAIL_PASSWORD=your_authorization_code
```

### Q6: 如何正确配置 Gmail？
**A**: Gmail 配置步骤：
1. **开启两步验证**：账户安全 → 两步验证
2. **生成应用专用密码**：
   - 访问 Google 账户设置
   - 安全性 → 应用专用密码
   - 选择"邮件"和设备
   - 生成 16 位密码
3. **配置环境变量**：
```env
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_16_digit_app_password
```

### Q7: 环境变量不生效怎么办？
**A**: 检查以下项目：
```bash
# 1. 确认 .env 文件在项目根目录
ls -la .env

# 2. 检查文件编码（必须是 UTF-8）
file .env

# 3. 确认环境变量格式（等号两边不能有空格）
cat .env

# 4. 重启 MCP 服务器重新加载配置
uv run python -m email_mcp_server
```

### Q8: 如何自定义 SMTP 服务器？
**A**: 可以通过环境变量覆盖默认配置：
```env
# 基本配置
EMAIL_ADDRESS=your_email@custom-domain.com
EMAIL_PASSWORD=your_password

# 自定义 SMTP 配置
SMTP_SERVER=smtp.custom-domain.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

## 🔌 MCP 集成问题

### Q9: Claude Code 中无法找到邮件工具
**A**: 检查 MCP 服务器配置：
1. **确认配置路径正确**：
```json
{
  "mcpServers": {
    "email-mcp-server": {
      "command": "uv",
      "args": ["run", "python", "-m", "email_mcp_server"],
      "cwd": "/absolute/path/to/email-mcp-server"
    }
  }
}
```

2. **确认环境变量传递**：
```json
{
  "env": {
    "EMAIL_ADDRESS": "your_email@example.com",
    "EMAIL_PASSWORD": "your_password"
  }
}
```

3. **重启 Claude Code**

### Q10: Cursor 中 MCP 服务器启动失败
**A**: 排查步骤：
1. **检查 Cursor 控制台**的错误信息
2. **手动测试服务器启动**：
```bash
cd /path/to/email-mcp-server
uv run python -m email_mcp_server
```
3. **检查路径是否为绝对路径**
4. **确认虚拟环境已创建**：`uv sync`

### Q11: VS Code 中如何配置 MCP 服务器？
**A**: 需要安装 MCP 扩展并配置：
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

## 📧 邮件发送问题

### Q12: 邮件发送失败，提示认证错误
**A**: 常见原因和解决方案：
1. **密码/授权码错误**：重新生成授权码
2. **SMTP设置错误**：检查服务器地址和端口
3. **安全策略限制**：允许不够安全的应用访问（Gmail）
4. **网络连接问题**：检查防火墙和代理设置

### Q13: 附件发送失败
**A**: 检查以下项目：
1. **文件路径**：使用绝对路径或正确的相对路径
2. **文件大小**：单次发送限制 25MB
3. **文件权限**：确保有读取权限
4. **远程 URL**：检查网络连接和 URL 有效性

### Q14: HTML 邮件显示为纯文本
**A**: 确保 `body_format` 参数设置正确：
```python
send_email(
    to=["recipient@example.com"],
    subject="HTML 邮件",
    body="<h1>标题</h1><p>HTML内容</p>",
    body_format="html"  # 重要：设置为 "html"
)
```

### Q15: 如何发送给多个收件人？
**A**: 支持多种收件人类型：
```python
send_email(
    to=["user1@example.com", "user2@example.com"],  # 主收件人
    cc=["manager@example.com"],                      # 抄送
    bcc=["archive@example.com"],                     # 密送
    subject="群发邮件",
    body="邮件内容"
)
```

## 🔒 安全相关问题

### Q16: 如何保护邮箱密码安全？
**A**: 安全最佳实践：
1. **使用环境变量**：不要在代码中硬编码密码
2. **使用授权码**：而不是登录密码
3. **限制文件权限**：
```bash
chmod 600 .env
```
4. **定期更换授权码**
5. **使用应用专用密码**（Gmail）

### Q17: 在生产环境中如何提高安全性？
**A**: 生产环境安全建议：
1. **启用 require_confirmation**：
```env
REQUIRE_CONFIRMATION=true
```
2. **限制日志级别**：
```env
LOG_LEVEL=WARNING
```
3. **使用 HTTPS 代理**（如果适用）
4. **定期更新依赖**：`uv sync --upgrade`
5. **监控系统日志**

## 🐛 错误排查

### Q18: 如何启用调试模式？
**A**: 设置调试环境变量：
```env
LOG_LEVEL=DEBUG
LOG_FILE=debug.log
```

然后查看详细的日志信息：
```bash
tail -f debug.log
```

### Q19: 连接超时错误
**A**: 常见解决方案：
1. **增加超时时间**：
```env
DOWNLOAD_TIMEOUT=60
```
2. **检查网络连接**：确认能访问 SMTP 服务器
3. **检查防火墙设置**：确保端口 587/465 开放
4. **使用系统代理**（如果需要）

### Q20: 内存使用过高
**A**: 优化建议：
1. **限制附件大小**：
```env
MAX_ATTACHMENT_SIZE=10485760  # 10MB
```
2. **定期清理临时文件**：
```env
TEMP_DIR=/tmp/email_mcp
```
3. **监控内存使用**：使用系统监控工具

## 🚀 性能优化

### Q21: 如何提高邮件发送速度？
**A**: 优化建议：
1. **使用较快的网络连接**
2. **减少附件大小和数量**
3. **批量发送时使用连接池**
4. **选择合适的 SMTP 服务器**

### Q22: 大文件附件处理
**A**: 大文件处理策略：
1. **压缩文件**：减少文件大小
2. **使用云存储链接**：代替直接附件
3. **分批发送**：避免单次发送过大
4. **增加超时时间**：
```env
DOWNLOAD_TIMEOUT=300
MAX_RETRIES=5
```

## 🔧 高级配置

### Q23: 如何配置代理？
**A**: 系统代理自动支持，也可以手动设置：
```env
# HTTP 代理
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=https://proxy.company.com:8080

# SOCKS 代理
ALL_PROXY=socks5://proxy.company.com:1080
```

### Q24: 如何自定义日志配置？
**A**: 通过环境变量配置：
```env
# 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# 日志文件路径
LOG_FILE=/var/log/email_mcp.log

# 日志轮转（需要 logrotate 配置）
```

### Q25: require_confirmation 功能如何使用？
**A**: 详细参考：[require_confirmation 功能指南](../REQUIRE_CONFIRMATION_GUIDE.md)

基本使用：
```env
# 全局启用确认
REQUIRE_CONFIRMATION=true
```

单次调用覆盖：
```python
send_email(
    to=["user@example.com"],
    subject="重要邮件",
    body="内容",
    require_confirmation=True  # 强制确认
)
```

## 📚 其他问题

### Q26: 支持哪些邮箱提供商？
**A**: 目前支持：
- ✅ **Gmail** (@gmail.com)
- ✅ **QQ 邮箱** (@qq.com)
- ✅ **自定义 SMTP** 服务器

未来计划支持：
- 🔄 **Outlook** (@outlook.com, @hotmail.com)
- 🔄 **163 邮箱** (@163.com)
- 🔄 **企业邮箱**

### Q27: 如何获取技术支持？
**A**: 获取帮助的途径：
1. **查阅文档**：首先查看相关文档页面
2. **搜索 FAQ**：在本页面搜索问题
3. **GitHub Issues**：搜索或创建新的 Issue
4. **社区讨论**：GitHub Discussions

### Q28: 如何参与项目开发？
**A**: 参考贡献指南：
1. 阅读 [贡献指南](../CONTRIBUTING.md)
2. Fork 项目仓库
3. 创建功能分支
4. 提交 Pull Request

### Q29: 项目版本更新策略？
**A**: 遵循[语义化版本](https://semver.org/lang/zh-CN/)：
- **主版本号**：不兼容的 API 修改
- **次版本号**：向后兼容的功能性新增
- **修订号**：向后兼容的问题修正

查看 [变更日志](../CHANGELOG.md) 了解详细更新信息。

### Q30: 如何报告 Bug？
**A**: 报告 Bug 时请包含：
1. **环境信息**：
   - Python 版本
   - 操作系统
   - 项目版本

2. **重现步骤**：
   - 详细的重现步骤
   - 期望行为
   - 实际行为

3. **错误信息**：
   - 完整的错误堆栈
   - 相关日志

4. **其他信息**：
   - 配置文件（去除敏感信息）
   - 相关截图

---

## 🔍 问题搜索

如果您没有找到答案，请尝试：
1. 在本页面使用 Ctrl+F 搜索关键词
2. 查看 [故障排除指南](docs/TROUBLESHOOTING.md)
3. 搜索 GitHub Issues
4. 创建新的 GitHub Issue

**最后更新**: 2025年11月23日
**FAQ 版本**: v1.0.0

如有其他问题，欢迎提交 Issue 帮助我们完善此 FAQ！