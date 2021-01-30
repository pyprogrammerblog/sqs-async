import abc

from typing import Union, List, Optional, TYPE_CHECKING
from sqs_async.queues import GenericQueue
from sqs_async.backoff_policies import DEFAULT_BACKOFF
from sqs_async.utils.imports import get_async_tasks

import boto3

AnyQueue = Union[GenericQueue]

if TYPE_CHECKING:
    from sqs_workers.backoff_policies import BackoffPolicy


class AbstractSQSEnv(abc.ABC):

    def get_queue(self, name: str):
        raise NotImplementedError

    def create_queue(self):
        raise NotImplementedError

    def delete_queue(self):
        raise NotImplementedError


class SQSEnv(AbstractSQSEnv):

    def __init__(self, task_modules: List[str], queue_prefix: str = ""):

        self.registered_tasks = get_async_tasks(task_modules)

        self.queue_prefix = queue_prefix
        self.queues = {}
        self.backoff_policy = DEFAULT_BACKOFF

        # aws related
        self.session = boto3
        self.sqs_client = self.session.client("sqs")
        self.sqs_resource = self.session.resource("sqs")

    def get_queue(self, name: str):
        raise NotImplementedError

    def create_queue(self):
        raise NotImplementedError

    def get_or_create(self):
        raise NotImplementedError

    def delete_queue(self):
        raise NotImplementedError

    def process_queues(self):
        pass

    def queue(
        self,
        queue_name: str,
        queue_maker: AnyQueue = GenericQueue,
        backoff_policy: Optional[BackoffPolicy] = None,
    ) -> GenericQueue:

        """
        Get a queue object, initializing it with queue_maker if necessary.
        """
        if queue_name not in self.queues:
            backoff_policy = backoff_policy or self.backoff_policy
            self.queues[queue_name] = queue_maker(
                env=self,
                name=queue_name,
                backoff_policy=backoff_policy
            )
        return self.queues[queue_name]
