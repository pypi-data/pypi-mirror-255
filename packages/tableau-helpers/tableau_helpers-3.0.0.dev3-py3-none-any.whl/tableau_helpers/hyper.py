from collections import defaultdict
import csv
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Iterable, Optional, Union

from tableauhyperapi import (
    Connection,
    CreateMode,
    HyperProcess,
    Nullability,
    SqlType,
    TableDefinition,
    TableName,
    Telemetry,
    TypeTag,
    escape_string_literal,
)

logger = logging.getLogger(__name__)


def hyperprocess_env_kws() -> dict:
    telemetry_enabled = os.getenv("TABLEAU_HYPERAPI_TELEMETRY", False)
    telemetry = Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU
    if telemetry_enabled:
        telemetry = Telemetry.SEND_USAGE_DATA_TO_TABLEAU

    user_agent = os.getenv("TABLEAU_HYPERAPI_USER_AGENT", "")
    hyper_bin = os.getenv("TABLEAU_HYPERAPI_HYPER_BINARY", None)

    parameters = {}
    log_disable = os.getenv("TABLEAU_HYPERAPI_LOG_DISABLE", None)
    if log_disable is not None:
        parameters["log_config"] = ""  # empty string disables log
    log_dir = os.getenv("TABLEAU_HYPERAPI_LOG_DIR", None)
    if log_dir is not None:
        parameters["log_dir"] = log_dir
    log_file_max_count = os.getenv("TABLEAU_HYPERAPI_LOG_FILE_MAX_COUNT", "7")
    parameters["log_file_max_count"] = log_file_max_count
    log_file_size_limit = os.getenv("TABLEAU_HYPERAPI_LOG_FILE_SIZE_LIMIT", "100M")
    parameters["log_file_size_limit"] = log_file_size_limit

    return {
        "telemetry": telemetry,
        "user_agent": user_agent,
        "hyper_path": hyper_bin,
        "parameters": parameters,
    }


def select_columns_for_csv( csv_path: Path, schema: TableDefinition, delimiter, quote, escape, tempdir: Path ) -> Path:
    schema_column_names = [column.name.unescaped for column in schema.columns]
    tmp_filtered_path = Path(tempdir, f"{uuid.uuid4()}.csv")
    with open(csv_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter,quotechar=quote,escapechar=escape)
        with open(tmp_filtered_path, "w", newline='') as filtered_csv:
            quoting = csv.QUOTE_MINIMAL
            writer = csv.DictWriter(filtered_csv, fieldnames=schema_column_names, delimiter=delimiter, quotechar=quote, escapechar=escape, quoting=quoting)
            writer.writeheader()
            for row in reader:
                filtered_row = {key: value for (key,value) in row.items() if key in schema_column_names}
                writer.writerow(filtered_row)
    return tmp_filtered_path


def _gen_sql_for_with_csv(
    delimiter: str = ",",
    null: str = "",
    encoding: str = "utf-8",
    on_cast_failure: str = "error",
    header: bool = False,
    quote: str = '"',
    escape: Optional[str] = None,
    force_not_null: Optional[list[str]] = None,
    force_null: Optional[list[str]] = None,
):
    sql_with: str = "WITH ("
    sql_with += "FORMAT csv"
    sql_with += f", NULL {escape_string_literal(null)}"
    sql_with += f", DELIMITER {escape_string_literal(delimiter)}"
    sql_with += f", ENCODING {escape_string_literal(encoding)}"
    sql_with += f", ON_CAST_FAILURE {escape_string_literal(on_cast_failure)}"
    if header:
        sql_with += ", HEADER"
    sql_with += f", QUOTE {escape_string_literal(quote)}"
    if escape is not None:
        sql_with += f", ESCAPE {escape_string_literal(escape)}"
    if force_not_null is not None:
        sql_with += f", FORCE_NOT_NULL ({','.join(force_not_null)})"
    if force_null is not None:
        sql_with += f", FORCE_NULL ({','.join(force_null)})"
    sql_with += ")"
    return sql_with


def load_table_def(table_conf_file: Path) -> TableDefinition:
    with open(table_conf_file) as file:
        table_conf = json.load(file)
    return parse_table_definition(table_conf)


def parse_columns(columns: dict) -> Iterable[TableDefinition.Column]:
    for col in columns:
        name = col.get("name", None)
        if not name:
            raise ValueError("No name was provided for a column.")
        sql_type = col.get("sql_type", None)
        if not sql_type:
            logger.info("sql_type not set for column: %s, defaulting to TEXT", name)
            # log that varchar is default
        nullability = col.get("nullable", None)
        if nullability:
            nullability = Nullability.NULLABLE
        elif not nullability:
            nullability = Nullability.NOT_NULLABLE
        elif nullability is None:
            logger.info("Nullability defaulting to NOT_NULLABLE for column: %s", name)
            nullability = Nullability.NOT_NULLABLE
            # log that default is not nullable
        # don't check for collation presence because None is typical default for binary
        collation = col.get("collation", None)
        sql_type = SqlType(TypeTag[sql_type])
        yield TableDefinition.Column(name, sql_type, nullability, collation)


def parse_table_definition(tableconf: dict) -> TableDefinition:
    table_name = tableconf.get("table_name", None)
    columns = tableconf.get("columns", [])
    columns = parse_columns(columns)
    table_def = TableDefinition(TableName(table_name), columns)
    constraints = tableconf.get("constraints")
    if constraints is not None:
        if isinstance(constraints, str):
            constraints = [constraints]
        table_def.th_alterations = [
            f'ALTER TABLE "{table_name}" ADD {x}' for x in constraints
        ]
    return table_def


def copy_csv_to_hyper(
    save_path: Path,
    csv_path: Union[Path, list[Path]],
    schema: TableDefinition,
    delimiter: str = ",",
    null: str = "",
    encoding: str = "utf-8",
    on_cast_failure: str = "error",
    header: bool = False,
    quote: str = '"',
    escape: Optional[str] = None,
    force_not_null: Optional[list[str]] = None,
    force_null: Optional[list[str]] = None,
    create_mode: CreateMode = CreateMode.CREATE_AND_REPLACE,
) -> Optional[int]:
    """
    :param save_path: where to save the resulting hyperfile
    :param csv_path: the csv or list of csv paths to be imported
    :param schema: the TableDefinition for the destination hyperfile
    :param delimiter: the separator character for the input csv
    :param null: the string which represents a null in the csv
    :param encoding: the encoding type of the csv
        { 'utf-8' | 'utf-16' | 'utf-16-le' | 'utf-16-be' }
    :param on_cast_failure: how to handle a failure to cast types
        { 'error' | 'set_null' }
    :param header: if a header is present in the csv
    :param quote: character used to mark quoted fields
    :param escape: Specifies the character that should appear
        before a data character that matches the QUOTE value.
        The default is the same as the QUOTE value
        (so that the quoting character is doubled if it appears
        in the data). This must be a single one-byte character.
    :param force_not_null: Do not match the specified columns'
        values against the null string. In the default case
        where the null string is empty, this means that empty
        values will be read as zero-length strings rather than
        nulls, even when they are not quoted.
    :param force_null: Match the specified columns' values
        against the null string, even if it has been quoted,
        and if a match is found set the value to NULL.
        In the default case where the null string is empty,
        this converts a quoted empty string into NULL.
    :param create_mode: use CreateMode.NONE when appending a hyperfile
    :return: the count of rows written to the hyper file,
        otherwise None
    """  # noqa
    sql_commands: list[str] = []
    alterations: list[str] = []

    if isinstance(csv_path, str):
        raise TypeError("str instead of Path object passed as csv")
    if isinstance(csv_path, Path):
        csv_path = [csv_path]
    for c in csv_path:
        if not c.exists():
            raise FileNotFoundError(str(c))
        sql_from = f"COPY {schema.table_name} "
        sql_from += f"FROM {escape_string_literal(str(c))}"

        sql_with = _gen_sql_for_with_csv(
            delimiter=delimiter,
            null=null,
            encoding=encoding,
            on_cast_failure=on_cast_failure,
            header=header,
            quote=quote,
            escape=escape,
            force_not_null=force_not_null,
            force_null=force_null,
        )
        sql_commands.append(f"{sql_from} {sql_with}")
        try:
            if schema.th_alterations is not None:
                [alterations.append(x) for x in schema.th_alterations]
        except AttributeError:
            # alterations are optional
            pass

    with (
        HyperProcess(**hyperprocess_env_kws()) as hyper_process,
        Connection(
            endpoint=hyper_process.endpoint,
            database=save_path,
            create_mode=create_mode,
        ) as connection,
    ):
        rowcount = 0
        for command in sql_commands:
            connection.catalog.create_table_if_not_exists(table_definition=schema)
            rowcount += connection.execute_command(command)
        for command in alterations:
            connection.execute_command(command)

    return rowcount
