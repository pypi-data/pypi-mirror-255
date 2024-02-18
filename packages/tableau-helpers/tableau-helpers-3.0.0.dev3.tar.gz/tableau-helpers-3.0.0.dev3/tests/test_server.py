from pathlib import Path

import pytest
from tableauserverclient.server import FlowItem

import tests.conftest as ct
from tableau_helpers.server import ServerHelper


@pytest.mark.integration
def test_get_project_id():
    project_path = "ApiTest"
    helper = ServerHelper()
    helper.get_project_id(project_path)


@pytest.mark.integration
def test_get_project_id_nested():
    project_path = "ApiTest/Nested"
    helper = ServerHelper()
    helper.get_project_id(project_path)


@pytest.mark.integration
def test_create_or_replace_hyperfile(good_hyper_path=Path(ct.good_hyper_path())):
    helper = ServerHelper()
    helper.create_or_replace_hyper_file(good_hyper_path, "ApiTest", "test-data")


@pytest.mark.integration
def test_create_or_replace_joined_hyperfile(hyper_path=Path(ct.joined_hyper_path())):
    helper = ServerHelper()
    helper.create_or_replace_hyper_file(hyper_path, "ApiTest", "test-data")


@pytest.mark.integration
def test_get_flow_by_name():
    helper = ServerHelper()
    flow: FlowItem = helper.get_flow("ApiTest", "New Flow")
    assert flow is not None
