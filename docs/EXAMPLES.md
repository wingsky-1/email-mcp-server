# Email MCP 服务器示例代码与教程

本文档提供了 Email MCP 服务器的详细使用示例和实用教程。

## [BOOKS] 目录

- [基础示例](#基础示例)
- [高级功能示例](#高级功能示例)
- [实际应用场景](#实际应用场景)
- [集成示例](#集成示例)
- [错误处理示例](#错误处理示例)
- [性能优化示例](#性能优化示例)

## [ROCKET] 基础示例

### 1. 发送简单文本邮件

```python
# 最基本的邮件发送
send_email(
    to=["recipient@example.com"],
    subject="测试邮件",
    body="这是一封测试邮件，用于验证邮件发送功能。"
)
```

### 2. 发送 HTML 格式邮件

```python
# HTML 邮件示例
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>项目报告</title>
</head>
<body>
    <h1 style="color: #333;">项目进度报告</h1>
    <p>尊敬的团队成员：</p>
    <p>本周项目进展如下：</p>
    <ul>
        <li>[OK] 完成了用户认证模块</li>
        <li>[SYNC] 正在进行数据库优化</li>
        <li>[WAIT] 计划下周开始前端界面开发</li>
    </ul>
    <p style="color: #666;">祝好！</p>
</body>
</html>
"""

send_email(
    to=["team@example.com"],
    subject="项目进度报告 - HTML格式",
    html_body=html_content
)
```

### 3. 发送带附件的邮件

```python
# 单个附件
send_email(
    to=["recipient@example.com"],
    subject="项目文档",
    body="请查收附件中的项目文档。",
    attachments=["/path/to/project_document.pdf"]
)

# 多个附件
send_email(
    to=["recipient@example.com"],
    subject="月度报告",
    body="本月报告包含多个文件，请查收。",
    attachments=[
        "/path/to/report.pdf",
        "/path/to/data.xlsx",
        "/path/to/charts.png"
    ]
)

# 混合本地和远程附件
send_email(
    to=["recipient@example.com"],
    subject="综合资料包",
    body="包含本地文件和网络资源。",
    attachments=[
        "/path/to/local_file.pdf",
        "https://example.com/remote_file.pdf",
        "https://github.com/project/logo.png"
    ]
)
```

### 4. 多收件人邮件

```python
# 多个主收件人
send_email(
    to=["user1@example.com", "user2@example.com", "user3@example.com"],
    subject="团队会议通知",
    body="请准时参加明天下午3点的团队会议。"
)

# 包含抄送和密送
send_email(
    to=["team@example.com"],
    cc=["manager@example.com"],
    bcc=["archive@example.com"],
    subject="项目完成通知",
    body="项目已成功完成，详细信息见正文。"
)
```

### 5. 设置邮件优先级

```python
# 高优先级邮件
send_email(
    to=["admin@example.com"],
    subject="紧急：系统故障报告",
    body="生产环境出现严重故障，请立即处理！",
    priority=1  # 1=最高优先级
)

# 低优先级邮件
send_email(
    to=["newsletter@example.com"],
    subject="月度新闻摘要",
    body="这是本月的工作总结和新闻。",
    priority=5  # 5=最低优先级
)
```

## [TOOLS] 高级功能示例

### 1. require_confirmation 功能

```python
# 使用全局设置（假设全局启用确认）
send_email(
    to=["user@example.com"],
    subject="普通邮件",
    body="这封邮件会按照全局设置进行确认。"
)

# 强制要求确认
send_email(
    to=["boss@example.com"],
    subject="重要报告",
    body="这是一份重要报告，必须确认发送。",
    require_confirmation=True
)

# 跳过确认（适用于动化场景）
send_email(
    to=["system@example.com"],
    subject="自动生成的监控报告",
    body="系统自动生成的定期监控报告。",
    require_confirmation=False
)
```

### 2. 邮箱地址验证

```python
# 验证单个邮箱
result = validate_email("user@example.com")
print(f"验证结果: {result}")
# 输出: {'valid': True, 'email': 'user@example.com', 'normalized': 'user@example.com', 'message': 'Email format is valid'}

# 验证格式错误的邮箱
result = validate_email("invalid-email")
print(f"验证结果: {result}")
# 输出: {'valid': False, 'email': 'invalid-email', 'normalized': '', 'message': 'Invalid email format'}
```

### 3. 配置检查

```python
# 检查当前配置
config_result = check_email_config()
print(f"配置状态: {config_result}")
# 输出包含：
# - configured: 是否已配置
# - email_address: 配置的邮箱
# - provider: 邮箱提供商
# - connection_test: 连接测试结果
# - smtp_config: SMTP配置信息
```

### 4. 获取支持的邮箱提供商

```python
# 查看所有支持的提供商
providers = get_supported_providers()
print(f"支持的提供商: {providers}")

# 输出示例：
# {
#   "providers": [
#     {
#       "name": "Gmail",
#       "domains": ["gmail.com"],
#       "smtp_server": "smtp.gmail.com",
#       "smtp_port": 587,
#       "use_tls": True,
#       "use_ssl": False,
#       "description": "Google's free email service"
#     },
#     {
#       "name": "QQ邮箱",
#       "domains": ["qq.com"],
#       "smtp_server": "smtp.qq.com",
#       "smtp_port": 587,
#       "use_tls": True,
#       "use_ssl": False,
#       "description": "腾讯公司的免费邮箱服务"
#     }
#   ]
# }
```

## 网络 实际应用场景

### 场景1：项目进度报告

```python
def send_project_progress_report():
    """发送项目进度报告"""

    # HTML 邮件模板
    html_report = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #f8f9fa; padding: 20px; border-radius: 5px; }
            .progress { margin: 20px 0; }
            .task { margin: 10px 0; padding: 10px; border-left: 4px solid #007bff; }
            .completed { border-left-color: #28a745; }
            .in-progress { border-left-color: #ffc107; }
            .pending { border-left-color: #dc3545; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>[ROCKET] 项目进度报告</h1>
            <p><strong>项目名称:</strong> 智能邮件系统</p>
            <p><strong>报告日期:</strong> 2025年11月23日</p>
            <p><strong>项目经理:</strong> 张三</p>
        </div>

        <div class="progress">
            <h2>本周进展</h2>
            <div class="task completed">
                <h3>[OK] 用户认证模块</h3>
                <p>完成了JWT认证和权限管理系统</p>
            </div>
            <div class="task in-progress">
                <h3>[SYNC] 数据库优化</h3>
                <p>正在进行查询性能优化，完成度70%</p>
            </div>
            <div class="task pending">
                <h3>[WAIT] 前端界面开发</h3>
                <p>计划下周开始，预计2周完成</p>
            </div>
        </div>

        <div class="metrics">
            <h2>关键指标</h2>
            <ul>
                <li>代码覆盖率: 87.22%</li>
                <li>API响应时间: 平均120ms</li>
                <li>Bug修复率: 92%</li>
            </ul>
        </div>
    </body>
    </html>
    """

    # 发送邮件
    send_email(
        to=["team@company.com", "manager@company.com"],
        cc=["stakeholders@company.com"],
        subject="[ROCKET] 项目进度报告 - 智能邮件系统 (2025年11月23日)",
        body=html_report,
        body_format="html",
        priority=2,
        attachments=[
            "/path/to/detailed_metrics.pdf",
            "/path/to/burndown_chart.png",
            "https://dashboard.company.com/api/export/project_stats"
        ],
        require_confirmation=True  # 重要报告需要确认
    )

# 使用示例
send_project_progress_report()
```

### 场景2：自动化的系统监控报告

```python
import json
from datetime import datetime

def send_system_monitoring_report():
    """发送系统监控报告（自动化，无需确认）"""

    # 收集系统指标（示例数据）
    system_metrics = {
        "timestamp": datetime.now().isoformat(),
        "server_status": "healthy",
        "cpu_usage": "45%",
        "memory_usage": "68%",
        "disk_usage": "72%",
        "network_latency": "12ms",
        "active_users": 1247,
        "error_rate": "0.03%",
        "uptime": "99.98%"
    }

    # 生成监控报告内容
    report_content = f"""
系统监控报告
================

报告时间: {system_metrics['timestamp']}

[CHART] 系统状态
- 服务器状态: {system_metrics['server_status']} [OK]
- CPU使用率: {system_metrics['cpu_usage']}
- 内存使用率: {system_metrics['memory_usage']}
- 磁盘使用率: {system_metrics['disk_usage']}
- 网络延迟: {system_metrics['network_latency']}

 用户指标
- 在线用户数: {system_metrics['active_users']}
- 错误率: {system_metrics['error_rate']}
- 系统可用性: {system_metrics['uptime']}

[BELL] 告警状态
- CPU使用率正常 (<80%)
- 内存使用率正常 (<90%)
- 磁盘使用率注意 (>70%)
- 错误率良好 (<0.1%)

[GRAPH] 趋势分析
- 过去24小时系统运行稳定
- 用户活跃度较昨日增长5.2%
- 无重大故障发生
    """

    # 发送自动化邮件
    send_email(
        to=["ops@company.com", "devops@company.com"],
        subject=f"[MAGNIFY] 系统监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        body=report_content,
        attachments=[
            "/var/log/system.log",
            "/tmp/metrics_chart.png",
            "https://monitoring.company.com/reports/latest"
        ],
        require_confirmation=False  # 自动化报告无需确认
    )

# 定时任务示例（配合 cron 使用）
if __name__ == "__main__":
    send_system_monitoring_report()
```

### 场景3：客户服务自动回复

```python
def send_customer_service_reply(customer_email, customer_name, ticket_id, issue_type):
    """发送客户服务自动回复"""

    # 根据问题类型定制回复内容
    templates = {
        "billing": """
亲爱的{customer_name}：

感谢您联系我们的账单支持团队。

关于您的问题（工单号：{ticket_id}），我们的财务团队会在24小时内处理您的请求。
您可以通过以下链接查看账单详情：
https://billing.company.com/invoices

如有紧急问题，请直接拨打客服热线：400-123-4567

祝好！
客服团队
        """,

        "technical": """
尊敬的{customer_name}：

感谢您联系我们的技术支持团队。

我们已收到您的技术问题报告（工单号：{ticket_id}），技术工程师正在分析您的问题。
我们承诺在12小时内给您初步回复。

在此期间，您可以：
1. 查看我们的帮助中心：https://help.company.com
2. 尝试基本的故障排除步骤
3. 提供更多详细信息以加快处理进度

感谢您的耐心等待！

技术支持团队
        """,

        "general": """
您好{customer_name}：

感谢您联系我们。

我们已收到您的咨询（工单号：{ticket_id}），客服团队会尽快为您处理。
我们承诺在工作时间24小时内回复。

如有紧急事项，请致电：400-123-4567

客户服务团队
        """
    }

    # 选择合适的模板
    template = templates.get(issue_type, templates["general"])

    # 格式化邮件内容
    email_content = template.format(
        customer_name=customer_name,
        ticket_id=ticket_id
    )

    # 发送邮件
    send_email(
        to=[customer_email],
        cc=["support@company.com"],
        subject=f"Re: 您的咨询已收到 (工单号: {ticket_id})",
        body=email_content,
        priority=3,
        require_confirmation=False  # 自动回复无需确认
    )

# 使用示例
send_customer_service_reply(
    customer_email="customer@example.com",
    customer_name="李明",
    ticket_id="TK2025112301",
    issue_type="technical"
)
```

## [PLUG] 集成示例

### 1. 与 FastAPI 集成

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional

app = FastAPI(title="邮件服务API")

class EmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    attachments: Optional[List[str]] = None
    body_format: str = "plain"
    priority: int = 3

@app.post("/send-email")
async def api_send_email(request: EmailRequest):
    """API端点：发送邮件"""
    try:
        # 调用 Email MCP 服务器的 send_email 工具
        result = send_email(
            to=request.to,
            subject=request.subject,
            body=request.body,
            cc=request.cc,
            bcc=request.bcc,
            attachments=request.attachments,
            body_format=request.body_format,
            priority=request.priority
        )

        return {
            "success": True,
            "message": "邮件发送成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"邮件发送失败: {str(e)}")

@app.get("/validate-email/{email}")
async def api_validate_email(email: str):
    """API端点：验证邮箱格式"""
    try:
        result = validate_email(email)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")

@app.get("/check-config")
async def api_check_config():
    """API端点：检查邮件配置"""
    try:
        result = check_email_config()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置检查失败: {str(e)}")
```

### 2. 与 Django 集成

```python
# django_emails/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@require_http_methods(["POST"])
def send_email_view(request):
    """Django视图：发送邮件"""
    try:
        data = json.loads(request.body)

        result = send_email(
            to=data.get('to', []),
            subject=data.get('subject', ''),
            body=data.get('body', ''),
            cc=data.get('cc'),
            bcc=data.get('bcc'),
            attachments=data.get('attachments'),
            body_format=data.get('body_format', 'plain'),
            priority=data.get('priority', 3)
        )

        return JsonResponse({
            'success': True,
            'message': '邮件发送成功',
            'data': result
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# django_emails/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/send-email/', views.send_email_view, name='send_email'),
    path('api/validate-email/<str:email>/', views.validate_email_view, name='validate_email'),
    path('api/check-config/', views.check_config_view, name='check_config'),
]
```

### 3. 与 Node.js 集成

```javascript
// email-service.js
const { spawn } = require('child_process');
const path = require('path');

class EmailMCPService {
    constructor(serverPath) {
        this.serverPath = serverPath;
        this.process = null;
    }

    async sendEmail(emailData) {
        const { to, subject, body, cc, bcc, attachments, body_format, priority } = emailData;

        return new Promise((resolve, reject) => {
            const child = spawn('uv', ['run', 'python', '-m', 'email_mcp_server'], {
                cwd: this.serverPath,
                stdio: ['pipe', 'pipe', 'pipe']
            });

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
                        cc,
                        bcc,
                        attachments,
                        body_format: body_format || "plain",
                        priority: priority || 3
                    }
                }
            };

            let output = '';

            child.stdout.on('data', (data) => {
                output += data.toString();
            });

            child.on('close', (code) => {
                try {
                    const response = JSON.parse(output);
                    if (response.error) {
                        reject(new Error(response.error.message));
                    } else {
                        resolve(response.result);
                    }
                } catch (parseError) {
                    reject(new Error('Failed to parse server response'));
                }
            });

            child.stdin.write(JSON.stringify(message) + '\n');
            child.stdin.end();
        });
    }

    async validateEmail(email) {
        // 类似的实现...
    }
}

// 使用示例
const emailService = new EmailMCPService('/path/to/email-mcp-server');

async function sendWelcomeEmail(userEmail, userName) {
    try {
        const result = await emailService.sendEmail({
            to: [userEmail],
            subject: `欢迎加入我们，${userName}！`,
            body: `亲爱的${userName}，欢迎注册我们的服务...`,
            body_format: 'html',
            priority: 3
        });

        console.log('邮件发送成功:', result);
    } catch (error) {
        console.error('邮件发送失败:', error);
    }
}

module.exports = EmailMCPService;
```

## [ALERT] 错误处理示例

### 1. 完整的错误处理

```python
def send_email_with_error_handling(email_data):
    """带完整错误处理的邮件发送"""

    try:
        # 验证输入数据
        if not email_data.get('to'):
            raise ValueError("收件人地址不能为空")

        if not email_data.get('subject'):
            raise ValueError("邮件主题不能为空")

        if not email_data.get('body'):
            raise ValueError("邮件内容不能为空")

        # 验证邮箱格式
        for email in email_data['to']:
            validation_result = validate_email(email)
            if not validation_result['valid']:
                raise ValueError(f"无效的邮箱地址: {email}")

        # 检查附件是否存在
        if email_data.get('attachments'):
            import os
            for attachment in email_data['attachments']:
                if not attachment.startswith('http'):  # 本地文件
                    if not os.path.exists(attachment):
                        raise FileNotFoundError(f"附件文件不存在: {attachment}")

        # 发送邮件
        result = send_email(
            to=email_data['to'],
            subject=email_data['subject'],
            body=email_data['body'],
            cc=email_data.get('cc'),
            bcc=email_data.get('bcc'),
            attachments=email_data.get('attachments'),
            body_format=email_data.get('body_format', 'plain'),
            priority=email_data.get('priority', 3),
            require_confirmation=email_data.get('require_confirmation')
        )

        return {
            'success': True,
            'message': '邮件发送成功',
            'data': result
        }

    except ValueError as e:
        return {
            'success': False,
            'error_type': 'ValidationError',
            'error_message': str(e)
        }

    except FileNotFoundError as e:
        return {
            'success': False,
            'error_type': 'FileError',
            'error_message': str(e)
        }

    except Exception as e:
        # 捕获所有其他错误
        return {
            'success': False,
            'error_type': 'ServerError',
            'error_message': f"邮件发送失败: {str(e)}"
        }

# 使用示例
email_data = {
    'to': ['user@example.com'],
    'subject': '测试邮件',
    'body': '这是一封测试邮件',
    'attachments': ['nonexistent.pdf']  # 故意使用不存在的文件
}

result = send_email_with_error_handling(email_data)
print(result)
# 输出: {'success': False, 'error_type': 'FileError', 'error_message': '附件文件不存在: nonexistent.pdf'}
```

### 2. 重试机制

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        print(f"尝试 {attempt + 1} 失败，{delay}秒后重试...")
                        time.sleep(delay)
                        delay *= 2  # 指数退避
                    else:
                        print(f"所有 {max_retries} 次尝试都失败了")

            raise last_exception
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=2)
def send_email_with_retry(email_data):
    """带重试机制的邮件发送"""
    return send_email(**email_data)

# 使用示例
try:
    result = send_email_with_retry({
        'to': ['user@example.com'],
        'subject': '重要邮件',
        'body': '这封邮件会自动重试发送'
    })
    print("邮件发送成功:", result)
except Exception as e:
    print("邮件发送最终失败:", e)
```

## [BOLT] 性能优化示例

### 1. 批量邮件发送

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def send_bulk_emails_async(email_list, email_template, max_workers=5):
    """异步批量发送邮件"""

    def send_single_email(recipient_data):
        """发送单个邮件"""
        try:
            # 根据模板个性化邮件内容
            personalized_content = email_template.format(**recipient_data)

            result = send_email(
                to=[recipient_data['email']],
                subject=recipient_data.get('subject', '批量邮件'),
                body=personalized_content,
                require_confirmation=False  # 批量发送跳过确认
            )

            return {
                'email': recipient_data['email'],
                'success': True,
                'result': result
            }
        except Exception as e:
            return {
                'email': recipient_data['email'],
                'success': False,
                'error': str(e)
            }

    # 使用线程池并发发送
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(send_single_email, email_list))

    # 统计结果
    success_count = sum(1 for r in results if r['success'])
    failure_count = len(results) - success_count

    return {
        'total': len(results),
        'success': success_count,
        'failure': failure_count,
        'results': results
    }

# 使用示例
email_template = """
亲爱的{name}：

您好！这是我们的个性化邮件内容。

您的会员等级：{tier}
最近的消费金额：{amount}
专属优惠：{offer}

祝好！
团队
"""

email_list = [
    {
        'email': 'user1@example.com',
        'name': '张三',
        'tier': 'VIP',
        'amount': '1,234',
        'offer': '8折优惠'
    },
    {
        'email': 'user2@example.com',
        'name': '李四',
        'tier': '黄金会员',
        'amount': '567',
        'offer': '9折优惠'
    }
    # ... 更多收件人
]

# 发送批量邮件
result = await send_bulk_emails_async(email_list, email_template)
print(f"批量发送完成: 成功 {result['success']} 封，失败 {result['failure']} 封")
```

### 2. 内存优化的附件处理

```python
import os
import tempfile
from pathlib import Path

def optimize_attachments(attachment_paths, max_total_size=25*1024*1024):
    """优化附件处理，减少内存使用"""

    optimized_attachments = []
    current_size = 0

    for attachment_path in attachment_paths:
        # 获取文件大小
        file_size = os.path.getsize(attachment_path)

        # 检查是否超出总大小限制
        if current_size + file_size > max_total_size:
            print(f"警告: 跳过 {attachment_path}，超出大小限制")
            continue

        # 对于大文件，使用临时文件流式处理
        if file_size > 10 * 1024 * 1024:  # 10MB以上的文件
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            try:
                # 这里可以添加文件压缩逻辑
                with open(attachment_path, 'rb') as original:
                    temp_file.write(original.read())

                optimized_attachments.append(temp_file.name)
                current_size += file_size

            except Exception as e:
                print(f"处理文件 {attachment_path} 失败: {e}")
                temp_file.close()
                os.unlink(temp_file.name)
                continue
        else:
            # 小文件直接添加
            optimized_attachments.append(attachment_path)
            current_size += file_size

    return optimized_attachments

def send_email_with_optimized_attachments(email_data):
    """发送带优化附件的邮件"""

    if 'attachments' in email_data:
        optimized_attachments = optimize_attachments(email_data['attachments'])
        email_data['attachments'] = optimized_attachments

    return send_email(**email_data)
```

## [EDIT] 最佳实践

### 1. 邮件模板管理

```python
class EmailTemplateManager:
    """邮件模板管理器"""

    def __init__(self, template_dir="templates"):
        self.template_dir = Path(template_dir)
        self.templates = {}
        self.load_templates()

    def load_templates(self):
        """加载所有模板文件"""
        for template_file in self.template_dir.glob("*.html"):
            template_name = template_file.stem
            with open(template_file, 'r', encoding='utf-8') as f:
                self.templates[template_name] = f.read()

    def get_template(self, template_name, **kwargs):
        """获取并渲染模板"""
        if template_name not in self.templates:
            raise ValueError(f"模板 '{template_name}' 不存在")

        template = self.templates[template_name]
        return template.format(**kwargs)

# 使用示例
template_manager = EmailTemplateManager()

# 发送使用模板的邮件
welcome_email_content = template_manager.get_template(
    'welcome',
    user_name="张三",
    company_name="科技公司",
    login_url="https://app.company.com/login"
)

send_email(
    to=["newuser@example.com"],
    subject="欢迎注册",
    body=welcome_email_content,
    body_format="html"
)
```

### 2. 配置管理最佳实践

```python
# config/production.env
EMAIL_ADDRESS=production@company.com
EMAIL_PASSWORD=production_password
LOG_LEVEL=WARNING
REQUIRE_CONFIRMATION=true

# config/development.env
EMAIL_ADDRESS=dev@company.com
EMAIL_PASSWORD=dev_password
LOG_LEVEL=DEBUG
REQUIRE_CONFIRMATION=false

# config/testing.env
EMAIL_ADDRESS=test@company.com
EMAIL_PASSWORD=test_password
LOG_LEVEL=ERROR
REQUIRE_CONFIRMATION=false
```

---

**最后更新**: 2025年11月23日
**示例版本**: v1.0.0

更多示例和最佳实践将持续更新，如有特定的使用场景需求，欢迎提交 Issue！