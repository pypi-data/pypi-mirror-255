# pylint: disable=missing-function-docstring, missing-class-docstring
import time
from contextlib import ContextDecorator
from functools import wraps
from inspect import getfullargspec
from logging import Logger
from typing import Callable


class Timer(ContextDecorator):
    _start: float
    _stop: float
    _interval: float

    def __init__(self, logger: Logger, stack: str):
        super().__init__()
        self._logger = logger
        self._stack = stack

    @property
    def interval(self) -> float:
        return self._interval

    def __enter__(self) -> "Timer":
        self._start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        del exc_type, exc_value, exc_traceback
        self._stop = time.time()
        self._interval = self._stop - self._start

        self._logger.debug("Time [%s]: %s s", self._stack, round(self._interval, 3))


def timer(logger: Logger) -> Callable:
    def _timeit(func) -> Callable:
        @wraps(func)
        def _wrapper(*args, **kwargs):
            with Timer(logger=logger, stack=_get_stack(func, *args)):
                return func(*args, **kwargs)

        return _wrapper

    return _timeit


def _get_stack(func: Callable, *args) -> str:
    try:
        argspec = getfullargspec(func)[0]

        if argspec[0] == "self":
            return f"{args[0].__class__.__name__}.{func.__name__}"

        return f"{func.__module__}.{func.__qualname__}"

    except (TypeError, IndexError):
        return f"{func.__module__}.{func.__qualname__}"
