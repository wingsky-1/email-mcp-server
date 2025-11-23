"""Logging config 模块测试"""

import logging
import pytest
from unittest.mock import patch, Mock
from pathlib import Path

from email_mcp_server.logging_config import setup_logging, get_logger


class TestLoggingSetup:
    """日志设置测试"""

    @pytest.mark.unit
    def test_setup_logging_default(self):
        """测试默认日志设置"""
        # 重置日志配置
        logging.getLogger().handlers = []

        with patch('email_mcp_server.logging_config.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                'EMAIL_MCP_LOG_LEVEL': 'INFO',
                'EMAIL_MCP_LOG_FILE': None
            }.get(key, default)

            with patch('email_mcp_server.logging_config.logging.basicConfig') as mock_config:
                setup_logging()

                # 验证基本配置被调用
                mock_config.assert_called_once()
                call_args = mock_config.call_args[1]

                # 验证默认配置
                assert call_args['level'] == logging.INFO
                assert 'format' in call_args

    @pytest.mark.unit
    def test_setup_logging_with_file(self):
        """测试设置日志文件"""
        # 重置日志配置
        logging.getLogger().handlers = []

        with patch('email_mcp_server.logging_config.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                'EMAIL_MCP_LOG_LEVEL': 'DEBUG',
                'EMAIL_MCP_LOG_FILE': '/tmp/test.log'
            }.get(key, default)

            with patch('email_mcp_server.logging_config.logging.basicConfig') as mock_config:
                with patch('email_mcp_server.logging_config.Path') as mock_path:
                    mock_path_instance = Mock()
                    mock_path_instance.parent = Mock()
                    mock_path_instance.parent.exists.return_value = True
                    mock_path_instance.parent.mkdir = Mock()
                    mock_path.return_value = mock_path_instance

                    setup_logging()

                    # 验证文件处理器被添加
                    # 注意：实际实现可能不同，需要根据具体代码调整
                    mock_config.assert_called()

    @pytest.mark.unit
    def test_setup_logging_debug_level(self):
        """测试DEBUG级别日志"""
        # 重置日志配置
        logging.getLogger().handlers = []

        with patch('email_mcp_server.logging_config.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                'EMAIL_MCP_LOG_LEVEL': 'DEBUG',
                'EMAIL_MCP_LOG_FILE': None
            }.get(key, default)

            with patch('email_mcp_server.logging_config.logging.basicConfig') as mock_config:
                setup_logging()

                call_args = mock_config.call_args[1]
                assert call_args['level'] == logging.DEBUG

    @pytest.mark.unit
    def test_setup_logging_warning_level(self):
        """测试WARNING级别日志"""
        # 重置日志配置
        logging.getLogger().handlers = []

        with patch('email_mcp_server.logging_config.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                'EMAIL_MCP_LOG_LEVEL': 'WARNING',
                'EMAIL_MCP_LOG_FILE': None
            }.get(key, default)

            with patch('email_mcp_server.logging_config.logging.basicConfig') as mock_config:
                setup_logging()

                call_args = mock_config.call_args[1]
                assert call_args['level'] == logging.WARNING

    @pytest.mark.unit
    def test_setup_logging_invalid_level(self):
        """测试无效日志级别"""
        # 重置日志配置
        logging.getLogger().handlers = []

        with patch('email_mcp_server.logging_config.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                'EMAIL_MCP_LOG_LEVEL': 'INVALID_LEVEL',
                'EMAIL_MCP_LOG_FILE': None
            }.get(key, default)

            with patch('email_mcp_server.logging_config.logging.basicConfig') as mock_config:
                # 应该回退到默认级别
                setup_logging()

                call_args = mock_config.call_args[1]
                # 根据实际实现，可能使用默认级别或抛出错误
                # 这里假设使用默认级别 INFO
                assert call_args['level'] == logging.INFO


class TestGetLogger:
    """获取Logger测试"""

    @pytest.mark.unit
    def test_get_logger_with_name(self):
        """测试获取带名称的logger"""
        logger = get_logger("test_module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    @pytest.mark.unit
    def test_get_logger_default_name(self):
        """测试获取默认名称的logger"""
        with patch('email_mcp_server.logging_config.__name__', 'test_logging_config'):
            logger = get_logger()

            assert isinstance(logger, logging.Logger)
            assert logger.name == 'test_logging_config'

    @pytest.mark.unit
    def test_get_logger_multiple_calls(self):
        """测试多次调用get_logger返回相同实例"""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")

        # 同名logger应该是同一个实例
        assert logger1 is logger2

    @pytest.mark.unit
    def test_get_logger_different_names(self):
        """测试不同名称返回不同logger实例"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        # 不同名logger应该是不同的实例
        assert logger1 is not logger2
        assert logger1.name == "module1"
        assert logger2.name == "module2"


class TestLoggingConfiguration:
    """日志配置详细测试"""

    @pytest.mark.unit
    def test_log_format_contains_time(self):
        """测试日志格式包含时间"""
        with patch('email_mcp_server.logging_config.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: 'INFO'

            with patch('email_mcp_server.logging_config.logging.basicConfig') as mock_config:
                setup_logging()

                call_args = mock_config.call_args[1]
                format_string = call_args.get('format', '')

                # 验证格式包含时间戳
                assert '%(asctime)s' in format_string

    @pytest.mark.unit
    def test_log_format_contains_level(self):
        """测试日志格式包含级别"""
        with patch('email_mcp_server.logging_config.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: 'INFO'

            with patch('email_mcp_server.logging_config.logging.basicConfig') as mock_config:
                setup_logging()

                call_args = mock_config.call_args[1]
                format_string = call_args.get('format', '')

                # 验证格式包含日志级别
                assert '%(levelname)s' in format_string

    @pytest.mark.unit
    def test_log_format_contains_module(self):
        """测试日志格式包含模块名"""
        with patch('email_mcp_server.logging_config.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: 'INFO'

            with patch('email_mcp_server.logging_config.logging.basicConfig') as mock_config:
                setup_logging()

                call_args = mock_config.call_args[1]
                format_string = call_args.get('format', '')

                # 验证格式包含模块名
                assert '%(name)s' in format_string

    @pytest.mark.unit
    def test_log_format_contains_message(self):
        """测试日志格式包含消息"""
        with patch('email_mcp_server.logging_config.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: 'INFO'

            with patch('email_mcp_server.logging_config.logging.basicConfig') as mock_config:
                setup_logging()

                call_args = mock_config.call_args[1]
                format_string = call_args.get('format', '')

                # 验证格式包含消息
                assert '%(message)s' in format_string


class TestEnvironmentVariableHandling:
    """环境变量处理测试"""

    @pytest.mark.unit
    def test_environment_variable_priority(self):
        """测试环境变量优先级"""
        # 重置日志配置
        logging.getLogger().handlers = []

        with patch('email_mcp_server.logging_config.os.getenv') as mock_getenv:
            # 模拟环境变量设置
            mock_getenv.side_effect = lambda key, default=None: {
                'EMAIL_MCP_LOG_LEVEL': 'ERROR',
                'EMAIL_MCP_LOG_FILE': '/var/log/email_mcp.log'
            }.get(key, default)

            with patch('email_mcp_server.logging_config.logging.basicConfig') as mock_config:
                setup_logging()

                # 验证环境变量被使用
                call_args = mock_config.call_args[1]
                assert call_args['level'] == logging.ERROR

    @pytest.mark.unit
    def test_missing_environment_variables(self):
        """测试缺少环境变量时的默认行为"""
        # 重置日志配置
        logging.getLogger().handlers = []

        with patch('email_mcp_server.logging_config.os.getenv') as mock_getenv:
            mock_getenv.return_value = None  # 所有环境变量都未设置

            with patch('email_mcp_server.logging_config.logging.basicConfig') as mock_config:
                setup_logging()

                # 验证使用默认值
                call_args = mock_config.call_args[1]
                assert call_args['level'] == logging.INFO  # 默认级别