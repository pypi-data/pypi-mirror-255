import os
import shutil
import logging
from pprint import pformat
from typing import Generator
from contextlib import contextmanager
from contextlib import asynccontextmanager

from fastapi import FastAPI
from ewoksjob.client.local import pool_context
from celery import current_app as current_celery_app

from .backends import json_backend
from .. import resources
from . import config
from .routes.execution import socketio
from .routes.tasks.discovery import discover_tasks


logger = logging.getLogger(__name__)


@asynccontextmanager
async def fastapi_lifespan(app: FastAPI) -> Generator[None, None, None]:
    get_ewoks_settings = app.dependency_overrides.get(
        config.get_ewoks_settings, config.get_ewoks_settings
    )
    ewoks_settings = get_ewoks_settings()
    _configure_socketio(ewoks_settings)
    _copy_default_resources(ewoks_settings)
    _enable_execution_events(ewoks_settings)
    with _enable_execution(ewoks_settings):
        _rediscover_tasks(ewoks_settings)
        _print_ewoks_settings(ewoks_settings)
        yield


def _configure_socketio(app_settings: config.EwoksSettings) -> None:
    socketio.configure_socketio(app_settings)


def _copy_default_resources(ewoks_settings: config.EwoksSettings) -> None:
    """Copy the default resources (tasks, workflows and icon) from the
    python package to the resource directory."""
    for resource, resource_ext in {
        "tasks": [".json"],
        "icons": [".png", ".svg"],
        "workflows": [".json"],
    }.items():
        root_url = json_backend.root_url(ewoks_settings.resource_directory, resource)
        os.makedirs(root_url, exist_ok=True)
        for filename in os.listdir(resources.DEFAULT_ROOT / resource):
            _, ext = os.path.splitext(filename)
            if ext not in resource_ext:
                continue

            src = resources.DEFAULT_ROOT / resource / filename
            if not os.path.isfile(src):
                continue

            dest = root_url / filename
            if not os.path.exists(dest):
                shutil.copy(src, dest)


def _rediscover_tasks(ewoks_settings: config.EwoksSettings) -> None:
    if not ewoks_settings.discover_tasks:
        return
    tasks = discover_tasks(ewoks_settings)
    root_url = json_backend.root_url(ewoks_settings.resource_directory, "tasks")
    for resource in tasks:
        json_backend.save_resource(root_url, resource["task_identifier"], resource)


def _enable_execution_events(ewoks_settings: config.EwoksSettings) -> None:
    """Set default ewoks event handler when nothing has been configured"""
    if ewoks_settings.configured:
        return
    if ewoks_settings.ewoks is None:
        ewoks_settings.ewoks = dict()
    if not ewoks_settings.ewoks.get("handlers"):
        ewoks_settings.ewoks["handlers"] = [
            {
                "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
                "arguments": [
                    {
                        "name": "uri",
                        "value": "file:ewoks_events.db",
                    }
                ],
            }
        ]


@contextmanager
def _enable_execution(
    ewoks_settings: config.EwoksSettings,
) -> Generator[None, None, None]:
    """Ensure workflows can be executed"""
    if ewoks_settings.celery is None:
        with pool_context():
            yield
    else:
        current_celery_app.conf.update(ewoks_settings.celery)
        yield


def _print_ewoks_settings(ewoks_settings: config.EwoksSettings) -> None:
    """Print summary of all Ewoks settings"""
    lines = list()
    resourcedir = ewoks_settings.resource_directory
    if not resourcedir:
        resourcedir = "."
    lines += ["", "", "RESOURCE DIRECTORY:", os.path.abspath(resourcedir)]

    adict = ewoks_settings.celery
    if adict is None:
        lines += ["", "CELERY:", "Not configured (local workflow execution)"]
    else:
        lines += ["", "CELERY:", pformat(adict)]

    adict = ewoks_settings.ewoks
    if adict is None:
        lines += ["", "EWOKS:", "Not configured (local workflow execution)"]
    else:
        lines += ["", "EWOKS:", pformat(adict)]

    lines += [""]

    logger.info("\n".join(lines))
