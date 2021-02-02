import abc
import logging
import boto3
import warnings

from typing import List, TYPE_CHECKING
from sqs_async.queues import GenericQueue
from sqs_async.backoff_policies import DEFAULT_BACKOFF
from sqs_async.utils.imports import get_async_tasks
from botocore.exceptions import ClientError


if TYPE_CHECKING:
    from sqs_workers.backoff_policies import BackoffPolicy

logger = logging.getLogger(__name__)


class AbstractSQSEnv(abc.ABC):
    queue_prefix = ""
    sqs_client = None
    sqs_resource = None

    def get_queue(self, name: str):
        raise NotImplementedError

    def create_queue(self):
        raise NotImplementedError

    def delete_queue(self, queue_name: str, raise_error: bool = True):
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

    def queue(
        self,
        queue_name: str,
        backoff_policy=None,  # type: BackoffPolicy
    ) -> GenericQueue:

        """
        Get a queue object, initializing it with queue_maker if necessary.
        """
        if queue_name not in self.queues:
            backoff_policy = backoff_policy or self.backoff_policy
            self.queues[queue_name] = GenericQueue(
                env=self,
                name=queue_name,
                backoff_policy=backoff_policy
            )
        return self.queues[queue_name]

    def delete_queue(self, queue_name, fail_quiet=True):
        try:
            self.sqs_client.delete_queue(QueueName=queue_name)
        except ClientError as e:
            warnings.warn("Unknown error. %s", e.response['Error']['Message'])

    def process_queues(self):
        pass
