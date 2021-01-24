import abc
import multiprocessing
import warnings
from typing import TYPE_CHECKING, Dict, Optional, Type, Union
from async_sqs.queues import Queue
from async_sqs.backoff_policies import DEFAULT_BACKOFF

import boto3


class AbstractSQSEnv(abc.ABC):

    def get_queue(self, name: str):
        raise NotImplementedError

    def create_queue(self):
        raise NotImplementedError

    def delete_queue(self):
        raise NotImplementedError


class SQSEnv(AbstractSQSEnv):

    def __init__(self, session, queue_prefix):
        self.session = boto3.client('sqs')
        self.queue_prefix = queue_prefix
        self.backoff_policy = DEFAULT_BACKOFF
        self.processor_maker = None
        self.context_maker = None
        self.context = None
        self.queues = None
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

    def queue(
        self,
        queue_name: str,
        backoff_policy=None,
    ):
        """
        Get a queue object, initializing it with queue_maker if necessary.
        """
        if queue_name not in self.queues:
            backoff_policy = backoff_policy or self.backoff_policy
            queue = Queue(name=queue_name, backoff_policy=backoff_policy)
            self.queues[queue_name] = queue
        return self.queues[queue_name]
