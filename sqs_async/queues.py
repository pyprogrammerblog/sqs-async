import abc
import logging
import warnings
import boto3

from sqs_async import codecs
from typing import TYPE_CHECKING
from botocore.exceptions import ClientError
from sqs_async.backoff_policies import DEFAULT_BACKOFF
from sqs_async.backoff_policies import BackoffPolicy

DEFAULT_MESSAGE_GROUP_ID = "default"
SEND_BATCH_SIZE = 10


logger = logging.getLogger()

if TYPE_CHECKING:
    from sqs_async.sqs_env import SQSEnv


class AbstractQueue(abc.ABC):
    name: str

    def add_job(
        self,
        job_name: str,
        content_type,
        delay_seconds: int = None,
        deduplication_id=None,
        group_id=None,
        kwargs=None,
    ):
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
        backoff_policy: BackoffPolicy = DEFAULT_BACKOFF,
        raise_error=False
    ) -> None:
        self.env = env
        self.queue_name = name
        self.backoff_policy = backoff_policy
        self.sqs_queue = None,

        sqs = env.sqs_resource
        prefixed_name = self.get_sqs_queue_name()
        try:
            self.sqs_queue = sqs.get_queue_by_name(QueueName=prefixed_name)
        except ClientError as e:
            if "NonExistentQueue" in e.response["Error"]["Code"]:
                self.sqs_queue = sqs.create_queue(QueueName=prefixed_name)
            elif raise_error:
                raise
            else:
                warnings.warn("Client error %d", e.response["Error"]["Message"])


    def add_job(
        self,
        job_name,
        content_type=codecs.DEFAULT_CONTENT_TYPE,
        delay_seconds=None,
        deduplication_id=None,
        group_id=None,
        kwargs=None,
    ):
        """
        Add job to the queue. The body of the job will be converted to the text
        with one of the codes (by default it's "pickle")
        """
        codec = codecs.get_codec(content_type)
        message_body = codec.serialize(kwargs)
        return self.add_raw_job(
            job_name,
            message_body,
            content_type,
            delay_seconds,
            deduplication_id,
            group_id,
        )

    def add_raw_job(
        self,
        job_name,
        message_body,
        content_type,
        delay_seconds,
        deduplication_id,
        group_id,
    ):
        """
        Low-level function to put message to the queue
        """
        # if queue name ends with .fifo, then according to the AWS specs,
        # it's a FIFO queue, and requires group_id.
        # Otherwise group_id can be set to None
        if group_id is None and self.name.endswith(".fifo"):
            group_id = DEFAULT_MESSAGE_GROUP_ID

        kwargs = {
            "MessageBody": message_body,
            "MessageAttributes": {
                "ContentType": {"StringValue": content_type, "DataType": "String"},
                "JobName": {"StringValue": job_name, "DataType": "String"},
            },
        }
        if delay_seconds is not None:
            kwargs["DelaySeconds"] = int(delay_seconds)
        if deduplication_id is not None:
            kwargs["MessageDeduplicationId"] = str(deduplication_id)
        if group_id is not None:
            kwargs["MessageGroupId"] = str(group_id)

        ret = self.sqs_queue.send_message(**kwargs)
        return ret["MessageId"]

    def get_sqs_queue_name(self):
        """
        Take "high-level" (user-visible) queue name and return SQS
        ("low level") name by simply prefixing it. Used to create namespaces
        for different environments (development, staging, production, etc)
        """
        return self.env.get_sqs_queue_name(self.sqs_queue)
