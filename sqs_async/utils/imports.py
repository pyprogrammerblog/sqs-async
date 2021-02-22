import importlib

from typing import List
from inspect import getmembers
from sqs_async.tasks import AsyncTask


def isasynctask(object):
    """Return true if the object is a AsyncTask."""

    return isinstance(object, AsyncTask)


def get_registered_tasks(locations: List[str], file_name: str = "tasks"):
    """

    :param file_name:
    :param location: str. 'sqs_async.test_project'
    :param file: str. 'tasks'
    :return: dict
    """
    tasks = {}

    for location in locations:
        full_location = f"{location}.{file_name}"
        module = importlib.import_module(full_location)
        members = dict(getmembers(module, isasynctask))
        tasks.update({f"{full_location}.{k}": v for k, v in members.items()})

    return tasks
