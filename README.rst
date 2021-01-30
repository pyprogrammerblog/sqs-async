sqs-async
=========

Async Python Processor for SQS

Example
-------

Decorate any task you have and create a SQSAsyncEnv object:

.. code::

    >>> import async_sqs import tasks
        >>>
        >>> @tasks.register
        ... def message(name):              # a message is any task decorate
        ...     print(f"Hello {name}")
        >>>
        >>> message.delay(args=("World",))  # this is converted into an awaitable like below
        >>>
        >>> import asyncio
        >>>
        >>> @tasks.register
        ... async def message(name):
        ...     await asyncio.sleep(1)
        >>>
        >>> message.delay(queue=queue, args=("World",))
        >>> message.delay(args=("World",))  # this goes to default queue
        >>>
        >>> from async_sqs.sqs_env import SQSEnv
        >>> queue = SQSEnv().queue("messages")
        >>> queue.process_queue()   # this run async event loop, all is manage as coroutines
        >>>
        >>> @tasks.register
        ... def message(name):              # a message is any task decorate
        ...     print(f"Hello {name}")
        >>>
        >>> message.delay(args=("World",))  # this is converted into an awaitable like below
        >>>
        >>> import asyncio
        >>>
        >>> @tasks.register
        ... async def message(name):
        ...     await asyncio.sleep(1)
        >>>
        >>> message.delay(queue=queue, args=("World",))
        >>> message.delay(args=("World",))  # this goes to default queue
        >>>
        >>> from async_sqs.sqs_env import SQSEnv
        >>> queue = SQSEnv().queue("messages")
        >>> queue.process_queue()   # this run async event loop, all is manage as coroutines
    >>>
    >>> @tasks.register
    ... def message(name):              # a message is any task decorate
    ...     print(f"Hello {name}")
    >>>
    >>> message.delay(args=("World",))  # this is converted into an awaitable like below
    >>>
    >>> import asyncio
    >>>
    >>> @tasks.register
    ... async def message(name):
    ...     await asyncio.sleep(1)
    >>>
    >>> message.delay(queue=queue, args=("World",))
    >>> message.delay(args=("World",))  # this goes to default queue
    >>>
    >>> from async_sqs.sqs_env import SQSAsyncEnv
    >>> queue = SQSEnv().queue("messages")
    >>> queue.process_queue()   # this run async event loop, all is manage as coroutines
    >>>
    >>> @tasks.register
    ... def message(name):              # a message is any task decorate
    ...     print(f"Hello {name}")
    >>>
    >>> message.delay(args=("World",))  # this is converted into an awaitable like below
    >>>
    >>> import asyncio
    >>>
    >>> @tasks.register
    ... async def message(name):
    ...     await asyncio.sleep(1)
    >>>
    >>> message.delay(queue=queue, args=("World",))
    >>> message.delay(args=("World",))  # this goes to default queue
    >>>
    >>> from async_sqs.sqs_env import SQSEnv
    >>> queue = SQSEnv().queue("messages")
    >>> queue.process_queue()   # this run async event loop, all is manage as coroutines

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

