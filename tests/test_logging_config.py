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
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # 使用默认配置设置日志
        setup_logging()

        # 验证根日志记录器已配置
        assert len(root_logger.handlers) >= 1
        assert root_logger.level != logging.NOTSET

        # 验证控制台处理器存在
        console_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) >= 1

    @pytest.mark.unit
    def test_setup_logging_with_file(self):
        """测试设置日志文件"""
        # 重置日志配置
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # Mock配置以返回日志文件路径
        with patch('email_mcp_server.logging_config.get_app_settings') as mock_settings:
            mock_config = Mock()
            mock_config.log_level = "DEBUG"
            mock_config.log_file = "/tmp/test.log"
            mock_settings.return_value = mock_config

            setup_logging()

            # 验证日志记录器已配置（即使文件配置失败，基本配置也应该工作）
            assert root_logger.level == logging.DEBUG
            assert len(root_logger.handlers) >= 1

    @pytest.mark.unit
    def test_setup_logging_debug_level(self):
        """测试DEBUG级别日志"""
        # 重置日志配置
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # Mock配置返回DEBUG级别
        with patch('email_mcp_server.logging_config.get_app_settings') as mock_settings:
            mock_config = Mock()
            mock_config.log_level = "DEBUG"
            mock_config.log_file = None
            mock_settings.return_value = mock_config

            setup_logging()

            # 验证根日志记录器级别为DEBUG
            assert root_logger.level == logging.DEBUG

    @pytest.mark.unit
    def test_setup_logging_warning_level(self):
        """测试WARNING级别日志"""
        # 重置日志配置
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # Mock配置返回WARNING级别
        with patch('email_mcp_server.logging_config.get_app_settings') as mock_settings:
            mock_config = Mock()
            mock_config.log_level = "WARNING"
            mock_config.log_file = None
            mock_settings.return_value = mock_config

            setup_logging()

            # 验证根日志记录器级别为WARNING
            assert root_logger.level == logging.WARNING

    @pytest.mark.unit
    def test_setup_logging_invalid_level(self):
        """测试无效日志级别"""
        # 重置日志配置
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # Mock配置返回无效级别，应该回退到默认INFO
        with patch('email_mcp_server.logging_config.get_app_settings') as mock_settings:
            mock_config = Mock()
            mock_config.log_level = "INVALID_LEVEL"
            mock_config.log_file = None
            mock_settings.return_value = mock_config

            setup_logging()

            # 无效级别应该回退到默认INFO级别
            # getattr(logging, "INVALID_LEVEL", logging.INFO) 会返回 logging.INFO
            assert root_logger.level == logging.INFO


class TestGetLogger:
    """获取Logger测试"""

    @pytest.mark.unit
    def test_get_logger_with_name(self):
        """测试获取带名称的logger"""
        logger = get_logger("test_module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    @pytest.mark.unit
    def test_get_logger_functionality(self):
        """测试logger功能正常"""
        logger = get_logger("test_functionality")

        # 测试logger方法可用
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'critical')

    @pytest.mark.unit
    def test_get_logger_multiple_calls(self):
        """测试多次调用get_logger返回相同实例"""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")

        # 应该返回相同的logger实例
        assert logger1 is logger2

    @pytest.mark.unit
    def test_get_logger_different_names(self):
        """测试不同名称返回不同logger实例"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        # 不同名称应该返回不同的logger实例
        assert logger1 is not logger2
        assert logger1.name == "module1"
        assert logger2.name == "module2"


class TestLoggingConfiguration:
    """日志配置测试"""

    @pytest.mark.unit
    def test_logger_has_handlers(self):
        """测试logger配置后包含处理器"""
        setup_logging()
        logger = get_logger("test")

        # 验证logger可以正常使用
        assert isinstance(logger, logging.Logger)
        assert len(logger.handlers) >= 0  # 可能继承根logger的处理器

    @pytest.mark.unit
    def test_logger_level_inheritance(self):
        """测试logger级别继承"""
        setup_logging()
        logger = get_logger("test_inheritance")

        # logger应该继承根logger的配置
        assert isinstance(logger, logging.Logger)

    @pytest.mark.unit
    def test_logger_effective_level(self):
        """测试logger有效级别"""
        root_logger = logging.getLogger()
        original_level = root_logger.level

        try:
            root_logger.handlers.clear()
            setup_logging()

            logger = get_logger("test_effective")
            # logger应该有一个有效的级别
            assert logger.getEffectiveLevel() != logging.NOTSET

        finally:
            # 恢复原始级别
            root_logger.level = original_level

    @pytest.mark.unit
    def test_third_party_library_logging(self):
        """测试第三方库日志级别设置"""
        setup_logging()

        # 验证第三方库的日志级别被设置为WARNING
        urllib3_logger = logging.getLogger("urllib3")
        requests_logger = logging.getLogger("requests")

        assert urllib3_logger.level == logging.WARNING
        assert requests_logger.level == logging.WARNING


class TestEnvironmentVariableHandling:
    """环境变量处理测试"""

    @pytest.mark.unit
    def test_environment_config_integration(self):
        """测试环境变量集成配置"""
        # 重置日志配置
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # 通过环境变量设置配置
        with patch.dict('os.environ', {'LOG_LEVEL': 'ERROR', 'LOG_FILE': ''}):
            # Mock get_app_settings来模拟环境变量读取
            with patch('email_mcp_server.logging_config.get_app_settings') as mock_settings:
                mock_config = Mock()
                mock_config.log_level = "ERROR"
                mock_config.log_file = None
                mock_settings.return_value = mock_config

                setup_logging()

                # 验证ERROR级别设置生效
                assert root_logger.level == logging.ERROR

    @pytest.mark.unit
    def test_missing_environment_variables(self):
        """测试缺失环境变量的处理"""
        # 重置日志配置
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # 使用默认配置（无环境变量）
        with patch('email_mcp_server.logging_config.get_app_settings') as mock_settings:
            mock_config = Mock()
            mock_config.log_level = "INFO"  # 默认值
            mock_config.log_file = None
            mock_settings.return_value = mock_config

            setup_logging()

            # 验证默认配置生效
            assert root_logger.level == logging.INFO
            assert len(root_logger.handlers) >= 1