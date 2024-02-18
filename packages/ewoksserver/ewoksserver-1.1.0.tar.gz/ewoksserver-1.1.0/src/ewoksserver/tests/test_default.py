import pytest
from .api_versions import ROOT_ALL_VERSIONS


@pytest.mark.parametrize("root", ROOT_ALL_VERSIONS)
def test_default_workflows(rest_client, default_workflow_identifiers, root):
    for identifier in default_workflow_identifiers:
        response = rest_client.get(f"{root}/workflow/{identifier}")
        data = response.json()
        assert response.status_code == 200, data


@pytest.mark.parametrize("root", ROOT_ALL_VERSIONS)
def test_default_icons(rest_client, default_icon_identifiers, root):
    for identifier in default_icon_identifiers:
        response = rest_client.get(f"{root}/icon/{identifier}")
        data = response.json()
        assert response.status_code == 200, data


@pytest.mark.parametrize("root", ROOT_ALL_VERSIONS)
def test_default_tasks(rest_client, default_task_identifiers, root):
    for identifier in default_task_identifiers:
        response = rest_client.get(f"{root}/task/{identifier}")
        data = response.json()
        assert response.status_code == 200, data
