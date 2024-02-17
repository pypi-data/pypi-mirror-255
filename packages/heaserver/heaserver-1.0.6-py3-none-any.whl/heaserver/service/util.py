import logging

from functools import wraps
from typing import Optional, Type, Any, TypeVar
from collections.abc import AsyncGenerator, Awaitable, Coroutine, Callable, Generator, Iterable
import requests
from contextlib import contextmanager
import asyncio
import time
import os
from dataclasses import dataclass
import inspect

RT = TypeVar('RT')  # return type

def async_retry(*exceptions: Type[Exception], retries: int = 3, cooldown: Optional[int] = 1,
                verbose: bool = True) -> Callable[[Coroutine[Any, Any, RT]], Coroutine[Any, Any, RT]]:
    """
    Decorate an async function to execute it a few times before giving up and raising a ``RetryExhaustedError``.

    :param exceptions: One or more exceptions expected during function execution, as positional arguments.
    :param retries: Number of retries of function execution.
    :param cooldown: Seconds to wait before retry. If None, does not cool down.
    :param verbose: Specifies if we should log about not successful attempts.
    """

    def wrap(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            _logger = logging.getLogger(__name__)
            retries_count = 0

            while True:
                try:
                    result = await func(*args, **kwargs)
                except exceptions as err:
                    retries_count += 1
                    message = "Exception {} during {} execution. " \
                              "{} of {} retries attempted".format(type(err), func, retries_count, retries)

                    if retries_count > retries:
                        verbose and _logger.exception(message)
                        raise RetryExhaustedError(func.__qualname__) from err
                    else:
                        verbose and _logger.warning(message)

                    if cooldown:
                        await asyncio.sleep(cooldown)
                else:
                    return result
        return inner
    return wrap


def retry(*exceptions: Type[Exception], retries: int = 3, cooldown: Optional[int] = 1,
          verbose: bool = True) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """
    Decorate a non-async function to execute it a few times before giving up and raising a ``RetryExhaustedError``.

    :param exceptions: One or more exceptions expected during function execution, as positional arguments.
    :param retries: Number of retries of function execution.
    :param cooldown: Seconds to wait before retry. If None, does not cool down.
    :param verbose: Specifies if we should log about not successful attempts.
    :return a callable that accepts a callable, wraps it with the retry behavior, and returns a callable with the same
    signature.
    """

    def wrap(func):
        @wraps(func)
        def inner(*args, **kwargs):
            _logger = logging.getLogger(__name__)
            retries_count = 0

            while True:
                try:
                    result = func(*args, **kwargs)
                except exceptions as err:
                    retries_count += 1
                    message = "Exception {} during {} execution. " \
                              "{} of {} retries attempted".format(type(err), func, retries_count, retries)

                    if retries_count > retries:
                        verbose and _logger.exception(message)
                        raise RetryExhaustedError(f'Exhausted retries of {func}') from err
                    else:
                        verbose and _logger.warning(message)

                    if cooldown:
                        time.sleep(cooldown)
                else:
                    return result
        return inner
    return wrap


class RetryExhaustedError(Exception):
    """
    Indicates that the retries have been exhausted and the decorated function has failed.
    """
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


@contextmanager
def modified_environ(*remove, **update):
    """
    Temporarily updates the ``os.environ`` dictionary in-place.

    The ``os.environ`` dictionary is updated in-place so that the modification
    is sure to work in all situations. Code obtained from
    https://stackoverflow.com/questions/2059482/python-temporarily-modify-the-current-processs-environment.

    :param remove: Environment variables to remove.
    :param update: Dictionary of environment variables and values to add/update.
    """
    env = os.environ
    update = update or {}
    remove = remove or []

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: env[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in env)

    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]


@contextmanager
def request_get_with_retry(url: str, retries=10, cooldown: int | None = 5, timeout: float | None = 60) -> Generator[requests.Response, None, None]:
    """
    Context manager that opens a URL, retrying if unsuccessful, and generates a HTTPResponse.

    :param url: the URL to open (required).
    :param retries: the number of retries.
    :param cooldown: the cooldown period (None for no cooldown).
    :param timeout: the connection timeout (None for no timeout).
    :raises TimeoutError: if the final retry timed out.
    :raises URLError: if the final retry errored out.
    """
    logger = logging.getLogger(__name__)
    logger.debug('Connecting to URL %s', url)

    if not retries:
        retries = 0

    @retry(requests.exceptions.RequestException, retries=retries, cooldown=cooldown)
    def do_open() -> requests.Response:
        try:
            with requests.get(url, timeout=timeout) as response:
                return response
        except Exception as e:
            logger.exception(f'Error getting URL {url}')
            raise e
    response = do_open()
    try:
        yield response
    finally:
        response.close()


class DuplicateError(ValueError):
    """
    The exception raised by the check_duplicates function.
    """
    def __init__(self, msg: str, duplicate_item: Any):
        """
        Creates the error.

        :param msg: the message to display when the exception is raised.
        :param duplicate_item: the item triggering the exception.
        """
        super().__init__(msg)
        self.__duplicate_item = duplicate_item

    @property
    def duplicate_item(self) -> Any:
        """The item triggering the exception."""
        return self.__duplicate_item


def check_duplicates(itr: Iterable[Any]):
    """
    Checks an iterable for duplicate items and raises an exception if one is found.

    @param itr: an iterable.
    @raise DuplicateError if a duplicate is found.
    """
    s = set()
    for item in itr:
        if item in s:
            raise DuplicateError(f'Duplicate {item}', item)
        else:
            s.add(item)


@dataclass(frozen=True)
class TypeEnforcingFrozenDataclass:
    def __post_init__(self):
        for (name, field_type) in self.__annotations__.items():
            if not isinstance(self.__dict__[name], field_type):
                current_type = type(self.__dict__[name])
                raise TypeError(f"The field `{name}` was assigned by `{current_type}` instead of `{field_type}`")

def issubclass_silent(cls, class_or_tuple, /):
    """
    Works like the builtin issubclass, except it returns False if cls is not a
    type instead of raising a TypeError.
    """
    return isinstance(cls, type) and cls is not None and issubclass(cls, class_or_tuple)

T = TypeVar('T')

def to_type(cls_or_instance: T | Type[T] | None, type_: Type[T]) -> Type[T] | None:
    if cls_or_instance is not None and not issubclass_silent(cls_or_instance, type_) and not isinstance(cls_or_instance, type_):
        raise TypeError(f'cls_or_instance not a subclass nor instance of {type_}; was {cls_or_instance}')

    if cls_or_instance is None:
        return None
    elif isinstance(cls_or_instance, type):
        return cls_or_instance
    else:
        return type(cls_or_instance)

async def queued_processing(generator: Callable[[], AsyncGenerator[T, None]],
                            item_processor: Callable[[T], Awaitable[None]],
                            exceptions_to_ignore: Callable[[Exception], bool] | None = None,
                            queue_max_size=100, num_workers=10):
    """
    Places items in an async generator into an asyncio queue for processing by the provided async item_processor.
    Specified exceptions may be suppressed.

    :param generator: the item async generator (required).
    :param item_processor: the async item processor.
    :param exceptions_to_ignore: a function that takes an exception parameter and returns whether the exception should
    be suppressed.
    :param queue_max_size the maximum size of the queue (default is 0, meaning infinite size).
    :param num_workers: the number of workers that take items off the queue (default is 10).
    """
    logger = logging.getLogger(__name__)
    queue = asyncio.Queue(queue_max_size)
    async def worker(name: str, queue: asyncio.Queue):
        try:
            logger.debug('Starting worker %s', name)
            while True:
                coro = await queue.get()
                logger.debug('Worker %s processing item %s', name, coro)
                try:
                    await item_processor(coro)
                    logger.debug('Worker %s processing item %s', name, coro)
                finally:
                    queue.task_done()
        except asyncio.CancelledError:
            logger.debug('Ending worker %s', name)
        except:
            logger.exception('Error in worker %s', name)
            raise
    workers = []
    for i in range(num_workers):
        workers.append(asyncio.create_task(worker(f'worker-{i}', queue)))
    try:
        async for coro in generator():
            await queue.put(coro)
        await queue.join()
    finally:
        for worker in workers:
            worker.cancel()
        exceptions_to_raise = []
        for r in await asyncio.gather(*workers, return_exceptions=True):
            if isinstance(r, Exception) and (not exceptions_to_ignore or not exceptions_to_ignore(r)):
                exceptions_to_raise.append(r)
        if exceptions_to_raise:
            raise exceptions_to_raise[0]


def public_methods(cls: Type) -> list[str]:
    """
    Returns a list of the provided class' public methods, defined as any callable attribute of the class that is not a
    class and whose name does not begin with an underscore.

    :param cls: the class (required).
    :return: a list of method names.
    """
    l: list[str] = []
    for method in dir(cls):
        attr = getattr(cls, method)
        if not method.startswith('_') and not inspect.isclass(attr):
            l.append(method)
    return l


async def yield_control():
    """
    Yields control from the current async task to another task.
    """
    await asyncio.sleep(0.1)
