from asyncio import get_running_loop
from functools import wraps
from time import sleep
from typing import Callable, Coroutine, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


def poll(interval: int | float = 0.001):
    loop = get_running_loop()

    def decorator(func: Callable[P, Coroutine[None, None, T]]) -> Callable[P, T]:

        @wraps(func)
        def wrapper(*args, **kwargs):
            future = loop.create_task(func(*args, **kwargs))
            while True:
                if future.done():
                    return future.result()
                sleep(interval)

        return wrapper  # type: ignore

    return decorator
