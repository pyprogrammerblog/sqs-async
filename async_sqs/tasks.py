from typing import Callable
import functools
from datetime import timedelta
import settings

from async_sqs.queues import AbstractQueue, Queue
from async_sqs.settings import DEFAULT_QUEUE_NAME


def register(
        queue: AbstractQueue = None,
        name: str = None,
        delayed: timedelta = None
):
    """
    Regirter functions as SQS async functions

    Examples:

    >>> import async_sqs.tasks import register
    >>> @register
    ... def message(name):
    ...     print(f"Hello {name}")
    >>>
    >>> message.delay(args=("World",))
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper_register():
            return AsyncTask(
                job_name=name or func.__name__,
                processor=func,
                queue=queue,
                delayed=delayed
            )
        return wrapper_register()
    return decorator


class AsyncTask:

    def __init__(
            self,
            job_name: str,
            processor: Callable,
            queue: AbstractQueue = None,
            delayed: timedelta = None,
    ) -> None:
        self.job_name = job_name
        self.processor = processor
        self.queue = queue
        self.delayed = delayed
        self.__doc__ = processor.__doc__

    def __call__(self, *args, **kwargs):
        self.run(*args, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.job_name}>"

    def run(self, *args, **kwargs):
        """
        Run the task synchronously.
        """
        return self.processor(*args, **kwargs)

    def delay(self, queue: str = None, args: tuple = None, kwargs: dict = None):
        """
        Run the task asynchronously.
        """
        queue = self.queue or Queue(queue or DEFAULT_QUEUE_NAME)

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


if __name__ == "__main__":

    @register()
    def message(name):
        print(f"Hola {name}")

    message.delay(queue='queue-test', args=("Jose",))
    message("Jose")
