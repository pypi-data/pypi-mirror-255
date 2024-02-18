from pathlib import Path

import pytest

from tableau_helpers.cli.csv_to_hyper import main
from tests import conftest


@pytest.mark.parametrize(
    "csv,table_def", [(conftest.good_csv_path(), conftest.good_table_def_path())]
)
def test_csv_to_hyper(tmp_path, csv, table_def):
    args = [
        "--csv",
        csv,
        "--table-def",
        table_def,
        "--dest",
        Path(tmp_path, "tmp.hyper").absolute().as_posix(),
    ]
    main(args)


@pytest.mark.parametrize(
    "tsv,table_def", [(conftest.good_tab_path(), conftest.good_table_def_path())]
)
def test_tsv_to_hyper(tmp_path, tsv, table_def):
    args = [
        "--csv",
        tsv,
        "--table-def",
        table_def,
        "--dest",
        Path(tmp_path, "tmp.hyper").absolute().as_posix(),
        "--delimiter",
        "\t",
    ]
    main(args)
