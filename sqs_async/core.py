import logging
from typing import Any

logger = logging.getLogger(__name__)


class BatchProcessingResult(object):
    def __init__(self, queue_name, succeeded=None, failed=None):
        self.queue_name = queue_name
        self.succeeded = succeeded or []
        self.failed = failed or []

    def update_with_message(self, message, success):
        # type: (Any, bool) -> None
        """
        Update processing result with a message.
        """
        if success:
            self.succeeded.append(message)
        else:
            self.failed.append(message)

    def succeeded_count(self):
        return len(self.succeeded)

    def failed_count(self):
        return len(self.failed)

    def total_count(self):
        return self.succeeded_count() + self.failed_count()

    def __repr__(self):
        return "<BatchProcessingResult/%s/%s/%s>" % (
            self.queue_name,
            self.succeeded_count(),
            self.failed_count(),
        )


def get_job_name(message):
    attrs = message.message_attributes or {}
    return (attrs.get("JobName") or {}).get("StringValue")
