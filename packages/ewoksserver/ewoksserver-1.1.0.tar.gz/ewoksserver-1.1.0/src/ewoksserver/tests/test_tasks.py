import pytest
from .api_versions import ROOT_ALL_VERSIONS


@pytest.mark.parametrize("root", ROOT_ALL_VERSIONS)
def test_single_task(rest_client, root):
    identifier = "myproject.tasks.Dummy"

    response = rest_client.get(f"{root}/task/{identifier}")
    data = response.json()
    expected = {
        "message": "Task 'myproject.tasks.Dummy' is not found.",
        "type": "task",
        "identifier": "myproject.tasks.Dummy",
    }
    assert response.status_code == 404
    assert data == expected

    task1a = {
        "task_identifier": identifier,
        "task_type": "class",
        "required_input_names": ["a"],
    }
    response = rest_client.post(f"{root}/tasks", json=task1a)
    data = response.json()
    assert response.status_code == 200, data
    expected = {
        "required_input_names": ["a"],
        "task_identifier": "myproject.tasks.Dummy",
        "task_type": "class",
    }
    assert data == expected

    response = rest_client.get(f"{root}/task/{identifier}")
    data = response.json()
    assert response.status_code == 200, data
    assert data == task1a

    task1b = {
        "task_identifier": identifier,
        "task_type": "class",
        "required_input_names": ["a", "b"],
    }
    response = rest_client.put(f"{root}/task/{identifier}", json=task1b)
    data = response.json()
    assert response.status_code == 200, data
    expected = {
        "required_input_names": ["a", "b"],
        "task_identifier": "myproject.tasks.Dummy",
        "task_type": "class",
    }
    assert data == expected

    response = rest_client.get(f"{root}/task/{identifier}")
    data = response.json()
    assert response.status_code == 200, data
    assert data == task1b

    response = rest_client.delete(f"{root}/task/{identifier}")
    data = response.json()
    assert response.status_code == 200
    assert data == {"identifier": identifier}

    response = rest_client.delete(f"{root}/task/{identifier}")
    data = response.json()
    assert response.status_code == 404
    assert data == {
        "identifier": identifier,
        "message": f"Task '{identifier}' is not found.",
        "type": "task",
    }

    response = rest_client.get(f"{root}/task/{identifier}")
    data = response.json()
    assert response.status_code == 404
    expected = {
        "identifier": identifier,
        "message": f"Task '{identifier}' is not found.",
        "type": "task",
    }
    assert data == expected


@pytest.mark.parametrize("root", ROOT_ALL_VERSIONS)
def test_multiple_tasks(rest_client, default_task_identifiers, root):
    response = rest_client.get(f"{root}/tasks")
    data = response.json()
    assert response.status_code == 200
    assert sorted(data["identifiers"]) == sorted(default_task_identifiers)

    task1a = {
        "task_identifier": "myproject.tasks.Dummy1",
        "task_type": "class",
        "required_input_names": ["a"],
    }
    task1b = {
        "task_identifier": "myproject.tasks.Dummy1",
        "task_type": "class",
        "required_input_names": ["a", "b"],
    }
    task2 = {
        "task_identifier": "myproject.tasks.Dummy2",
        "task_type": "class",
        "required_input_names": ["a", "b"],
    }

    response = rest_client.post(f"{root}/tasks", json=task1a)
    data = response.json()
    assert response.status_code == 200, data
    assert data == task1a

    response = rest_client.post(f"{root}/tasks", json=task1b)
    data = response.json()
    assert response.status_code == 409, data
    expected = {
        "identifier": "myproject.tasks.Dummy1",
        "message": "Task 'myproject.tasks.Dummy1' already exists.",
        "type": "task",
    }
    assert data == expected

    response = rest_client.post(f"{root}/tasks", json=task2)
    data = response.json()
    assert response.status_code == 200, data
    assert data == task2

    response = rest_client.get(f"{root}/tasks")
    data = response.json()
    assert response.status_code == 200, data
    expected = default_task_identifiers + [
        "myproject.tasks.Dummy1",
        "myproject.tasks.Dummy2",
    ]
    assert sorted(data["identifiers"]) == sorted(expected)


@pytest.mark.parametrize("root", ROOT_ALL_VERSIONS)
def test_discover_tasks(rest_client, default_task_identifiers, root):
    response = rest_client.get(f"{root}/tasks")
    data = response.json()
    assert response.status_code == 200
    assert sorted(data["identifiers"]) == sorted(default_task_identifiers)

    module = "ewoksserver.tests.dummy_tasks"

    response = rest_client.post(f"{root}/tasks/discover", json={"modules": [module]})
    data = response.json()
    assert response.status_code == 200, data
    expected = [
        "ewoksserver.tests.dummy_tasks.MyTask1",
        "ewoksserver.tests.dummy_tasks.MyTask2",
    ]
    assert sorted(data["identifiers"]) == sorted(expected)

    response = rest_client.get(f"{root}/tasks")
    data = response.json()
    assert response.status_code == 200
    expected = default_task_identifiers + [
        "ewoksserver.tests.dummy_tasks.MyTask1",
        "ewoksserver.tests.dummy_tasks.MyTask2",
    ]
    assert sorted(data["identifiers"]) == sorted(expected)

    response = rest_client.post(f"{root}/tasks/discover", json={"modules": [module]})
    data = response.json()
    assert response.status_code == 200, data

    response = rest_client.post(
        f"{root}/tasks/discover", json={"modules": ["not_a_module"]}
    )
    data = response.json()
    assert response.status_code == 404, data
    assert "No module named" in data["message"]

    response = rest_client.post(f"{root}/tasks/discover")
    data = response.json()
    assert response.status_code == 200, data
    assert data["identifiers"]


@pytest.mark.parametrize("root", ROOT_ALL_VERSIONS)
def test_task_descriptions(rest_client, default_task_identifiers, root):
    response = rest_client.get(f"{root}/tasks/descriptions")
    data = response.json()
    assert response.status_code == 200
    default_descriptions = [
        desc
        for desc in data["items"]
        if desc["task_identifier"] in default_task_identifiers
    ]
    assert data == {"items": default_descriptions}

    module = "ewoksserver.tests.dummy_tasks"

    response = rest_client.post(f"{root}/tasks/discover", json={"modules": [module]})
    data1 = response.json()
    assert response.status_code == 200, data1

    response = rest_client.get(f"{root}/tasks/descriptions")
    data2 = response.json()["items"]
    data2 = [
        r["task_identifier"] for r in data2 if r["task_identifier"].startswith(module)
    ]
    assert response.status_code == 200
    assert sorted(data1["identifiers"]) == sorted(data2)
