import os

import pytest
from dotenv import load_dotenv
from tableauhyperapi import SqlType, TableDefinition, TableName


@pytest.fixture(autouse=True)
def load_env():
    load_dotenv()


def good_csv_path():
    return os.path.abspath("tests/resources/good_default_format.csv")


def good_csv_path_with_header():
    return os.path.abspath("tests/resources/good_default_format_with_header.csv")


def good_csv_path_after_select():
    return os.path.abspath("tests/resources/good_default_format_text2_selected.csv")


def good_csv2_path():
    return os.path.abspath("tests/resources/good_default_format2.csv")


def good_left_path():
    return os.path.abspath("tests/resources/good_left.csv")


def good_right_path():
    return os.path.abspath("tests/resources/good_right.csv")


def good_tab_path():
    return os.path.abspath("tests/resources/good_default_format.tab")


def doesnt_exist_path():
    return os.path.abspath("tests/resources/doesnt_exist.csv")


def good_csv_schema():
    return TableDefinition(
        table_name=TableName("test_table_name"),
        columns=[
            TableDefinition.Column("integers", SqlType.int()),
            TableDefinition.Column("text1", SqlType.text()),
            TableDefinition.Column("text2", SqlType.text()),
        ],
    )

def good_csv_schema_selected():
    return TableDefinition(
        table_name=TableName("test_table_name"),
        columns=[
            TableDefinition.Column("text2", SqlType.text()),
        ],
    )


def bad_csv_schema():
    return TableDefinition(
        table_name=TableName("test_table_name"),
        columns=[
            TableDefinition.Column("integers", SqlType.int()),
            TableDefinition.Column("text1", SqlType.int()),
            TableDefinition.Column("text2", SqlType.text()),
        ],
    )


def good_table_def_path():
    return os.path.abspath("tests/resources/good_default_format_table_def.json")


def good_join_table_def_path():
    return os.path.abspath("tests/resources/good_join_table_def.json")


def good_join_right_def_path():
    return os.path.abspath("tests/resources/good_join_right_def.json")


def good_join_left_def_path():
    return os.path.abspath("tests/resources/good_join_left_def.json")


def good_hyper_path():
    return os.path.abspath("tests/resources/good_default_format.hyper")


def joined_hyper_path():
    return os.path.abspath("tests/resources/joined.hyper")
