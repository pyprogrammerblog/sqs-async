import abc
import boto3

from typing import TYPE_CHECKING
from sqs_async.backoff_policies import DEFAULT_BACKOFF
from sqs_async.backoff_policies import BackoffPolicy


if TYPE_CHECKING:
    from sqs_workers import SQSEnv


class AbstractQueue(abc.ABC):
    name: str

    def add_job(self):
        raise NotImplementedError

    def process_queue(self, verbose, keep_alive, processes):
        raise NotImplementedError

    def process_batch(self, filter: dict):
        raise NotImplementedError

    def process_message(self):
        raise NotImplementedError

    def get_raw_messages(self):
        raise NotImplementedError


class GenericQueue(AbstractQueue):
    def __init__(
            self,
            env,  # type: SQSEnv
            name: str,
            backoff_policy: BackoffPolicy = DEFAULT_BACKOFF
    ) -> None:
        self.env = env,
        self.queue_name = name
        self.backoff_policy = backoff_policy

        # if queue was not provided, get or create queue by name
        sqs = env.sqs_resource
        try:
            self.queue = sqs.get_queue_by_name(QueueName=self.queue_name)
        except Exception:
            self.queue = sqs.create_queue(QueueName=self.queue_name)

    def add_job(self):
        """
        Add job to the queue.
        """
        return self.queue.send_message()
