import asyncio
from functools import wraps
from warnings import warn

background_tasks = set()


def task(func):
    """Wrapper to make coroutines "runnable".

    Creates a task if event loop is running, otherwise runs it synchronously.
    """

    @wraps(func)
    def wrapped(*args, **kwargs):
        coro = func(*args, **kwargs)

        try:
            _task = asyncio.create_task(coro)
        except RuntimeError as ex:
            if "event loop" in str(ex):
                return asyncio.run(coro)
            raise

        background_tasks.add(_task)
        _task.add_done_callback(background_tasks.discard)

        return _task

    return wrapped


def runner_task(func):
    @wraps(func)
    async def wrapped(self, *args, **kwargs):
        if not self._active:
            raise RuntimeError('Must be called inside a "with" block.')

        return await func(self, *args, **kwargs)

    return task(wrapped)


class AsyncRunner:
    def __init__(self):
        self._active = False

    def __enter__(self):
        self._active = True

        return self

    def __exit__(self, a, b, c):
        self._active = False

    def run(self, app):
        warn(
            "Function .run() is deprecated and will be removed in a future version. Please check the getting started guide for the recommended way to start coroutines.",
            DeprecationWarning,
            stacklevel=2,
        )
        if self._active:
            return asyncio.run(app(self))
        else:
            raise RuntimeError('App must be run inside a "with" block.')
