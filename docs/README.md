# Email MCP 服务器文档中心

欢迎来到 Email MCP 服务器的文档中心！这里包含了使用、配置和开发 Email MCP 服务器的所有信息。

## [BOOKS] 文档导航

### [ROCKET] 快速开始
- [**安装指南**](docs/INSTALLATION.md) - 详细的安装和环境配置说明
- [**快速上手**](docs/QUICKSTART.md) - 5分钟快速运行邮件服务器
- [**基本使用**](README.md#使用示例) - 基本的使用示例

### [TOOLS] 配置与设置
- [**配置指南**](docs/CONFIGURATION.md) - 完整的配置参数说明
- [**邮箱提供商设置**](docs/EMAIL_PROVIDERS.md) - QQ邮箱、Gmail等配置详情
- [**环境变量参考**](docs/ENVIRONMENT_VARIABLES.md) - 所有环境变量详细说明
- [**require_confirmation 功能**](REQUIRE_CONFIRMATION_GUIDE.md) - 邮件发送确认功能指南

### [PLUG] 集成指南
- [**MCP 客户端配置**](docs/MCP_CLIENT_SETUP.md) - 各种AI开发环境配置
- [**API 文档**](docs/API.md) - 完整的API接口说明
- [**示例代码**](docs/EXAMPLES.md) - 丰富的使用示例和代码片段
- [**Docker 部署**](docs/DOCKER_DEPLOYMENT.md) - 容器化部署指南

###  开发指南
- [**开发环境搭建**](docs/DEVELOPMENT_SETUP.md) - 开发环境配置
- [**贡献指南**](CONTRIBUTING.md) - 如何参与项目开发
- [**测试指南**](docs/TESTING.md) - 测试编写和执行
- [**代码规范**](docs/CODING_STANDARDS.md) - 代码风格和质量标准

### [DOCS] 深入指南
- [**架构设计**](docs/ARCHITECTURE.md) - 系统架构和设计原理
- [**性能优化**](docs/PERFORMANCE.md) - 性能调优和最佳实践
- [**安全指南**](docs/SECURITY.md) - 安全配置和最佳实践
- [**故障排除**](docs/TROUBLESHOOTING.md) - 常见问题和解决方案

### 文件 参考资料
- [**变更日志**](CHANGELOG.md) - 版本变更记录
- [**FAQ**](docs/FAQ.md) - 常见问题解答
- [**虚拟环境使用指南**](虚拟环境使用指南.md) - uv和venv使用指南
- [**测试计划**](测试计划.md) - 项目测试现状和计划

## [TARGET] 按使用场景导航

### [BEGINNER] 初学者
1. 阅读 [安装指南](docs/INSTALLATION.md)
2. 完成 [快速上手](docs/QUICKSTART.md)
3. 查看 [基本使用示例](README.md#使用示例)

### [TOOLS] 系统管理员
1. 参考 [配置指南](docs/CONFIGURATION.md)
2. 查阅 [邮箱提供商设置](docs/EMAIL_PROVIDERS.md)
3. 了解 [安全配置](docs/SECURITY.md)

### [DEVELOPER] 开发者
1. 搭建 [开发环境](docs/DEVELOPMENT_SETUP.md)
2. 阅读 [API 文档](docs/API.md)
3. 查看 [示例代码](docs/EXAMPLES.md)
4. 了解 [贡献流程](CONTRIBUTING.md)

### [ROCKET] DevOps 工程师
1. 学习 [Docker 部署](docs/DOCKER_DEPLOYMENT.md)
2. 参考 [性能优化](docs/PERFORMANCE.md)
3. 查阅 [故障排除](docs/TROUBLESHOOTING.md)

## [SCANNER] 文档状态

### [OK] 已完成的文档
- [x] README.md - 项目主文档
- [x] CHANGELOG.md - 变更日志
- [x] CONTRIBUTING.md - 贡献指南
- [x] docs/API.md - API文档
- [x] docs/MCP_CLIENT_SETUP.md - 客户端配置
- [x] docs/CONFIGURATION.md - 配置指南
- [x] docs/DEVELOPMENT_GUIDE.md - 开发指南
- [x] docs/EXAMPLES.md - 示例代码
- [x] docs/FAQ.md - 常见问题
- [x] docs/TROUBLESHOOTING.md - 故障排除
- [x] REQUIRE_CONFIRMATION_GUIDE.md - 确认功能指南
- [x] 虚拟环境使用指南.md - 环境配置指南
- [x] 测试划.md - 测试计划总结

### [WAIT] 待完善的文档
- [ ] docs/INSTALLATION.md - 安装指南
- [ ] docs/QUICKSTART.md - 快速开始
- [ ] docs/EMAIL_PROVIDERS.md - 邮箱提供商设置
- [ ] docs/ENVIRONMENT_VARIABLES.md - 环境变量参考
- [ ] docs/DOCKER_DEPLOYMENT.md - Docker部署
- [ ] docs/DEVELOPMENT_SETUP.md - 开发环境搭建
- [ ] docs/TESTING.md - 测试指南
- [ ] docs/CODING_STANDARDS.md - 代码规范
- [ ] docs/ARCHITECTURE.md - 架构设计
- [ ] docs/PERFORMANCE.md - 性能优化
- [ ] docs/SECURITY.md - 安全指南

## [MAGNIFY] 快速查找

### 常见问题快速导航
- **如何配置Gmail？** → [邮箱提供商设置](docs/EMAIL_PROVIDERS.md#gmail)
- **如何添加附件？** → [示例代码](docs/EXAMPLES.md#attachments)
- **如何在Claude Code中使用？** → [MCP客户端配置](docs/MCP_CLIENT_SETUP.md#claude-code)
- **遇到错误怎么办？** → [故障排除](docs/TROUBLESHOOTING.md)
- **如何参与开发？** → [贡献指南](CONTRIBUTING.md)

### 配置参数快速查找
- **基本配置** → [配置指南](docs/CONFIGURATION.md#basic-settings)
- **SMTP设置** → [配置指南](docs/CONFIGURATION.md#smtp-settings)
- **安全设置** → [配置指南](docs/CONFIGURATION.md#security-settings)
- **性能设置** → [配置指南](docs/CONFIGURATION.md#performance-settings)

## [PHONE-OLD] 获取帮助

如果您在使用过程中遇到问题：

1. **查阅文档**：首先查看相关的文档页面
2. **搜索FAQ**：在 [FAQ页面](docs/FAQ.md) 中搜索常见问题
3. **查看Issues**：在 GitHub仓库中搜索相关的 Issue
4. **创建Issue**：如果问题未解决，请创建新的 GitHub Issue
5. **联系维护者**：通过 GitHub 联系项目维护者

## [SYNC] 文档更新

文档会随项目版本持续更新。每次版本发布时，相关文档也会同步更新。请查看 [变更日志](CHANGELOG.md) 了解最新的文档更新情况。

---

**最后更新时间**: 2025年11月23日
**文档版本**: v1.0.0
**项目版本**: v0.2.0

如有文档相关的问题或建议，欢迎提交 Issue 或 Pull Request！