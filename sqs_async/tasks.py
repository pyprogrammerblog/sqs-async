import asyncio

from typing import Callable
import functools
from datetime import timedelta

from sqs_async.queues import AbstractQueue


def register(queue: AbstractQueue = None, delayed: timedelta = None):
    """
    Regirter functions as SQS async functions

    Examples:

    >>> from sqs_async import tasks
    >>> import asyncio
    >>>
    >>> @tasks.register
    ... def message(name):
    ...     print(f"Hello {name}")
    >>>
    >>> @tasks.register
    ... async def async_message(name):
    ...     await asyncio.sleep(1)
    ...     print(f"Hello {name}")
    >>>
    >>> message("World!")
    Hello World!
    >>> async_message("World!")
    Hello World!
    >>>
    >>> from sqs_async.sqs_env import SQSEnv
    >>> sqs_env = SQSEnv(task_modules=['message_module'])          # create sqs env
    >>> message_queue = sqs_env.queue("message_queue")             # get or create a queue
    >>>
    >>> message.delay(queue=message_queue, args=("World",))        # send task to the queue as a coroutine
    >>>
    >>> async_message.delay(queue=message_queue, args=("World",))  # send task to the queue as a coroutine
    >>>
    >>> from sqs_async.sqs_env import SQSEnv
    >>> sqs_env = SQSEnv(task_modules=['message_module'])
    >>> message_queue = sqs_env.queue("message_queue")
    >>>
    >>> queue.process_queue()                                       # finally you can process a queue in an event loop, or
    >>> sqs_env.process_queues(queue_names=["message_queue"])       # some of them, (multiprocessing, each an event loop)
    >>> sqs_env.process_queues(queue_names=["*"])                   # or all of them
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper_register():
            return AsyncTask(
                task_name=func.__name__,
                location=f"{func.__module__}.{func.__name__}",
                processor=func,
                queue=queue,
                delayed=delayed,
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

    def delay(
        self,
        delay_seconds=None,
        queue: AbstractQueue = None,
        content_type=None,
        deduplication_id=None,
        group_id=None,
        kwargs: dict = None,
    ):
        """
        Run the task asynchronously.
        """
        queue = self.queue or queue
        assert self.queue, "Queue is not defined."

        if not kwargs:
            kwargs = {}

        return queue.add_job(
            self.task_name,
            content_type=content_type,
            delay_seconds=delay_seconds,
            deduplication_id=deduplication_id,
            group_id=group_id,
            kwargs=kwargs,
        )

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
