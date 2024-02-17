"""
General purpose utilities for the library.
They facilitate cross-domain usual tasks in a DRY manner through decorators 
and higher order functions.
"""

from __future__ import annotations

import asyncio
import functools
import logging
from time import perf_counter
from typing import Awaitable, Callable, Generator, Sequence, Type, TypeVar, Union

from rich.console import Console
from rich.logging import RichHandler
from rich.pretty import install
from rich.traceback import install as ins
from tenacity import retry as retry_
from tenacity import retry_if_exception_type, stop_after_attempt, wait_exponential
from typing_extensions import ParamSpec

from .exceptions import HTTPException

T = TypeVar("T")
R = TypeVar("R")
P = ParamSpec("P")


def setup_logging(name: str = __name__) -> logging.Logger:
    """
    Set up logging configuration and return a logger instance.

    Args:
        name (str): The name of the logger (default: __name__)

    Returns:
        logging.Logger: The configured logger instance.
    """
    install()
    ins()
    console = Console(record=True, force_terminal=True)
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        tracebacks_extra_lines=2,
        tracebacks_theme="monokai",
        show_level=False,
    )
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    console_handler.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO, handlers=[console_handler])
    logger_ = logging.getLogger(name)
    logger_.setLevel(logging.INFO)
    return logger_


logger = setup_logging()


def process_time(
    func: Callable[P, Union[Awaitable[T], T]]
) -> Callable[P, Awaitable[T]]:
    """
    Decorator that measures the execution time of a function.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function.

    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        start = perf_counter()
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        end = perf_counter()
        logger.info(
            "Time taken to execute %s: %s seconds", wrapper.__name__, end - start
        )
        return result  # type: ignore

    return wrapper


def handle_errors(
    func: Callable[P, Union[Awaitable[T], T]]
) -> Callable[P, Awaitable[T]]:
    """Decorator that handles errors raised by the decorated function.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The decorated function.

    Raises:
        HTTPException: If an exception is raised by the decorated function,
        it is caught and re-raised as an HTTPException with a status
        code of 500.
    """

    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            wrapper.__name__ = func.__name__
            logger.info("Calling %s", wrapper.__name__)
            if asyncio.iscoroutinefunction(func):
                response = await func(*args, **kwargs)
                logger.info(response)
                return response  # type: ignore
            response = func(*args, **kwargs)
            logger.info(response)
            return response  # type: ignore
        except Exception as exc:
            raise HTTPException(status_code=500, detail=repr(exc)) from exc

    return wrapper


def retry(
    retries: int = 3,
    wait: int = 1,
    max_wait: int = 3,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    Decorator that retries a function call a specified number of times,
    with a specified wait time between retries, and for specified exception types.

    Args:
        retries (int): The number of times to retry the function call.
        wait (int): The initial wait time between retries in seconds.
        max_wait (int): The maximum wait time between retries in seconds.
        exceptions (tuple[Type[Exception], ...]): The exception types to retry on.

    Returns:
        Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]: The decorated function.

    Example:
        @retry(retries=5, wait=2, max_wait=10, exceptions=(ValueError,))
        async def my_function():
            # code here
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        @retry_(
            stop=stop_after_attempt(retries),
            wait=wait_exponential(multiplier=wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
            reraise=True,
        )
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def robust(
    func: Callable[P, Awaitable[T]],
    *,
    max_retries: int = 3,
    wait: int = 1,
    max_wait: int = 3,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
) -> Callable[P, Awaitable[T]]:
    """
    Decorator that adds robustness to a function by retrying it in case of exceptions.

    Args:
        func (Callable[P, Awaitable[T]]): The function to be decorated.
        max_retries (int, optional): The maximum number of retries. Defaults to 3.
        wait (int, optional): The initial wait time between retries in seconds. Defaults to 1.
        max_wait (int, optional): The maximum wait time between retries in seconds. Defaults to 3.
        exceptions (tuple[Type[Exception], ...], optional): The exceptions to catch and retry on. Defaults to (Exception,).

    Returns:
        Callable[P, Awaitable[T]]: The decorated function.
    """
    return functools.reduce(
        lambda f, g: g(f),  # type: ignore
        [retry(max_retries, wait, max_wait, exceptions), process_time, handle_errors],
        func,
    )


def chunker(seq: Sequence[T], size: int) -> Generator[Sequence[T], None, None]:
    """
    Splits a sequence into smaller chunks of a specified size.

    Args:
        seq (Sequence[T]): The sequence to be chunked.
        size (int): The size of each chunk.

    Yields:
        Generator[Sequence[T], None, None]: A generator that yields each chunk of the sequence.

    Example:
        >>> list(chunker([1, 2, 3, 4, 5, 6, 7, 8, 9], 3))
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    """
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def async_io(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """
    Decorator that allows a synchronous I/O bound function to be executed asynchronously in a separate thread leaving the main thread non-blocked.

    CPU bound functions should not be decorated with this decorator, for that matter they should be derived to a cuda device within the context of a torch.no_grad() block.

    Args:
        func: The synchronous I/O bound function to be executed asynchronously.

    Returns:
        A wrapper function that executes the synchronous I/O function in a separate thread and returns an awaitable result.
    """

    @functools.wraps(func)
    @robust
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


def merge_dicts(*dicts: dict[str, T]) -> dict[str, T]:
    """
    Merges two or more dictionaries into a single dictionary.

    Args:
        *dicts (dict[str, T]): The dictionaries to be merged.

    Returns:
        dict[str, T]: The merged dictionary.

    Example:
        >>> merge_dicts({"a": 1, "b": 2}, {"b": 3, "c": 4})
        {"a": 1, "b": 3, "c": 4}
    """
    return {k: v for d in dicts for k, v in d.items()}


def _clean_dict(d: dict[str, T]) -> dict[str, T]:
    """
    Removes None values from a dictionary.

    Args:
        d (dict[str, T]): The dictionary to be cleaned.

    Returns:
        dict[str, T]: The cleaned dictionary.

    Example:
        >>> clean_dict({"a": 1, "b": None, "c": 3})
        {"a": 1, "c": 3}
    """
    nulls: list[str] = [k for k, v in d.items() if v is None]
    return {k: v for k, v in d.items() if k not in nulls}


def _clean_list(list_: list[T]) -> list[T]:
    """
    Removes None values from a list.

    Args:
        list_ (list[T]): The list to be cleaned.

    Returns:
        list[T]: The cleaned list.

    Example:
        >>> clean_list([1, None, 3])
        [1, 3]
    """
    return [v for v in list_ if v is not None]


def clean_object(obj: Union[dict[str, T], list[T]]) -> Union[dict[str, T], list[T]]:
    """
    Removes None values from a dictionary or a list.

    Args:
        obj (Union[dict[str, T], list[T]]): The object to be cleaned.

    Returns:
        Union[dict[str, T], list[T]]: The cleaned object.

    Example:
        >>> clean_object({"a": 1, "b": None, "c": 3})
        {"a": 1, "c": 3}
        >>> clean_object([1, None, 3])
        [1, 3]
    """
    if isinstance(obj, dict):
        return _clean_dict(obj)
    return _clean_list(obj)
