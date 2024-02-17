import logging
import tiktoken
from typing import Any, Callable, List, Optional, Type
from tenacity import RetryCallState, before_sleep_log, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .callbacks import CallbackManager
from ..utils import logger


def create_base_retry_decorator(
    error_types: List[Type[BaseException]],
    max_retries: int = 1,
    run_manager: Optional[CallbackManager] = None,
) -> Callable[[Any], Any]:
    """Create a retry decorator for a given LLM and provided list of error types."""

    _logging = before_sleep_log(logger, logging.WARNING)

    def _before_sleep(retry_state: RetryCallState) -> None:
        _logging(retry_state)
        if run_manager:
            run_manager.on_retry(retry_state, [])
        return None

    min_seconds = 4
    max_seconds = 10
    retry_instance = retry_if_exception_type(error_types[0]) if len(
        error_types) > 0 else retry_if_exception_type()
    for error in error_types[1:]:
        retry_instance = retry_instance | retry_if_exception_type(error)
    return retry(
        reraise=True,
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=1, min=min_seconds, max=max_seconds),
        retry=retry_instance,
        before_sleep=_before_sleep,
    )


def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
