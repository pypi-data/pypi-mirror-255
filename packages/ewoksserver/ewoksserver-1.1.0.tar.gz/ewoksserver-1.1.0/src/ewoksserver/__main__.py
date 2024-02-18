"""Start ewoks server from the command line (supports configuration)

..code: bash

    ewoks-server --reload
"""

import sys
import logging
from typing import Optional, List

import click
from uvicorn.main import main as uvicorn_cmd

from .app.config import create_ewoks_settings
from .app.config import create_app_settings


uvicorn_cmd = click.option(
    "--config",
    type=str,
    default=None,
    help="Path to the config python script (equivalent to the environment variable 'EWOKSSERVER_SETTINGS')",
)(uvicorn_cmd)

uvicorn_cmd = click.option(
    "--dir",
    type=str,
    default=None,
    help="Root directory for resources (e.g. workflows, tasks, icons descriptions)",
)(uvicorn_cmd)

uvicorn_cmd = click.option(
    "--without-events",
    is_flag=True,
    help="Disable Socket.IO app for event stream",
)(uvicorn_cmd)

uvicorn_cmd = click.option(
    "--frontend-tests",
    is_flag=True,
    help="Load frontend test configuration",
)(uvicorn_cmd)

uvicorn_cmd = click.option(
    "--rediscover-tasks",
    is_flag=True,
    help="Run task discovery on start up",
)(uvicorn_cmd)

uvicorn_cmd = click.option(
    "--no-older-versions",
    is_flag=True,
    help="Do not provide end-points for older versions of the Ewoks API",
)(uvicorn_cmd)


def ewoks_main(
    config: Optional[str] = None,  # ewoks parameter
    dir: Optional[str] = None,  # ewoks parameter
    without_events: bool = False,  # ewoks parameter
    frontend_tests: bool = False,  # ewoks parameter
    rediscover_tasks: bool = False,  # ewoks parameter
    no_older_versions: bool = False,  # app parameter
    log_level: Optional[str] = None,  # uvicorn parameter
    **kw
):
    if not log_level:
        log_level = "info"
    if log_level:
        level = logging.getLevelName(log_level.upper())
        logging.basicConfig(
            level=level, format="%(levelname)8s(BACKEND %(asctime)s): %(message)s"
        )
    create_app_settings(no_older_versions=no_older_versions)
    create_ewoks_settings(
        config=config,
        directory=dir,
        without_events=without_events,
        frontend_tests=frontend_tests,
        rediscover_tasks=rediscover_tasks,
    )
    return uvicorn_main(log_level=log_level, **kw)


uvicorn_main = uvicorn_cmd.callback
uvicorn_cmd.callback = ewoks_main


def main(argv: Optional[List[str]] = None) -> None:
    """Exposes the uvicorn CLI with a default APP factory"""
    if argv is None:
        argv = sys.argv[1:]
    if "--factory" not in argv:
        argv += ["--factory", "ewoksserver.app:create_app"]
    uvicorn_cmd(argv)


if __name__ == "__main__":
    sys.exit(main())
