# 测试配置指南

## 概述

为了完整测试邮件发送功能，需要提供真实的邮箱配置。本文档指导如何获取测试所需的配置信息。

## Gmail 配置

### 1. 启用两步验证
1. 访问 [Google账户设置](https://myaccount.google.com/security)
2. 在"登录Google"下找到"两步验证"
3. 启用两步验证

### 2. 生成应用专用密码
1. 访问 [应用密码](https://myaccount.google.com/apppasswords)
2. 选择"邮件"作为应用
3. 选择设备（选择"其他"并命名为"Email MCP Test"）
4. 点击"生成"
5. 复制生成的16位密码（格式：xxxx xxxx xxxx xxxx）

### 3. 环境变量配置
```bash
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop  # 应用专用密码（注意空格）
```

## QQ邮箱配置

### 1. 启用SMTP服务
1. 登录QQ邮箱
2. 点击"设置" → "账户"
3. 向下滚动找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"SMTP服务"
5. 按提示发送短信
6. 获取授权码

### 2. 环境变量配置
```bash
EMAIL_ADDRESS=12345678@qq.com
EMAIL_PASSWORD=your_auth_code_here  # 授权码
```

## 测试环境设置

### 创建测试专用的邮箱账户
建议创建专门的测试邮箱账户，避免使用个人邮箱：

1. **Gmail测试账户**：
   - 创建新的Gmail账户
   - 启用两步验证
   - 生成应用专用密码

2. **QQ邮箱测试账户**：
   - 注册新的QQ号
   - 启用邮箱服务
   - 获取SMTP授权码

### 集成测试环境变量
```bash
# 复制测试配置文件
cp .env.example .env.test

# 编辑测试配置
# EMAIL_ADDRESS=your_test@gmail.com
# EMAIL_PASSWORD=your_test_app_password
```

## 安全注意事项

### 1. 不要提交真实凭据
```bash
# 确保.env文件在.gitignore中
echo ".env" >> .gitignore
echo ".env.test" >> .gitignore
echo ".env.local" >> .gitignore
```

### 2. 使用测试专用账户
- 不要使用生产邮箱账户
- 定期更换测试账户密码
- 使用最小权限原则

### 3. CI/CD环境配置
对于自动化测试，考虑以下选项：

1. **跳过集成测试**：
   ```yaml
   # 在CI中仅运行单元测试
   pytest -m "unit"
   ```

2. **使用测试服务**：
   - 使用 [Mailtrap](https://mailtrap.io/) 等邮件测试服务
   - 配置临时SMTP服务器

3. **环境变量注入**：
   ```yaml
   # GitHub Actions示例
   - name: Run integration tests
   env:
     EMAIL_ADDRESS: ${{ secrets.TEST_EMAIL }}
     EMAIL_PASSWORD: ${{ secrets.TEST_PASSWORD }}
   run: pytest -m "integration"
   ```

## 测试场景配置

### 本地开发测试
```bash
# 使用真实配置进行本地测试
export EMAIL_ADDRESS=your_test@gmail.com
export EMAIL_PASSWORD=your_app_password
pytest tests/test_email_service.py::TestEmailService::test_send_email_real -v
```

### Mock测试（推荐）
大部分测试应使用Mock，避免真实网络调用：
```bash
# 运行单元测试（使用Mock）
pytest -m "unit" --cov=src/email_mcp_server

# 运行集成测试（需要真实配置）
pytest -m "integration"
```

## 故障排除

### 常见错误

1. **"535-5.7.8 Username and Password not accepted"**
   - 检查是否使用应用专用密码
   - 确认两步验证已启用

2. **"SMTPAuthenticationError"**
   - 验证邮箱地址格式
   - 检查授权码是否正确

3. **"Connection timeout"**
   - 检查网络连接
   - 验证SMTP服务器地址和端口

### 调试模式
```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
pytest tests/test_email_service.py::test_connect_success -v -s
```