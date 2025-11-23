"""Custom exceptions for the Email MCP Server."""



class EmailMCPServerError(Exception):
    """Base exception for all Email MCP Server errors."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ConfigurationError(EmailMCPServerError):
    """Configuration related errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "CONFIG_ERROR")


class ValidationError(EmailMCPServerError):
    """Data validation errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "VALIDATION_ERROR")


class EmailServiceError(EmailMCPServerError):
    """Email service related errors."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message, error_code or "EMAIL_SERVICE_ERROR")


class SMTPConnectionError(EmailServiceError):
    """SMTP connection errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "SMTP_CONNECTION_ERROR")


class AuthenticationError(EmailServiceError):
    """Authentication errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "AUTHENTICATION_ERROR")


class AttachmentError(EmailMCPServerError):
    """Attachment related errors."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message, error_code or "ATTACHMENT_ERROR")


class AttachmentFileNotFoundError(AttachmentError):
    """File not found errors."""

    def __init__(self, file_path: str) -> None:
        super().__init__(f"File not found: {file_path}", "FILE_NOT_FOUND")


class FileSizeError(AttachmentError):
    """File size too large errors."""

    def __init__(self, file_path: str, size: int, max_size: int) -> None:
        super().__init__(
            f"File too large: {file_path} ({size} bytes > {max_size} bytes)",
            "FILE_SIZE_ERROR",
        )


class DownloadError(AttachmentError):
    """File download errors."""

    def __init__(self, url: str, reason: str) -> None:
        super().__init__(
            f"Failed to download file from {url}: {reason}", "DOWNLOAD_ERROR"
        )


class NetworkError(EmailMCPServerError):
    """Network related errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "NETWORK_ERROR")


class EmailTimeoutError(NetworkError):
    """Timeout errors."""

    def __init__(self, operation: str, timeout: int) -> None:
        super().__init__(
            f"Operation {operation} timed out after {timeout} seconds", "TIMEOUT_ERROR"
        )


# 错误代码映射
ERROR_CODES = {
    # 配置错误
    "CONFIG_ERROR": {
        "code": "E001",
        "message": "Configuration error",
        "description": "Invalid or missing configuration",
    },
    "VALIDATION_ERROR": {
        "code": "E002",
        "message": "Validation error",
        "description": "Input data validation failed",
    },
    # 邮件服务错误
    "EMAIL_SERVICE_ERROR": {
        "code": "E101",
        "message": "Email service error",
        "description": "General email service error",
    },
    "SMTP_CONNECTION_ERROR": {
        "code": "E102",
        "message": "SMTP connection error",
        "description": "Failed to connect to SMTP server",
    },
    "AUTHENTICATION_ERROR": {
        "code": "E103",
        "message": "Authentication error",
        "description": "Email authentication failed",
    },
    # 附件错误
    "ATTACHMENT_ERROR": {
        "code": "E201",
        "message": "Attachment error",
        "description": "Attachment processing error",
    },
    "FILE_NOT_FOUND": {
        "code": "E202",
        "message": "File not found",
        "description": "Specified file does not exist",
    },
    "FILE_SIZE_ERROR": {
        "code": "E203",
        "message": "File size error",
        "description": "File exceeds maximum size limit",
    },
    "DOWNLOAD_ERROR": {
        "code": "E204",
        "message": "Download error",
        "description": "Failed to download remote file",
    },
    # 网络错误
    "NETWORK_ERROR": {
        "code": "E301",
        "message": "Network error",
        "description": "Network connectivity error",
    },
    "TIMEOUT_ERROR": {
        "code": "E302",
        "message": "Timeout error",
        "description": "Operation timed out",
    },
}


def get_error_info(error_code: str) -> dict:
    """获取错误代码信息."""
    return ERROR_CODES.get(
        error_code,
        {
            "code": "E999",
            "message": "Unknown error",
            "description": "Unknown error occurred",
        },
    )


def format_error_response(exception: EmailMCPServerError) -> dict:
    """格式化错误响应."""
    error_info = (
        get_error_info(exception.error_code)
        if exception.error_code
        else ERROR_CODES["EMAIL_SERVICE_ERROR"]
    )

    return {
        "success": False,
        "error": {
            "code": error_info["code"],
            "type": exception.error_code or "EMAIL_SERVICE_ERROR",
            "message": error_info["message"],
            "description": error_info["description"],
            "detail": exception.message,
        },
    }
