"""
Adds thread-local context to a Python logger. Taken from neocrym/log-with-context
"""
import collections.abc
import contextlib
import contextvars
import logging
from typing import Any, Dict, Mapping, Optional
from weakref import WeakKeyDictionary

_LOGGING_CONTEXT: contextvars.ContextVar[Mapping[str, Any]] = contextvars.ContextVar("_LOGGING_CONTEXT")


def _recursive_merge(a: Mapping[str, Any], b: Mapping[str, Any]):
    ans: Dict[str, Any] = {**a}
    for k, v in b.items():
        if k not in ans or not (isinstance(ans[k], collections.abc.Mapping) and isinstance(v, collections.abc.Mapping)):
            ans[k] = v
            continue
        ans[k] = _recursive_merge(ans[k], v)
    return ans


def get_logging_context() -> Mapping[str, Any]:
    """
    Retrieve the log context for the current python context.
    This initializes the thread-local variable if necessary.
    """
    return _LOGGING_CONTEXT.get({})


class LogWithContextFilter(logging.Filter):
    """Filter to append the ``extras`` onto the LogRecord."""

    def filter(self, record: logging.LogRecord) -> bool:
        items = get_logging_context().items()
        for k, v in items:
            if not hasattr(record, k):
                setattr(record, k, v)
        return True


filtered_loggers = WeakKeyDictionary()


def get_logger(name: Optional[str]):
    logger = logging.getLogger(name)
    if logger not in filtered_loggers:
        logger.addFilter(LogWithContextFilter())
        filtered_loggers[logger] = True
    return logger


# Backwards compatibility
Logger = get_logger


@contextlib.contextmanager
def add_logging_context(*, _merge: bool = True, **log_context: Any):
    """A context manager to push and pop `extra` dictionary keys.

    Parameters
    ----------
    _merge
        Whether to merge the new context with the existing log context.
    extra
        Contextual information to add to the log record
    """
    if _merge:
        log_context = _recursive_merge(
            _LOGGING_CONTEXT.get({}),
            log_context,
        )
    token = _LOGGING_CONTEXT.set(log_context)
    try:
        yield
    finally:
        _LOGGING_CONTEXT.reset(token)
