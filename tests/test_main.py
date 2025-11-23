"""Main 模块测试"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import logging

from email_mcp_server.main import main, create_server, get_server


class TestMainFunction:
    """Main 函数测试"""

    @pytest.mark.unit
    def test_create_server(self):
        """测试创建服务器"""
        # 重置全局实例
        with patch('email_mcp_server.main._mcp_instance', None):
            with patch('email_mcp_server.main.FastMCP') as mock_fastmcp:
                mock_server = Mock()
                mock_fastmcp.return_value = mock_server

                with patch('email_mcp_server.main.register_email_tools'):
                    with patch('email_mcp_server.main.get_email_settings'):
                        server = create_server()

                        # 验证 FastMCP 被正确调用
                        mock_fastmcp.assert_called_once_with(
                            name="Email MCP Server",
                            instructions="一个强大的邮件发送MCP服务器，支持QQ邮箱和Gmail，可以发送文本、HTML邮件和附件。",
                            website_url="https://github.com/your-email/email-mcp-server",
                            debug=False,
                            log_level="INFO",
                        )

                        # 验证返回的服务器实例
                        assert server is mock_server

    @pytest.mark.unit
    def test_create_server_with_custom_name(self):
        """测试使用自定义名称创建服务器"""
        # 重置全局实例
        with patch('email_mcp_server.main._mcp_instance', None):
            with patch('email_mcp_server.main.FastMCP') as mock_fastmcp:
                mock_server = Mock()
                mock_fastmcp.return_value = mock_server

                with patch('email_mcp_server.main.register_email_tools'):
                    with patch('email_mcp_server.main.get_email_settings'):
                        create_server("Custom Server Name")

                        # 验证自定义名称被使用
                        mock_fastmcp.assert_called_once()
                        call_kwargs = mock_fastmcp.call_args[1]
                        assert call_kwargs['name'] == "Custom Server Name"

    @pytest.mark.unit
    def test_main_function_keyboard_interrupt(self):
        """测试键盘中断处理"""
        with patch('email_mcp_server.main.create_server') as mock_create:
            mock_server = Mock()
            mock_create.return_value = mock_server

            # 模拟键盘中断
            mock_server.run.side_effect = KeyboardInterrupt()

            with patch('email_mcp_server.main.logger') as mock_logger:
                main()

                # 验证日志记录
                mock_logger.info.assert_any_call("Starting Email MCP Server in STDIO mode...")
                mock_logger.info.assert_any_call("Server stopped by user")

    @pytest.mark.unit
    def test_main_function_exception(self):
        """测试异常处理"""
        with patch('email_mcp_server.main.create_server') as mock_create:
            mock_server = Mock()
            mock_create.return_value = mock_server

            # 模拟异常
            test_error = ValueError("Test error")
            mock_server.run.side_effect = test_error

            with patch('email_mcp_server.main.logger') as mock_logger:
                with pytest.raises(ValueError, match="Test error"):
                    main()

                # 验证错误日志记录
                mock_logger.info.assert_any_call("Starting Email MCP Server in STDIO mode...")
                mock_logger.error.assert_called_with("Server error: Test error")


class TestServerConfiguration:
    """服务器配置测试"""

    @pytest.mark.unit
    def test_get_server_returns_existing_instance(self):
        """测试获取已存在的服务器实例"""
        mock_server = Mock()

        with patch('email_mcp_server.main._mcp_instance', mock_server):
            result = get_server()
            assert result is mock_server

    @pytest.mark.unit
    def test_get_server_creates_new_instance(self):
        """测试创建新的服务器实例"""
        with patch('email_mcp_server.main._mcp_instance', None):
            with patch('email_mcp_server.main.create_server') as mock_create:
                mock_server = Mock()
                mock_create.return_value = mock_server

                result = get_server()
                mock_create.assert_called_once()
                assert result is mock_server

    @pytest.mark.unit
    def test_server_singleton_behavior(self):
        """测试服务器单例行为"""
        with patch('email_mcp_server.main._mcp_instance', None):
            with patch('email_mcp_server.main.FastMCP') as mock_fastmcp:
                mock_server = Mock()
                mock_fastmcp.return_value = mock_server

                with patch('email_mcp_server.main.register_email_tools'):
                    with patch('email_mcp_server.main.get_email_settings'):
                        # 第一次调用创建实例
                        server1 = create_server()
                        # 第二次调用返回同一实例
                        server2 = get_server()

                        assert server1 is server2
                        # FastMCP应该只被调用一次
                        mock_fastmcp.assert_called_once()

    @pytest.mark.unit
    def test_server_tool_registration_success(self):
        """测试工具注册成功"""
        with patch('email_mcp_server.main._mcp_instance', None):
            with patch('email_mcp_server.main.FastMCP') as mock_fastmcp:
                mock_server = Mock()
                mock_fastmcp.return_value = mock_server

                with patch('email_mcp_server.main.register_email_tools') as mock_register:
                    with patch('email_mcp_server.main.get_email_settings'):
                        with patch('email_mcp_server.main.logger') as mock_logger:
                            server = create_server()

                            # 验证工具注册被调用
                            mock_register.assert_called_once_with(server)
                            # 验证成功日志
                            mock_logger.info.assert_any_call("Email tools registered successfully")

    @pytest.mark.unit
    def test_server_tool_registration_failure(self):
        """测试工具注册失败处理"""
        with patch('email_mcp_server.main._mcp_instance', None):
            with patch('email_mcp_server.main.FastMCP') as mock_fastmcp:
                mock_server = Mock()
                mock_fastmcp.return_value = mock_server

                with patch('email_mcp_server.main.register_email_tools') as mock_register:
                    mock_register.side_effect = Exception("Registration failed")

                    with patch('email_mcp_server.main.get_email_settings'):
                        with patch('email_mcp_server.main.logger') as mock_logger:
                            server = create_server()

                            # 验证错误日志
                            mock_logger.error.assert_called_with("Failed to register email tools: Registration failed")


class TestLoggingAndErrorHandling:
    """日志和错误处理测试"""

    @pytest.mark.unit
    def test_startup_logging(self):
        """测试启动日志"""
        with patch('email_mcp_server.main._mcp_instance', None):
            with patch('email_mcp_server.main.FastMCP') as mock_fastmcp:
                mock_server = Mock()
                mock_fastmcp.return_value = mock_server

                with patch('email_mcp_server.main.register_email_tools'):
                    with patch('email_mcp_server.main.get_email_settings') as mock_settings:
                        mock_settings.return_value = Mock(provider=Mock(value="gmail"))

                        with patch('email_mcp_server.main.logger') as mock_logger:
                            create_server()

                            # 验证启动日志
                            mock_logger.info.assert_any_call("Configured for email provider: gmail")
                            mock_logger.info.assert_any_call("Email MCP Server initialized successfully")

    @pytest.mark.unit
    def test_email_configuration_warning(self):
        """测试邮箱配置警告"""
        with patch('email_mcp_server.main._mcp_instance', None):
            with patch('email_mcp_server.main.FastMCP') as mock_fastmcp:
                mock_server = Mock()
                mock_fastmcp.return_value = mock_server

                with patch('email_mcp_server.main.register_email_tools'):
                    with patch('email_mcp_server.main.get_email_settings') as mock_settings:
                        mock_settings.side_effect = Exception("Config error")

                        with patch('email_mcp_server.main.logger') as mock_logger:
                            create_server()

                            # 验证警告日志
                            mock_logger.warning.assert_called_with("Email configuration issue: Config error")
                            mock_logger.info.assert_any_call("Server will start but email functions require proper configuration")

    @pytest.mark.unit
    def test_error_logging_with_exception_info(self):
        """测试异常信息日志"""
        with patch('email_mcp_server.main.create_server') as mock_create:
            mock_server = Mock()
            mock_create.return_value = mock_server

            # 模拟异常
            test_error = ValueError("Test ValueError")
            mock_server.run.side_effect = test_error

            with patch('email_mcp_server.main.logger') as mock_logger:
                with pytest.raises(ValueError, match="Test ValueError"):
                    main()

                # 验证错误日志包含异常信息
                mock_logger.error.assert_called_with("Server error: Test ValueError")

    @pytest.mark.unit
    def test_global_instance_management(self):
        """测试全局实例管理"""
        # 测试重置全局实例
        with patch('email_mcp_server.main._mcp_instance', None):
            with patch('email_mcp_server.main.FastMCP') as mock_fastmcp:
                mock_server1 = Mock()
                mock_fastmcp.return_value = mock_server1

                with patch('email_mcp_server.main.register_email_tools'):
                    with patch('email_mcp_server.main.get_email_settings'):
                        # 创建第一个实例
                        server1 = create_server()
                        assert server1 is mock_server1

                        # 模拟重置全局实例
                        with patch('email_mcp_server.main._mcp_instance', None):
                            mock_server2 = Mock()
                            mock_fastmcp.return_value = mock_server2

                            # 应该创建新实例
                            server2 = create_server()
                            assert server2 is mock_server2
                            assert server1 is not server2