import abc
import logging
import boto3
import warnings
import multiprocessing

from typing import List, Union, TYPE_CHECKING
from sqs_async.queues import GenericQueue
from sqs_async.backoff_policies import DEFAULT_BACKOFF
from sqs_async.utils.imports import get_registered_tasks
from botocore.exceptions import ClientError
from sqs_async.shutdown_policies import NeverShutdown
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(raise_error_if_not_found=True))


if TYPE_CHECKING:
    from sqs_async.backoff_policies import BackoffPolicy

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

        self.registered_tasks = get_registered_tasks(task_modules)

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
                env=self, name=queue_name, backoff_policy=backoff_policy
            )
        return self.queues[queue_name]

    def delete_queue(self, queue_name, fail_quiet=True):
        try:
            self.sqs_client.delete_queue(QueueName=queue_name)
        except ClientError as e:
            warnings.warn("Unknown error. %s", e.response["Error"]["Message"])

    def process_queues(self, queue_names=None, shutdown_policy_maker=NeverShutdown):
        """
        Use multiprocessing to process multiple queues at once. If queue names
        are not set, process all known queues

        shutdown_policy_maker is an optional callable which doesn't accept any
        arguments and create a new shutdown policy for each queue.

        Can looks somewhat like this:

            lambda: IdleShutdown(idle_seconds=10)
        """
        if not queue_names:
            queue_names = self.get_all_known_queues()
        processes = []
        for queue_name in queue_names:
            queue = self.queue(queue_name)
            p = multiprocessing.Process(
                target=queue.process_queue,
                kwargs={"shutdown_policy": shutdown_policy_maker()},
            )
            p.start()
            processes.append(p)
        for p in processes:
            p.join()

    def queue_exist(self, queue_name: str, raise_error=False) -> Union[bool, None]:
        try:
            prefixed_name = self.get_sqs_queue_name(queue_name)
            self.sqs_client.get_queue_by_name(QueueName=prefixed_name)
            return True
        except ClientError as e:
            if "NonExistentQueue" in e.response["Error"]["Code"]:
                return False
            elif raise_error:
                raise
            else:
                warnings.warn("Client error %d", e.response["Error"]["Message"])

    def get_all_known_queues(self):
        resp = self.sqs_client.list_queues(**{"QueueNamePrefix": self.queue_prefix})
        if "QueueUrls" not in resp:
            return []
        urls = resp["QueueUrls"]
        ret = []
        for url in urls:
            sqs_name = url.rsplit("/", 1)[-1]
            queue_prefix_len = len(self.queue_prefix)
            ret.append(sqs_name[queue_prefix_len:])
        return ret

    def get_sqs_queue_name(self, queue_name):
        """
        Take "high-level" (user-visible) queue name and return SQS
        ("low level") name by simply prefixing it. Used to create namespaces
        for different environments (development, staging, production, etc)
        """
        return "{}{}".format(self.queue_prefix, queue_name)
