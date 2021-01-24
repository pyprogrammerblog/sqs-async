
import abc
import boto3

from async_sqs.backoff_policies import DEFAULT_BACKOFF
from async_sqs.backoff_policies import BackoffPolicy


class AbstractQueue(abc.ABC):
    name: str
    queue: abc.ABC

    def add_job(self):
        raise NotImplementedError

    def process_queue(self):
        raise NotImplementedError

    def process_batch(self):
        raise NotImplementedError

    def process_message(self):
        raise NotImplementedError

    def get_raw_messages(self):
        raise NotImplementedError


class Queue(AbstractQueue):

    def __init__(
            self,
            name: str,
            queue = None,
            backoff_policy: BackoffPolicy = DEFAULT_BACKOFF
    ) -> None:
        self.queue_name = name
        self.queue = queue
        self.backoff_policy = backoff_policy

        # if queue was not provided, get or create queue by name
        if not self.queue:
            sqs = boto3.resource('sqs')
            try:
                self.queue = sqs.get_queue_by_name(QueueName=self.queue_name)
            except Exception:
                self.queue = sqs.create_queue(QueueName=self.queue_name)

    def add_job(self):
        """
        Add job to the queue.
        """
        return self.queue.send_message()
