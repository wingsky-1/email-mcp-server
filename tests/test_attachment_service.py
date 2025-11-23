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
    def test_process_remote_attachment_success(self, attachment_service, remote_attachment, mock_requests_get):
        """测试成功处理远程附件"""
        remote_content = b"Remote file content"

        with patch('email_mcp_server.attachment_service.tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp_file = Mock()
            mock_temp_file.name = "/tmp/temp_file"
            mock_temp.__enter__.return_value = mock_temp_file

            with patch('email_mcp_server.attachment_service.Path') as mock_path:
                mock_path.return_value.stat.return_value.st_size = len(remote_content)
                mock_path.return_value.name = "file.pdf"
                mock_path.return_value.suffix = ".pdf"

                with patch('email_mcp_server.attachment_service.mimetypes') as mock_mimetypes:
                    mock_mimetypes.guess_type.return_value = ("application/pdf", None)

                    with patch('builtins.open', create=True) as mock_open:
                        mock_open.return_value.__enter__.return_value.read.return_value = remote_content

                        result = attachment_service.process_attachment(remote_attachment)

                        assert result.filename == "file.pdf"
                        assert result.content_type == "application/pdf"
                        assert result.data == remote_content
                        assert result.size == len(remote_content)
                        assert result.is_temp is True

    @pytest.mark.unit
    def test_process_remote_attachment_download_error(self, attachment_service, remote_attachment):
        """测试远程附件下载错误"""
        with patch('email_mcp_server.attachment_service.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")

            with pytest.raises(NetworkError):
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

        # 应该使用 URL 的哈希值作为文件名
        assert len(filename) == 32  # MD5 哈希长度

    @pytest.mark.unit
    def test_cleanup_temp_files(self, attachment_service, tmp_path):
        """测试清理临时文件"""
        # 创建临时文件
        temp_file1 = tmp_path / "temp1.txt"
        temp_file2 = tmp_path / "temp2.txt"
        temp_file1.write_text("temp1")
        temp_file2.write_text("temp2")

        attachment_service.temp_files = [str(temp_file1), str(temp_file2)]

        with patch('email_mcp_server.attachment_service.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.unlink.return_value = None

            attachment_service.cleanup_temp_files()

            assert attachment_service.temp_files == []
            mock_path.return_value.unlink.assert_called()

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

        # 验证哈希值长度（MD5）
        assert len(file_hash) == 32
        assert file_hash is not None

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
    def test_validate_attachment_local_not_exists(self, attachment_service, local_attachment):
        """测试验证本地不存在的附件"""
        with patch('email_mcp_server.attachment_service.Path') as mock_path:
            mock_path.return_value.exists.return_value = False

            with pytest.raises(AttachmentFileNotFoundError):
                attachment_service.validate_attachment(local_attachment)

    @pytest.mark.unit
    def test_validate_attachment_remote_valid(self, attachment_service, remote_attachment):
        """测试验证远程有效附件"""
        from urllib.parse import urlparse

        with patch('email_mcp_server.attachment_service.urlparse') as mock_urlparse:
            mock_urlparse.return_value = urlparse(remote_attachment.path)
            mock_urlparse.return_value.scheme = "https"
            mock_urlparse.return_value.netloc = "example.com"

            # 应该不抛出异常
            attachment_service.validate_attachment(remote_attachment)

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

        with patch.object(attachment_service, 'cleanup_temp_files') as mock_cleanup:
            del attachment_service
            mock_cleanup.assert_called_once()

    @pytest.mark.unit
    def test_download_remote_file_retry_success(self, attachment_service):
        """测试远程文件下载重试成功"""
        url = "https://example.com/file.txt"

        with patch('email_mcp_server.attachment_service.requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-length": "13"}
            mock_response.iter_content.return_value = [b"Remote content"]
            mock_session.get.return_value = mock_response

            with patch('email_mcp_server.attachment_service.tempfile.NamedTemporaryFile') as mock_temp:
                mock_temp_file = Mock()
                mock_temp_file.name = "/tmp/temp_download"
                mock_temp.__enter__.return_value = mock_temp_file

                result = attachment_service._download_remote_file(url)

                assert result == "/tmp/temp_download"
                mock_session.get.assert_called_once()

    @pytest.mark.unit
    def test_download_remote_file_retry_exhausted(self, attachment_service):
        """测试远程文件下载重试耗尽"""
        url = "https://example.com/file.txt"

        with patch('email_mcp_server.attachment_service.requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session

            mock_response = Mock()
            mock_response.status_code = 500
            mock_session.get.return_value = mock_response

            with pytest.raises(DownloadError):
                attachment_service._download_remote_file(url)

            # 验证重试次数
            assert mock_session.get.call_count == 4  # 初始请求 + 3次重试
