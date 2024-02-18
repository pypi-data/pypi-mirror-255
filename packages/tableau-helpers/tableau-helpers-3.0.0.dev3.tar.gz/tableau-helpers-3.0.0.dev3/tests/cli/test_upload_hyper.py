import pytest

from tableau_helpers.cli.upload_hyper import main
from tests import conftest


@pytest.mark.parametrize("hyperfile,project", [(conftest.good_hyper_path(), "ApiTest")])
def test_upload_hyper(hyperfile, project):
    args = [
        "--hyperfile",
        hyperfile,
        "--dest",
        project,
    ]
    main(args)


@pytest.mark.parametrize(
    "hyperfile,project,new_name", [(conftest.good_hyper_path(), "ApiTest", "new-name")]
)
def test_upload_hyper_rename(hyperfile, project, new_name):
    args = [
        "--hyperfile",
        hyperfile,
        "--dest",
        project,
        "--new-name",
        new_name,
    ]
    main(args)
