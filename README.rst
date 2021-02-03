sqs-async
=========

Async Python Processor for SQS.

Example
-------

Decorate any task you have with the decorator.
It can be a function class or coroutine class, the decorator
will wrap them into an asyncio coroutine.

.. code::

    >>> from sqs_async import tasks
    >>> import asyncio
    >>>
    >>> @tasks.register
    ... def message(name):
    ...     print(f"Hello {name}")
    >>>
    >>> @tasks.register
    ... async def async_message(name):
    ...     await asyncio.sleep(1)
    ...     print(f"Hello {name}")

They can be also called normally as we see.

.. code::

    >>> message("World!")
    Hello World!
    >>> async_message("World!")
    Hello World!


Now we create a SQSEnv to handle operations in the sqs environment. The parameter `task_modules`
tells the environment where the tasks are declared. Then the environment can registered
for further processing.

.. code::

    >>> from sqs_async.sqs_env import SQSEnv
    >>> sqs_env = SQSEnv(task_modules=['message_module'])          # create sqs env
    >>> message_queue = sqs_env.queue("message_queue")             # get or create a queue
    >>>
    >>> message.delay(queue=message_queue, args=("World",))        # send task to the queue as a coroutine
    >>>
    >>> async_message.delay(queue=message_queue, args=("World",))  # send task to the queue as a coroutine


Now form a different location we create again an environment.
We now process messages.

.. code::

    >>> from sqs_async.sqs_env import SQSEnv
    >>> sqs_env = SQSEnv(task_modules=["message_module"])
    >>> message_queue = sqs_env.queue("message_queue")
    >>>
    >>> queue.process_queue()                                       # finally you can process a queue in an event loop, or
    >>> sqs_env.process_queues(queue_names=["message_queue"])       # some of them, (multiprocessing, each an event loop)
    >>> sqs_env.process_queues(queue_names=["*"])                   # or all of them
