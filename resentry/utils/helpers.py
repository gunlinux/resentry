"""General helper functions for resentry."""

from datetime import datetime
from typing import Any, Optional


def format_timestamp(dt: Optional[datetime] = None) -> str:
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
        "python", "javascript", "typescript", "java", "go", 
        "rust", "csharp", "php", "ruby", "swift", "kotlin"
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
    return text[:max_length-3] + "..."


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