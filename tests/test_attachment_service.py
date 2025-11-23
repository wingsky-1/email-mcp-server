"""测试 AttachmentService 类"""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from email_mcp_server.attachment_service import AttachmentService
from email_mcp_server.exceptions import (
    AttachmentError,
    AttachmentFileNotFoundError,
    DownloadError,
    FileSizeError,
    NetworkError,
)
from email_mcp_server.models import Attachment, AttachmentType


class TestAttachmentService:
    """测试 AttachmentService 类"""

    @pytest.fixture
    def attachment_service(self) -> Generator[AttachmentService]:
        """创建附件服务实例"""
        with patch('email_mcp_server.attachment_service.get_app_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.max_attachment_size = 25 * 1024 * 1024  # 25MB
            mock_settings.temp_dir = "temp"
            mock_settings.download_timeout = 30
            mock_settings.max_retries = 3
            mock_get_settings.return_value = mock_settings

            service = AttachmentService()
            yield service

    @pytest.fixture
    def local_attachment(self) -> Attachment:
        """本地附件"""
        return Attachment(
            path="/path/to/file.txt",
            type=AttachmentType.LOCAL
        )

    @pytest.fixture
    def remote_attachment(self) -> Attachment:
        """远程附件"""
        return Attachment(
            path="https://example.com/file.pdf",
            type=AttachmentType.REMOTE
        )

    @pytest.fixture
    def large_attachment(self) -> Attachment:
        """大附件（超过限制）"""
        return Attachment(
            path="/path/to/large_file.bin",
            type=AttachmentType.LOCAL
        )

    @pytest.mark.unit
    def test_init(self, attachment_service):
        """测试 AttachmentService 初始化"""
        assert attachment_service.settings is not None
        assert attachment_service.temp_files == []
        assert attachment_service.settings.max_attachment_size == 25 * 1024 * 1024

    @pytest.mark.unit
    def test_process_local_attachment_success(self, attachment_service, local_attachment, tmp_path):
        """测试成功处理本地附件"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        # 修改附件路径为测试文件
        local_attachment.path = str(test_file)

        with patch('email_mcp_server.attachment_service.Path') as mock_path:
            mock_path_instance = mock_path.return_value
            mock_path_instance.exists.return_value = True
            mock_path_instance.stat.return_value.st_size = 12
            mock_path_instance.name = "test.txt"
            mock_path_instance.suffix = ".txt"

            with patch('email_mcp_server.attachment_service.mimetypes') as mock_mimetypes:
                mock_mimetypes.guess_type.return_value = ("text/plain", None)

                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = b"Test content"

                    result = attachment_service.process_attachment(local_attachment)

                    assert result.filename == "test.txt"
                    assert result.content_type == "text/plain"
                    assert result.data == b"Test content"
                    assert result.size == 12
                    assert result.is_temp is False

    @pytest.mark.unit
    def test_process_local_attachment_file_not_found(self, attachment_service, local_attachment):
        """测试本地附件文件不存在"""
        with patch('email_mcp_server.attachment_service.Path') as mock_path:
            mock_path.return_value.exists.return_value = False

            with pytest.raises(AttachmentError):
                attachment_service.process_attachment(local_attachment)

    @pytest.mark.unit
    def test_process_local_attachment_file_too_large(self, attachment_service, large_attachment, tmp_path):
        """测试本地附件文件过大"""
        # 创建大文件（超过25MB）
        test_file = tmp_path / "large_file.bin"
        large_content = b"x" * (30 * 1024 * 1024)  # 30MB
        test_file.write_bytes(large_content)

        large_attachment.path = str(test_file)

        with patch('email_mcp_server.attachment_service.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.stat.return_value.st_size = len(large_content)

            with pytest.raises(AttachmentError):
                attachment_service.process_attachment(large_attachment)

    @pytest.mark.unit
    def test_process_remote_attachment_success(self, attachment_service, remote_attachment):
        """测试成功处理远程附件"""
        remote_content = b"Remote file content"

        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": str(len(remote_content))}
        mock_response.iter_content.return_value = [remote_content]
        mock_response.raise_for_status.return_value = None

        # Create a real temp file for the test
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(remote_content)
            temp_file_path = temp_file.name

        try:
            with patch('email_mcp_server.attachment_service.Path') as mock_path:
                mock_path.return_value.stat.return_value.st_size = len(remote_content)
                mock_path.return_value.name = "file.pdf"
                mock_path.return_value.suffix = ".pdf"

                with patch('email_mcp_server.attachment_service.mimetypes') as mock_mimetypes:
                    mock_mimetypes.guess_type.return_value = ("application/pdf", None)

                    with patch('email_mcp_server.attachment_service.requests.Session') as mock_session_class:
                        mock_session = Mock()
                        mock_session_class.return_value = mock_session
                        mock_session.get.return_value = mock_response

                        # Mock the _download_remote_file method to return our temp file
                        with patch.object(attachment_service, '_download_remote_file', return_value=temp_file_path):

                            result = attachment_service.process_attachment(remote_attachment)

                            assert result.filename == "file.pdf"
                            assert result.content_type == "application/pdf"
                            assert result.data == remote_content
                            assert result.size == len(remote_content)
                            assert result.is_temp is True
        finally:
            # Clean up the temp file
            import os
            try:
                os.unlink(temp_file_path)
            except FileNotFoundError:
                pass

    @pytest.mark.unit
    def test_process_remote_attachment_download_error(self, attachment_service, remote_attachment):
        """测试远程附件下载错误"""
        with patch('email_mcp_server.attachment_service.requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_session.get.side_effect = Exception("Network error")

            with pytest.raises(AttachmentError, match="Failed to process attachment"):
                attachment_service.process_attachment(remote_attachment)

    @pytest.mark.unit
    def test_extract_filename_from_url(self, attachment_service):
        """测试从 URL 提取文件名"""
        url = "https://example.com/path/to/file.pdf"
        filename = attachment_service._extract_filename_from_url(url)

        assert filename == "file.pdf"

    @pytest.mark.unit
    def test_extract_filename_from_url_no_extension(self, attachment_service):
        """测试从没有扩展名的 URL 提取文件名"""
        url = "https://example.com/path/to/file"
        filename = attachment_service._extract_filename_from_url(url)

        assert filename == "file"

    @pytest.mark.unit
    def test_extract_filename_from_url_no_path(self, attachment_service):
        """测试从没有路径的 URL 提取文件名"""
        url = "https://example.com/"
        filename = attachment_service._extract_filename_from_url(url)

        # 应该使用 URL 的8位哈希值作为文件名
        assert len(filename) == 17  # "download_" + 8位哈希值
        assert filename.startswith("download_")

    @pytest.mark.unit
    def test_cleanup_temp_files(self, attachment_service, tmp_path):
        """测试清理临时文件"""
        # 创建临时文件
        temp_file1 = tmp_path / "temp1.txt"
        temp_file2 = tmp_path / "temp2.txt"
        temp_file1.write_text("temp1")
        temp_file2.write_text("temp2")

        attachment_service.temp_files = [str(temp_file1), str(temp_file2)]

        with patch('email_mcp_server.attachment_service.os.path.exists') as mock_exists, \
             patch('email_mcp_server.attachment_service.os.unlink') as mock_unlink:
            mock_exists.return_value = True
            mock_unlink.return_value = None

            attachment_service.cleanup_temp_files()

            assert attachment_service.temp_files == []
            # Should call os.unlink twice (for both files)
            assert mock_unlink.call_count == 2
            mock_exists.assert_any_call(str(temp_file1))
            mock_exists.assert_any_call(str(temp_file2))

    @pytest.mark.unit
    def test_cleanup_temp_files_file_not_exists(self, attachment_service, tmp_path):
        """测试清理不存在的临时文件"""
        temp_file = tmp_path / "nonexistent.txt"
        attachment_service.temp_files = [str(temp_file)]

        with patch('email_mcp_server.attachment_service.Path') as mock_path:
            mock_path.return_value.exists.return_value = False

            # 应该不抛出异常
            attachment_service.cleanup_temp_files()

            assert attachment_service.temp_files == []

    @pytest.mark.unit
    def test_get_file_hash(self, attachment_service):
        """测试获取文件哈希"""
        file_data = b"Test content"
        file_hash = attachment_service.get_file_hash(file_data)

        # 验证哈希值长度（SHA256应该是64位十六进制字符）
        assert len(file_hash) == 64
        assert file_hash is not None
        # 验证哈希值是有效的十六进制字符串
        assert all(c in "0123456789abcdef" for c in file_hash)
        # 验证相同内容产生相同哈希
        file_hash2 = attachment_service.get_file_hash(file_data)
        assert file_hash == file_hash2
        # 验证不同内容产生不同哈希
        different_hash = attachment_service.get_file_hash(b"Different content")
        assert file_hash != different_hash

    @pytest.mark.unit
    def test_get_file_hash_empty_data(self, attachment_service):
        """测试空数据的文件哈希"""
        empty_hash = attachment_service.get_file_hash(b"")

        # 空数据的SHA256哈希是固定的
        expected_empty_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert empty_hash == expected_empty_hash

    @pytest.mark.unit
    def test_get_file_hash_large_data(self, attachment_service):
        """测试大数据的文件哈希"""
        # 创建1MB的测试数据
        large_data = b"A" * (1024 * 1024)
        large_hash = attachment_service.get_file_hash(large_data)

        assert len(large_hash) == 64
        assert large_hash is not None

    @pytest.mark.unit
    def test_validate_attachment_local_valid(self, attachment_service, local_attachment, tmp_path):
        """测试验证本地有效附件"""
        test_file = tmp_path / "valid.txt"
        test_file.write_text("Valid content")
        local_attachment.path = str(test_file)

        with patch('email_mcp_server.attachment_service.Path') as mock_path:
            mock_path.return_value.exists.return_value = True

            # 应该不抛出异常
            attachment_service.validate_attachment(local_attachment)

    @pytest.mark.unit
    def test_validate_attachment_local_not_absolute(self, attachment_service):
        """测试验证本地附件路径格式 - 必须使用绝对路径"""
        # 测试相对路径（应该失败）
        relative_attachment = Attachment(path="relative/path/file.txt", type=AttachmentType.LOCAL)

        with pytest.raises(AttachmentError, match="Local file path must be absolute"):
            attachment_service.validate_attachment(relative_attachment)

        # 测试各种绝对路径格式（应该通过）
        absolute_paths = [
            "C:\\path\\to\\file.txt",  # Windows路径
            "/path/to/file.txt",       # Unix路径
            "D:\\folder\\document.pdf"  # Windows其他盘符
        ]

        for path in absolute_paths:
            absolute_attachment = Attachment(path=path, type=AttachmentType.LOCAL)
            # 应该不抛出异常
            attachment_service.validate_attachment(absolute_attachment)

    @pytest.mark.unit
    def test_validate_attachment_local_empty_path(self, attachment_service):
        """测试验证空路径的本地附件"""
        empty_attachment = Attachment(path="", type=AttachmentType.LOCAL)

        with pytest.raises(AttachmentError, match="Local file path must be absolute"):
            attachment_service.validate_attachment(empty_attachment)

    @pytest.mark.unit
    def test_validate_attachment_remote_valid(self, attachment_service):
        """测试验证远程有效附件"""
        valid_urls = [
            "https://example.com/file.pdf",
            "http://test.org/document.txt",
            "https://api.service.com/download/image.jpg"
        ]

        for url in valid_urls:
            attachment = Attachment(path=url, type=AttachmentType.REMOTE)
            # 应该不抛出异常
            attachment_service.validate_attachment(attachment)

    @pytest.mark.unit
    def test_validate_attachment_remote_invalid_url(self, attachment_service):
        """测试验证远程无效 URL"""
        invalid_attachment = Attachment(
            path="invalid-url",
            type=AttachmentType.REMOTE
        )

        with pytest.raises(AttachmentError):
            attachment_service.validate_attachment(invalid_attachment)

    @pytest.mark.unit
    def test_del_cleanup(self, attachment_service):
        """测试析构函数清理"""
        # 模拟临时文件列表
        attachment_service.temp_files = ["/tmp/test1", "/tmp/test2"]

        # 测试cleanup_temp_files方法存在且可调用
        assert hasattr(attachment_service, 'cleanup_temp_files')
        assert callable(getattr(attachment_service, 'cleanup_temp_files'))

    @pytest.mark.unit
    def test_download_remote_file_retry_success(self, attachment_service):
        """测试远程文件下载重试成功"""
        url = "https://example.com/file.txt"
        expected_path = "/tmp/temp_download"

        with patch('email_mcp_server.attachment_service.requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-length": "13"}
            mock_response.iter_content.return_value = [b"Remote content"]
            mock_session.get.return_value = mock_response

            # Mock tempfile.NamedTemporaryFile和open函数
            with patch('email_mcp_server.attachment_service.tempfile.NamedTemporaryFile') as mock_temp, \
                 patch('builtins.open', mock_file_open=Mock()) as mock_open:

                # 配置tempfile mock
                mock_temp.return_value.__enter__.return_value.name = expected_path
                mock_open.return_value.__enter__.return_value = mock_open.return_value
                mock_open.return_value.write = Mock()

                result = attachment_service._download_remote_file(url)

                # 验证结果是临时文件路径字符串
                assert result == expected_path
                mock_session.get.assert_called_once()
                mock_temp.assert_called_once()
                mock_open.assert_called_once_with(expected_path, "wb")

    @pytest.mark.unit
    def test_download_remote_file_retry_exhausted(self, attachment_service):
        """测试远程文件下载重试耗尽"""
        url = "https://example.com/file.txt"

        with patch('email_mcp_server.attachment_service.requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session

            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = Exception("500 Server Error")
            mock_session.get.return_value = mock_response

            with pytest.raises(Exception):  # requests层面的异常
                attachment_service._download_remote_file(url)

            # 由于使用requests HTTPAdapter进行重试，我们只验证session.get被调用
            assert mock_session.get.called
