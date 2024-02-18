from pathlib import Path
from typing import List
from functools import lru_cache
from collections import namedtuple

import pytest
from fastapi.testclient import TestClient

from ewokscore import events
from ewoksjob.tests.conftest import celery_config  # noqa F401
from ewoksjob.tests.conftest import celery_includes  # noqa F401

from .. import app as newserver
from ..app import config as serverconfig
from ..app.backends.binary_backend import _load_url
from ..resources import DEFAULT_ROOT

from .data import resource_filenames
from .socketio_test import SocketIOTestClient


@pytest.fixture
def rest_client(tmpdir):
    """Client to the REST server (no execution)."""
    app = newserver.create_app()

    @lru_cache()
    def get_ewoks_settings_for_tests():
        return serverconfig.EwoksSettings(
            configured=True, resource_directory=str(tmpdir)
        )

    app.dependency_overrides[serverconfig.get_ewoks_settings] = (
        get_ewoks_settings_for_tests
    )

    with TestClient(app) as client:
        yield client


@pytest.fixture()
def ewoks_handlers(tmpdir):
    uri = f"file:{tmpdir / 'ewoks_events.db'}"
    yield [
        {
            "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
            "arguments": [{"name": "uri", "value": uri}],
        }
    ]
    events.cleanup()


@pytest.fixture
def local_exec_client(tmpdir, ewoks_handlers):
    """Client to the REST server and Socket.IO (execution with process pool)."""
    app = newserver.create_app()

    def get_settings_override():
        return serverconfig.EwoksSettings(
            configured=True,
            resource_directory=str(tmpdir),
            ewoks={"handlers": ewoks_handlers},
        )

    app.dependency_overrides[serverconfig.get_ewoks_settings] = get_settings_override

    with TestClient(app) as client:
        with SocketIOTestClient() as sclient:
            yield client, sclient


@pytest.fixture
def celery_exec_client(tmpdir, celery_session_worker, ewoks_handlers):
    """Client to the REST server and Socket.IO (execution with celery)."""
    app = newserver.create_app()

    def get_settings_override():
        return serverconfig.EwoksSettings(
            configured=True,
            resource_directory=str(tmpdir),
            celery=dict(),
            ewoks={"handlers": ewoks_handlers},
        )

    app.dependency_overrides[serverconfig.get_ewoks_settings] = get_settings_override

    with TestClient(app) as client:
        with SocketIOTestClient() as sclient:
            yield client, sclient


@pytest.fixture
def png_icons():
    filenames = resource_filenames()
    return [_load_url(filename) for filename in filenames if filename.endswith(".png")]


@pytest.fixture
def svg_icons():
    filenames = resource_filenames()
    return [_load_url(filename) for filename in filenames if filename.endswith(".svg")]


@pytest.fixture(scope="session")
def default_icon_identifiers() -> List[Path]:
    return [
        url.name
        for url in (DEFAULT_ROOT / "icons").iterdir()
        if not url.name.startswith("__")
    ]


@pytest.fixture(scope="session")
def default_workflow_identifiers() -> List[Path]:
    return [
        url.stem
        for url in (DEFAULT_ROOT / "workflows").iterdir()
        if url.suffix == ".json"
    ]


@pytest.fixture(scope="session")
def default_task_identifiers() -> List[Path]:
    return [
        url.stem for url in (DEFAULT_ROOT / "tasks").iterdir() if url.suffix == ".json"
    ]


@pytest.fixture
def mocked_local_submit(mocker) -> str:
    submit_local_mock = mocker.patch(
        "ewoksserver.app.routes.execution.router.submit_local"
    )

    MockFuture = namedtuple("Future", ["task_id"])

    arguments = dict()
    task_id = 0

    def mocked_submit(*args, **kwargs):
        nonlocal task_id
        arguments["args"] = args
        arguments["kwargs"] = kwargs
        task_id += 1
        return MockFuture(task_id=task_id)

    submit_local_mock.side_effect = mocked_submit
    return arguments
