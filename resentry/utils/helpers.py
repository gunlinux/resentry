"""General helper functions for resentry."""

import json
from datetime import datetime
from typing import Any

import gzip
import brotli


def json_loads(data: str) -> Any:
    """Synchronous JSON parsing function."""
    return json.loads(data)


def parse_json(
    data: bytes | str,
) -> Any:  # Using Any since JSON parsing results can be different types
    """
    Safely parse JSON from bytes, handling UTF-8 encoding synchronously.
    """
    if isinstance(data, bytes):
        data_str = decode_utf8(data)
        return json_loads(data_str)
    else:
        return json_loads(data)


def gzip_decompress(data: bytes) -> bytes:
    """Synchronous gzip decompression function."""

    return gzip.decompress(data)


def brotli_decompress(data: bytes) -> bytes:
    """Synchronous brotli decompression function."""

    return brotli.decompress(data)


def decode_utf8(data: bytes) -> str:
    """Synchronous UTF-8 decoding function."""
    return data.decode("utf-8", "replace")


def format_timestamp(dt: datetime | None = None) -> str:
    """
    Format a datetime object as an ISO string.

    Args:
        dt: Optional datetime object to format. If None, uses current time.

    Returns:
        ISO formatted timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()


def validate_project_language(lang: str) -> bool:
    """
    Validate if the provided language is supported.

    Args:
        lang: Programming language string to validate

    Returns:
        True if language is supported, False otherwise
    """
    supported_languages = {
        "python",
        "javascript",
        "typescript",
        "java",
        "go",
        "rust",
        "csharp",
        "php",
        "ruby",
        "swift",
        "kotlin",
    }
    return lang.lower() in supported_languages


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length, adding ellipsis if truncated.

    Args:
        text: Text to truncate
        max_length: Maximum allowed length

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary.

    Args:
        dictionary: Dictionary to get value from
        key: Key to look for
        default: Default value if key not found

    Returns:
        Value from dictionary or default
    """
    try:
        return dictionary.get(key, default)
    except AttributeError:
        return default
