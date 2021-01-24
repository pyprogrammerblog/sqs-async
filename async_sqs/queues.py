
import abc


class AbstractQueue(abc.ABC):
    name: str

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

    def __init__(self, name):
        self.name = name

    def add_job(
        self,
        job_name,
        _content_type=codecs.DEFAULT_CONTENT_TYPE,
        _delay_seconds=None,
        _deduplication_id=None,
        _group_id=None,
        **job_kwargs
    ):
        """
        Add job to the queue.
        """
        return q.add_job(
            job_name,
            _content_type=_content_type,
            _delay_seconds=_delay_seconds,
            _deduplication_id=_deduplication_id,
            _group_id=_group_id,
            **job_kwargs
        )
