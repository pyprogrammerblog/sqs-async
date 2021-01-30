import asyncio

from typing import Callable
import functools
from datetime import timedelta

from sqs_async.queues import AbstractQueue
from sqs_async.settings import DEFAULT_QUEUE_NAME


def register(
        queue: AbstractQueue = None,
        delayed: timedelta = None
):
    """
    Regirter functions as SQS async functions

    Examples:

    >>> import sqs_async import tasks
    >>> import sqs_async.sqs_env import SQSAsyncEnv
    >>>
    >>> @tasks.register()
    ... def message(name):              # a message is any task decorate
    ...     print(f"Hello {name}")
    >>>
    >>> message.delay(args=("World",))  # this is converted into an awaitable like below
    >>>
    >>> import asyncio
    >>>
    >>> @tasks.register
    ... async def message(name):
    ...     await asyncio.sleep(1)
    >>>
    >>> message.delay(queue=queue, args=("World",))
    >>> message.delay(args=("World",))  # this goes to default queue
    >>>
    >>> from sqs_async.sqs_env import SQSEnv
    >>> queue = SQSAsyncEnv().queue("messages")
    >>> queue.process_queue()   # this run async event loop, all is manage as coroutines
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper_register():
            return AsyncTask(
                task_name=func.__name__,
                location=f"{func.__module__}.{func.__name__}",
                processor=func,
                queue=queue,
                delayed=delayed
            )
        return wrapper_register()
    return decorator


class AsyncTask:

    def __init__(
            self,
            task_name: str,
            location: str,
            processor: Callable,
            queue: AbstractQueue = None,
            delayed: timedelta = None,
    ) -> None:
        self.task_name = task_name
        self.location = location
        self.processor = processor
        self.queue = queue
        self.delayed = delayed
        self.__doc__ = processor.__doc__

    def __call__(self, *args, **kwargs):
        self.run(*args, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__} at {self.location}>"

    def run(self, *args, **kwargs):
        """
        Run the task synchronously.
        """
        if asyncio.iscoroutinefunction(self.processor):
            return asyncio.run(self.processor(*args, **kwargs))
        else:
            return self.processor(*args, **kwargs)

    def delay(self, queue: AbstractQueue = None, args: tuple = None, kwargs: dict = None):
        """
        Run the task asynchronously.
        """
        assert self.queue or queue, "Queue is not defined."
        queue = self.queue or queue

        if not kwargs:
            kwargs = {}

        _content_type = kwargs.pop("_content_type", None)
        _delay_seconds = kwargs.pop("_delay_seconds", self.delayed)
        _deduplication_id = kwargs.pop("_deduplication_id", None)
        _group_id = kwargs.pop("_group_id", None)

        return queue.add_job()

    def bake(self, *args, **kwargs):
        """
        Create a baked version of the async task, which contains the reference
        to a queue and task, as well as all arguments which needs to be passed
        to it.
        """
        return BakedAsyncTask(self, args, kwargs)


class BakedAsyncTask(object):
    def __init__(self, async_task, args, kwargs):
        self.async_task = async_task
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        self.async_task(*self.args, **self.kwargs)

    def delay(self):
        self.async_task.delay(*self.args, **self.kwargs)

    def __repr__(self):
        return f"BakedAsyncTask({self.async_task}, ...)"
