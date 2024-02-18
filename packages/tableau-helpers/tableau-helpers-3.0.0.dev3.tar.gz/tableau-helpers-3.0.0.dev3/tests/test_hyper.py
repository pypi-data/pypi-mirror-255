# Sample Test passing with nose and pytest
from pathlib import Path

import pytest
from tableauhyperapi import CreateMode, HyperException, HyperProcess

import tests.conftest as ct
import tempfile
from tableau_helpers import hyper
from tests.test_utils import textfile_diff

def test_select_csv_columns(
    tmp_path, csv_path=ct.good_csv_path_with_header(), csv_schema=ct.good_csv_schema_selected(), expected_csv_after_select=ct.good_csv_path_after_select()
):
    selected_columns_csv = hyper.select_columns_for_csv(Path(csv_path), csv_schema, delimiter=",", quote="\"", escape="\\", tempdir=tmp_path)
    assert textfile_diff(selected_columns_csv, expected_csv_after_select)


def test_create_hyper_from_default_csv_path_obj(
    tmp_path, csv_path=ct.good_csv_path(), csv_schema=ct.good_csv_schema()
):
    tmp_hyper_file = Path(tmp_path, "tmp.hyper")
    linecount = hyper.copy_csv_to_hyper(tmp_hyper_file, Path(csv_path), csv_schema)
    assert linecount == 2


def test_create_hyper_from_default_csv_path_str(
    tmp_path, csv_path=ct.good_csv_path(), csv_schema=ct.good_csv_schema()
):
    tmp_hyper_file = Path(tmp_path, "tmp.hyper")
    linecount = hyper.copy_csv_to_hyper(tmp_hyper_file, Path(csv_path), csv_schema)
    assert linecount == 2


def test_create_hyper_from_default_tab_path_str(
    tmp_path, csv_path=ct.good_tab_path(), csv_schema=ct.good_csv_schema()
):
    tmp_hyper_file = Path(tmp_path, "tmp.hyper")
    linecount = hyper.copy_csv_to_hyper(
        tmp_hyper_file, Path(csv_path), csv_schema, delimiter="\t"
    )
    assert linecount == 2


def test_fail_create_hyper_from_default_tab_path_str(
    tmp_path, csv_path=ct.good_tab_path(), csv_schema=ct.good_csv_schema()
):
    tmp_hyper_file = Path(tmp_path, "tmp.hyper")
    with pytest.raises(HyperException):
        assert hyper.copy_csv_to_hyper(tmp_hyper_file, Path(csv_path), csv_schema)


def compare_columns(columns_a, columns_b):
    for x, y in zip(columns_a, columns_b):
        assert x.name == y.name
        assert x.nullability == y.nullability
        assert x.type == y.type
        assert x.collation == y.collation


def test_load_good_table_def(
    table_def_path=ct.good_table_def_path(), csv_schema=ct.good_csv_schema()
):
    table_def = hyper.load_table_def(Path(table_def_path))
    assert table_def.table_name == csv_schema.table_name
    compare_columns(table_def.columns, csv_schema.columns)


def test_append_hyper_separate_csv_calls(
    tmp_path,
    csv_left=ct.good_left_path(),
    csv_right=ct.good_right_path(),
    csv_join_left=ct.good_join_left_def_path(),
):
    tmp_hyper_file = Path(tmp_path, "tmp.hyper")
    tabledef = hyper.load_table_def(Path(csv_join_left))
    linecount = hyper.copy_csv_to_hyper(tmp_hyper_file, Path(csv_left), tabledef)
    assert linecount == 2
    linecount = hyper.copy_csv_to_hyper(
        tmp_hyper_file, Path(csv_right), tabledef, create_mode=CreateMode.NONE
    )
    assert linecount == 2
    with HyperProcess(hyper.hyperprocess_env_kws()) as hyperprocess:
        conn = hyper.Connection(hyperprocess.endpoint, tmp_hyper_file)
        query = f"SELECT * FROM {hyper.TableName(tabledef.table_name)}"
        with conn.execute_query(query) as res:
            assert len(list(res)) == 4


def test_copy_multiple_csvs(
    tmp_path,
    csv_left=ct.good_left_path(),
    csv_right=ct.good_right_path(),
    csv_join_left=ct.good_join_left_def_path(),
):
    tmp_hyper_file = Path(tmp_path, "tmp.hyper")
    csvs = [Path(csv_left), Path(csv_right)]
    tabledef = hyper.load_table_def(Path(csv_join_left))
    linecount = hyper.copy_csv_to_hyper(tmp_hyper_file, csvs, tabledef)
    assert linecount == 4
    with HyperProcess(hyper.hyperprocess_env_kws()) as hyperprocess:
        conn = hyper.Connection(hyperprocess.endpoint, tmp_hyper_file)
        query = f"SELECT * FROM {hyper.TableName(tabledef.table_name)}"
        with conn.execute_query(query) as res:
            assert len(list(res)) == 4


def test_create_hyper_with_fact_table(
    tmp_path,
    csv_left=ct.good_left_path(),
    csv_right=ct.good_right_path(),
    csv_join_right=ct.good_join_right_def_path(),
    csv_join_left=ct.good_join_left_def_path(),
):
    tmp_hyper_file = Path(tmp_path, "tmp.hyper")
    [Path(csv_left), Path(csv_right)]
    tabledef_left = hyper.load_table_def(Path(csv_join_left))
    tabledef_right = hyper.load_table_def(Path(csv_join_right))
    linecount = hyper.copy_csv_to_hyper(tmp_hyper_file, Path(csv_left), tabledef_left)
    assert linecount == 2
    linecount = hyper.copy_csv_to_hyper(
        tmp_hyper_file, Path(csv_right), tabledef_right, create_mode=CreateMode.NONE
    )
    assert linecount == 2
    with HyperProcess(hyper.hyperprocess_env_kws()) as hyperprocess:
        conn = hyper.Connection(hyperprocess.endpoint, tmp_hyper_file)
        res = conn.catalog.get_table_names("public")
        assert len(res) == 2


def test_create_hyper_from_default_csv_doesnt_exist(
    tmp_path,
    doesnt_exist_path=ct.doesnt_exist_path(),
    good_csv_schema=ct.good_csv_schema(),
):
    tmp_hyper_file = Path(tmp_path, "tmp.hyper")
    with pytest.raises(FileNotFoundError):
        assert hyper.copy_csv_to_hyper(
            tmp_hyper_file, Path(doesnt_exist_path), good_csv_schema
        )


def test_create_hyper_from_string_path(
    tmp_path,
    doesnt_exist_path=ct.doesnt_exist_path(),
    good_csv_schema=ct.good_csv_schema(),
):
    tmp_hyper_file = Path(tmp_path, "tmp.hyper")
    with pytest.raises(TypeError):
        assert hyper.copy_csv_to_hyper(
            tmp_hyper_file, doesnt_exist_path, good_csv_schema
        )


def test_create_hyper_from_default_csv_with_header(
    tmp_path, good_csv_path=ct.good_csv_path_with_header(), good_csv_schema=ct.good_csv_schema()
):
    tmp_hyper_file = Path(tmp_path, "tmp.hyper")
    linecount = hyper.copy_csv_to_hyper(
        tmp_hyper_file,
        Path(good_csv_path),
        good_csv_schema,
        header=True,
    )
    assert linecount == 2


def test_create_hyper_from_default_csv_bad_schema(
    tmp_path, good_csv_path=ct.good_csv_path(), bad_csv_schema=ct.bad_csv_schema()
):
    tmp_hyper_file = Path(tmp_path, "tmp.hyper")

    with pytest.raises(HyperException):
        assert hyper.copy_csv_to_hyper(
            tmp_hyper_file, Path(good_csv_path), bad_csv_schema
        )
