"""General helper functions for resentry."""

import asyncio
import json
from datetime import datetime
from typing import Any
from concurrent.futures import ThreadPoolExecutor


def sync_json_loads(data: str) -> Any:
    """Synchronous JSON parsing function to run in thread pool."""
    return json.loads(data)


def sync_json_dumps(data: Any) -> str:
    """Synchronous JSON serialization function to run in thread pool."""
    return json.dumps(data)


def sync_gzip_decompress(data: bytes) -> bytes:
    """Synchronous gzip decompression function to run in thread pool."""
    import gzip

    return gzip.decompress(data)


def sync_brotli_decompress(data: bytes) -> bytes:
    """Synchronous brotli decompression function to run in thread pool."""
    import brotli  # type: ignore

    return brotli.decompress(data)


def sync_decode_utf8(data: bytes) -> str:
    """Synchronous UTF-8 decoding function to run in thread pool."""
    return data.decode("utf-8", "replace")


async def async_json_loads(data: str) -> Any:
    """Asynchronously parse JSON using thread pool executor."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, sync_json_loads, data)
    return result


async def async_json_dumps(data: Any) -> str:
    """Asynchronously serialize JSON using thread pool executor."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, sync_json_dumps, data)
    return result


async def async_gzip_decompress(data: bytes) -> bytes:
    """Asynchronously decompress gzip data using thread pool executor."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, sync_gzip_decompress, data)
    return result


async def async_brotli_decompress(data: bytes) -> bytes:
    """Asynchronously decompress brotli data using thread pool executor."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, sync_brotli_decompress, data)
    return result


async def async_decode_utf8(data: bytes) -> str:
    """Asynchronously decode UTF-8 data using thread pool executor."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, sync_decode_utf8, data)
    return result


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
