"""Attachment handling service."""

import contextlib
import hashlib
import mimetypes
import os
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
import requests.adapters

from .config import get_app_settings
from .exceptions import (
    AttachmentError,
    AttachmentFileNotFoundError,
    DownloadError,
    EmailTimeoutError,
    FileSizeError,
    NetworkError,
)
from .logging_config import get_logger
from .models import Attachment, AttachmentType

logger = get_logger(__name__)


class AttachmentService:
    """附件处理服务."""

    def __init__(self) -> None:
        """初始化附件服务."""
        self.settings = get_app_settings()
        self.temp_files: list[str] = []

    def process_attachment(self, attachment: Attachment) -> dict:
        """
        处理附件，返回文件信息和文件对象。

        Args:
            attachment: 附件对象

        Returns:
            包含文件信息和文件对象的字典
        """
        try:
            if attachment.type == AttachmentType.LOCAL:
                return self._process_local_attachment(attachment)
            elif attachment.type == AttachmentType.REMOTE:
                return self._process_remote_attachment(attachment)
            else:
                raise AttachmentError(f"Unsupported attachment type: {attachment.type}")

        except Exception as e:
            logger.error(f"Failed to process attachment {attachment.path}: {e}")
            raise AttachmentError(f"Failed to process attachment: {e}") from e

    def _process_local_attachment(self, attachment: Attachment) -> dict:
        """处理本地附件."""
        file_path = Path(attachment.path)

        # 检查文件是否存在
        if not file_path.exists():
            raise AttachmentFileNotFoundError(str(file_path))

        # 检查文件大小
        file_size = file_path.stat().st_size
        if file_size > self.settings.max_attachment_size:
            raise FileSizeError(
                str(file_path), file_size, self.settings.max_attachment_size
            )

        # 确定文件名和MIME类型
        filename = attachment.filename or file_path.name
        content_type = (
            attachment.content_type
            or mimetypes.guess_type(str(file_path))[0]
            or "application/octet-stream"
        )

        # 读取文件
        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
        except Exception as e:
            raise AttachmentError(f"Failed to read local file {file_path}: {e}") from e

        return {
            "filename": filename,
            "content_type": content_type,
            "data": file_data,
            "size": file_size,
            "is_temp": False,
        }

    def _process_remote_attachment(self, attachment: Attachment) -> dict:
        """处理远程附件."""
        url = attachment.path

        # 下载文件
        temp_file_path = self._download_remote_file(url)

        try:
            # 获取文件信息
            file_size = os.path.getsize(temp_file_path)
            if file_size > self.settings.max_attachment_size:
                os.unlink(temp_file_path)
                raise FileSizeError(
                    url, file_size, self.settings.max_attachment_size
                )

            # 确定文件名和MIME类型
            filename = attachment.filename or self._extract_filename_from_url(url)
            content_type = (
                attachment.content_type
                or mimetypes.guess_type(temp_file_path)[0]
                or mimetypes.guess_type(url)[0]
                or "application/octet-stream"
            )

            # 读取文件
            with open(temp_file_path, "rb") as f:
                file_data = f.read()

            # 清理临时文件
            os.unlink(temp_file_path)

            return {
                "filename": filename,
                "content_type": content_type,
                "data": file_data,
                "size": file_size,
                "is_temp": True,
            }

        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                with contextlib.suppress(OSError):
                    os.unlink(temp_file_path)
            raise e

    def _download_remote_file(self, url: str) -> str:
        """下载远程文件."""
        session = requests.Session()

        # 设置重试策略
        retry_strategy = requests.adapters.Retry(
            total=self.settings.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            logger.info(f"Downloading file from {url}")
            start_time = time.time()

            # 发送请求
            response = session.get(
                url,
                stream=True,
                timeout=self.settings.download_timeout,
                headers={"User-Agent": "Email-MCP-Server/1.0"},
            )

            # 检查响应状态
            response.raise_for_status()

            # 获取文件大小
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.settings.max_attachment_size:
                raise FileSizeError(
                    url, int(content_length), self.settings.max_attachment_size
                )

            # 下载文件
            downloaded_size = 0
            with open(temp_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded_size += len(chunk)
                        if downloaded_size > self.settings.max_attachment_size:
                            raise FileSizeError(
                                url, downloaded_size, self.settings.max_attachment_size
                            )
                        f.write(chunk)

            download_time = time.time() - start_time
            logger.info(
                f"Successfully downloaded {downloaded_size} bytes from {url} in {download_time:.2f}s"
            )

            return temp_file_path

        except requests.exceptions.Timeout:
            raise EmailTimeoutError("download", self.settings.download_timeout) from None
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Network error while downloading {url}: {e}") from e
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise DownloadError(url, "File not found (404)") from None
            elif e.response.status_code == 403:
                raise DownloadError(url, "Access forbidden (403)") from None
            else:
                raise DownloadError(url, f"HTTP error {e.response.status_code}") from e
        except Exception as e:
            raise DownloadError(url, str(e)) from e
        finally:
            session.close()

    def _extract_filename_from_url(self, url: str) -> str:
        """从URL中提取文件名."""
        try:
            parsed_url = urlparse(url)
            path = parsed_url.path
            filename = os.path.basename(path)

            if not filename or filename == "/":
                # 生成默认文件名
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                filename = f"download_{url_hash}"

            return filename

        except Exception:
            # 如果解析失败，生成默认文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            return f"download_{url_hash}"

    def cleanup_temp_files(self) -> None:
        """清理临时文件."""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                with contextlib.suppress(OSError):
                    os.unlink(temp_file)
                    logger.debug(f"Cleaned up temporary file: {temp_file}")
            else:
                logger.warning(f"Temporary file not found for cleanup: {temp_file}")

        self.temp_files.clear()

    def get_file_hash(self, file_data: bytes) -> str:
        """计算文件的哈希值."""
        return hashlib.sha256(file_data).hexdigest()

    def validate_attachment(self, attachment: Attachment) -> None:
        """验证附件配置."""
        if attachment.type == AttachmentType.LOCAL:
            # 验证本地文件路径
            file_path = Path(attachment.path)
            if not file_path.is_absolute():
                raise AttachmentError("Local file path must be absolute")

        elif attachment.type == AttachmentType.REMOTE:
            # 验证URL格式
            try:
                parsed = urlparse(attachment.path)
                if not parsed.scheme or not parsed.netloc:
                    raise AttachmentError("Invalid URL format") from None
                if parsed.scheme not in ["http", "https"]:
                    raise AttachmentError("Only HTTP and HTTPS URLs are supported") from None
            except Exception as e:
                raise AttachmentError(f"Invalid remote URL: {e}") from e

    def __del__(self) -> None:
        """析构函数，清理临时文件."""
        with contextlib.suppress(Exception):
            self.cleanup_temp_files()
