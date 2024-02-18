import argparse
import logging
import sys
from pathlib import Path
import tempfile


from tableau_helpers import hyper, utils
from tableau_helpers.cli import logs

tempdir = tempfile.TemporaryDirectory()
log = logging.getLogger(__name__)


def literal(value: str) -> str:
    return value.encode().decode("unicode_escape")


def _parse_args(args):
    description = (
        "csv_to_hyper creates a hyperfile with Tableau's hyperapi given a csv and"
        " table-definition"
    )
    parser = argparse.ArgumentParser(description=description)
    levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    parser.add_argument("--log-level", default="INFO", choices=levels)
    parser.add_argument("--log-level-stdout", default=None, choices=levels)
    parser.add_argument("--log-level-stderr", default="WARNING", choices=levels)
    parser.add_argument(
        "--csv",
        type=utils.path_or_url,
        required=True,
        nargs="+",
        help="Provide the CSV to be copied with the hyperapi.",
    )
    parser.add_argument(
        "--table-def",
        type=Path,
        required=True,
        help="Provide the path to the table-definition file for the csv.",
    )
    dest_help = (
        "Optionally provide the destination path for hyper, the default appends .hyper"
        " to the csv's path"
    )
    parser.add_argument("--dest", type=Path, required=False, help=dest_help)
    parser.add_argument(
        "--header",
        action="store_true",
        required=False,
        help="Specify if there is a header in your csv.",
    )
    parser.add_argument(
        "--delimiter",
        type=literal,
        default=",",
        required=False,
        help="Specify the delimiter in your csv.",
    )
    parser.add_argument(
        "--quote",
        type=str,
        default='"',
        required=False,
        help="Specify the quotation character in your csv.",
    )
    parser.add_argument(
        "--null",
        type=str,
        default="",
        required=False,
        help="Specify the value representing null entries in your csv.",
    )
    parser.add_argument(
        "--encoding",
        type=str,
        default="utf-8",
        required=False,
        help="Specify the encoding type of your csv.",
    )
    return parser.parse_args(args)


def main(args):
    try:
        args = _parse_args(args)
        logs.config_logs(args.log_level, args.log_level_stdout, args.log_level_stderr)
        args.csv = [utils.try_unzip(csv) for csv in args.csv]
        table_definition = hyper.load_table_def(args.table_def)
        hyper.copy_csv_to_hyper(
            args.dest,
            args.csv,
            table_definition,
            delimiter=args.delimiter,
            header=args.header,
            quote=args.quote,
            null=args.null,
            encoding=args.encoding,
        )
    except Exception as e:
        log.critical("Uncaught exception", exc_info=e)


def entry_point():
    main(sys.argv[1:])


if __name__ == "__main__":
    entry_point()
