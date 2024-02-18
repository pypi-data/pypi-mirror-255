import time

import pytest
from ewokscore.tests.examples.graphs import get_graph

from .api_versions import ROOT_ALL_VERSIONS, ROOT_V1_1_0


@pytest.mark.parametrize("root", ROOT_ALL_VERSIONS)
def test_execute_with_celery(celery_exec_client, root):
    _test_execute(root, *celery_exec_client)


@pytest.mark.parametrize("root", ROOT_ALL_VERSIONS)
def test_execute_without_celery(local_exec_client, root):
    _test_execute(root, *local_exec_client)


@pytest.mark.parametrize("root", ROOT_ALL_VERSIONS)
def test_new_client_new_events(local_exec_client, root):
    client, sclient = local_exec_client
    _test_execute(root, client, sclient)
    sclient.disconnect()
    sclient.connect()
    time.sleep(1)
    assert not sclient.get_events()


@pytest.mark.parametrize("root", ROOT_ALL_VERSIONS)
def test_execute_options(rest_client, mocked_local_submit, root):
    workflow = {
        "graph": {
            "id": "myworkflow",
            "label": "label1",
            "category": "cat1",
            "execute_arguments": {
                "engine": "ppf",
                "_slurm_spawn_arguments": {
                    "parameters": {"time_limit": 10, "partition": "nice"},
                    "pre_script": "module load ewoks",
                },
            },
            "worker_options": {"queue": "id00"},
        },
        "nodes": [{"id": "task1"}],
    }
    response = rest_client.post(f"{root}/workflows", json=workflow)
    data = response.json()
    assert response.status_code == 200, data

    # Check that the backend uses execute_arguments and worker_options
    # from the workflow definition
    response = rest_client.post(f"{root}/execute/myworkflow")
    expected_submit_arguments = {
        "args": (),
        "kwargs": {
            "args": (workflow,),
            "kwargs": {
                "engine": "ppf",
                "_slurm_spawn_arguments": {
                    "parameters": {"time_limit": 10, "partition": "nice"},
                    "pre_script": "module load ewoks",
                },
            },
            "queue": "id00",
        },
    }
    assert mocked_local_submit == expected_submit_arguments

    # Check that the backend merges execute_arguments and worker_options
    # from the client
    data = {
        "execute_arguments": {
            "engine": "ppf",
            "_slurm_spawn_arguments": {
                "parameters": {"time_limit": 20, "partition": "nice"},
                "pre_script": "module load ewoks",
            },
        },
        "worker_options": {"queue": "id00", "time_limit": 30},
    }

    response = rest_client.post(f"{root}/execute/myworkflow", json=data)
    expected_submit_arguments = {
        "args": (),
        "kwargs": {
            "args": (workflow,),
            "kwargs": {
                "engine": "ppf",
                "_slurm_spawn_arguments": {
                    "parameters": {"time_limit": 20, "partition": "nice"},
                    "pre_script": "module load ewoks",
                },
            },
            "queue": "id00",
            "time_limit": 30,
        },
    }
    assert mocked_local_submit == expected_submit_arguments


def _test_execute(root, client, sclient):
    graph_name, expected = upload_graph(root, client)
    response = client.post(f"{root}/execute/{graph_name}")
    assert response.status_code == 200, response.json()

    n = 2 * (len(expected) + 2)
    events = get_events(sclient, n)
    _assert_events(response, events, expected)
    return n


def upload_graph(root, client):
    graph_name = "acyclic1"
    graph, expected = get_graph(graph_name)
    response = client.post(f"{root}/workflows", json=graph)
    assert response.status_code == 200, response.json()
    return graph_name, expected


def get_events(sclient, nevents, timeout=10):
    t0 = time.time()
    events = list()
    while True:
        events.extend(sclient.get_events())
        if len(events) == nevents:
            break
        time.sleep(0.1)
        if time.time() - t0 > timeout:
            raise TimeoutError(f"Received {len(events)} instead of {nevents}")
    return events


def _assert_events(response, events, expected):
    n = 2 * (len(expected) + 2)
    assert len(events) == n

    job_id = response.json()["job_id"]
    for event in events:
        assert event["job_id"] == job_id
        if event["node_id"]:
            assert event["node_id"] in expected


@pytest.mark.parametrize("root", ROOT_V1_1_0)
def test_get_workers_with_celery(celery_exec_client, root):
    rest_client, _ = celery_exec_client
    response = rest_client.get(f"{root}/execution/workers")
    assert response.status_code == 200, response.json()
    assert len(response.json()["workers"]) == 1


@pytest.mark.parametrize("root", ROOT_V1_1_0)
def test_get_workers_without_celery(rest_client, root):
    response = rest_client.get(f"{root}/execution/workers")
    assert response.status_code == 200, response.json()
    assert response.json()["workers"] is None
