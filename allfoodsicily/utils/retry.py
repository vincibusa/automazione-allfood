"""Retry logic for API calls."""

from functools import wraps
from typing import Callable, TypeVar, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_api_call(
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 10.0
):
    """Decorator for retrying API calls with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds
        max_wait: Maximum wait time in seconds
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=initial_wait, max=max_wait),
            retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
            reraise=True
        )
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    f"Retrying {func.__name__} after error: {str(e)}"
                )
                raise
        
        return wrapper
    return decorator

