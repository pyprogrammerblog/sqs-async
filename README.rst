sqs-async
=========

Async Python Processor for SQS

Example
-------

Decorate any task you have and create a SQSAsyncEnv object:

.. code::

    >>> import async_sqs.tasks import register
    >>> @register
    ... def message(name):
    ...     print(f"Hello {name}")
    >>>
    >>> message.delay(args=("World",))


.. code::

    >>> from async_sqs import SQSAsyncEnv
    >>> sqs = SQSAsyncEnv()  # this register all tasks. autodiscover=True
    >>> sqs.registered_tasks


Get or create a new queue...

.. code::

    >>> queue = sqs.create("messages")
    >>> queue = sqs.queue("messages")
    >>> queue = sqs.get_or_create("messages")


Start sending tasks to the queue...

.. code::

    >>> from async_tasks import send_message
    >>> send_message.delay(args, kwargs)      # this add into the queue a job
    >>> send_message(args, kwargs)            # this run the task as normal method


Process them...

.. code::

    >>> sqs.queue('messages').process()  # uses asyncio, aiohttp and aiobotocore
    >>> queue.process_all()  # opens multiprocessing

