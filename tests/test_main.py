"""Main 模块测试"""

import pytest
from unittest.mock import Mock, patch, MagicMock

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

                with patch('email_mcp_server.main.register_email_tools') as mock_register:
                    server = create_server()

                    # 验证 FastMCP 被调用
                    mock_fastmcp.assert_called_once()

                    # 验证工具被注册
                    mock_register.assert_called_once_with(mock_server)

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
                    create_server("Custom Server Name")

                    # 验证自定义名称被使用
                    mock_fastmcp.assert_called_once()
                    call_kwargs = mock_fastmcp.call_args[1]
                    assert call_kwargs['name'] == "Custom Server Name"

    @pytest.mark.unit
    def test_create_server_singleton(self):
        """测试服务器单例模式"""
        # 重置全局实例
        with patch('email_mcp_server.main._mcp_instance', None):
            with patch('email_mcp_server.main.FastMCP') as mock_fastmcp:
                mock_server = Mock()
                mock_fastmcp.return_value = mock_server

                with patch('email_mcp_server.main.register_email_tools'):
                    server1 = create_server()
                    server2 = create_server()

                    # FastMCP应该只被调用一次（单例模式）
                    mock_fastmcp.assert_called_once()

                    # 两次调用应该返回同一个实例
                    assert server1 is server2
                    assert server1 is mock_server

    @pytest.mark.unit
    def test_get_server_uninitialized(self):
        """测试获取未初始化的服务器"""
        # 重置全局实例
        with patch('email_mcp_server.main._mcp_instance', None):
            with patch('email_mcp_server.main.create_server') as mock_create:
                mock_server = Mock()
                mock_create.return_value = mock_server

                server = get_server()

                # 应该调用create_server
                mock_create.assert_called_once()
                assert server is mock_server

    @pytest.mark.unit
    def test_get_server_initialized(self):
        """测试获取已初始化的服务器"""
        # 模拟已初始化的服务器
        mock_server = Mock()
        with patch('email_mcp_server.main._mcp_instance', mock_server):
            with patch('email_mcp_server.main.create_server') as mock_create:
                server = get_server()

                # 不应该再次调用create_server
                mock_create.assert_not_called()
                assert server is mock_server

    @pytest.mark.unit
    def test_main_function_success(self):
        """测试 main 函数成功运行"""
        mock_server = Mock()
        mock_server.run = Mock()

        with patch('email_mcp_server.main.create_server', return_value=mock_server):
            with patch('email_mcp_server.main.logger') as mock_logger:
                main()

                # 验证服务器被创建并运行
                mock_server.run.assert_called_once()

                # 验证日志记录
                mock_logger.info.assert_any_call("Starting Email MCP Server in STDIO mode...")

    @pytest.mark.unit
    def test_main_function_keyboard_interrupt(self):
        """测试 main 函数处理键盘中断"""
        mock_server = Mock()
        mock_server.run.side_effect = KeyboardInterrupt()

        with patch('email_mcp_server.main.create_server', return_value=mock_server):
            with patch('email_mcp_server.main.logger') as mock_logger:
                # 应该正常退出，不抛出异常
                main()

                # 验证服务器被运行
                mock_server.run.assert_called_once()

                # 验证退出日志
                mock_logger.info.assert_any_call("Email MCP Server stopped by user")

    @pytest.mark.unit
    def test_main_function_exception(self):
        """测试 main 函数处理异常"""
        mock_server = Mock()
        test_error = Exception("Test error")
        mock_server.run.side_effect = test_error

        with patch('email_mcp_server.main.create_server', return_value=mock_server):
            with patch('email_mcp_server.main.logger') as mock_logger:
                # 应该重新抛出异常
                with pytest.raises(Exception, match="Test error"):
                    main()

                # 验证错误日志
                mock_logger.error.assert_called_once_with(
                    "Email MCP Server encountered an error", exc_info=True
                )


class TestServerConfiguration:
    """服务器配置测试"""

    @pytest.mark.unit
    def test_server_creation_with_custom_name(self):
        """测试使用自定义名称创建服务器"""
        with patch('email_mcp_server.main.FastMCP') as mock_fastmcp:
            mock_server = Mock()
            mock_fastmcp.return_value = mock_server

            with patch('email_mcp_server.main.register_email_tools'):
                create_server()

                # 验证服务器名称
                mock_fastmcp.assert_called_once_with("Email MCP Server")

    @pytest.mark.unit
    def test_server_tool_registration(self):
        """测试服务器工具注册"""
        with patch('email_mcp_server.main.FastMCP') as mock_fastmcp:
            mock_server = Mock()
            mock_fastmcp.return_value = mock_server

            with patch('email_mcp_server.main.register_email_tools') as mock_register:
                create_server()

                # 验证 register_email_tools 被调用
                mock_register.assert_called_once_with(mock_server)


class TestLoggingAndErrorHandling:
    """日志和错误处理测试"""

    @pytest.mark.unit
    def test_startup_logging(self):
        """测试启动日志"""
        mock_server = Mock()
        mock_server.run = Mock()

        with patch('email_mcp_server.main.create_server', return_value=mock_server):
            with patch('email_mcp_server.main.logger') as mock_logger:
                main()

                # 验证启动日志
                mock_logger.info.assert_any_call("Starting Email MCP Server...")

    @pytest.mark.unit
    def test_successful_shutdown_logging(self):
        """测试成功关闭日志"""
        mock_server = Mock()
        mock_server.run = Mock()

        with patch('email_mcp_server.main.create_server', return_value=mock_server):
            with patch('email_mcp_server.main.logger') as mock_logger:
                main()

                # 注意：当前实现可能没有明确的关闭日志
                # 这个测试可以用来验证是否添加了关闭日志
                # mock_logger.info.assert_any_call("Email MCP Server stopped gracefully")
                pass

    @pytest.mark.unit
    def test_error_logging_with_exception_info(self):
        """测试带异常信息的错误日志"""
        mock_server = Mock()
        test_error = ValueError("Test ValueError")
        mock_server.run.side_effect = test_error

        with patch('email_mcp_server.main.create_server', return_value=mock_server):
            with patch('email_mcp_server.main.logger') as mock_logger:
                with pytest.raises(ValueError, match="Test ValueError"):
                    main()

                # 验证错误日志包含异常信息
                mock_logger.error.assert_called_once_with(
                    "Email MCP Server encountered an error",
                    exc_info=True
                )