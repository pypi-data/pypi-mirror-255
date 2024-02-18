import logging
from typing import Optional
import sys


def config_logs(
    level: int = logging.WARNING,
    stdout_level: Optional[int] = None,
    stderr_level: Optional[int] = logging.WARNING,
    handlers: list = [],
):
    if stdout_level is not None:
        stdout = logging.StreamHandler(sys.stdout)
        stdout.setLevel(stdout_level)
        handlers.append(stdout)
    if stderr_level is not None:
        stderr = logging.StreamHandler(sys.stderr)
        stderr.setLevel(stderr_level)
        handlers.append(stderr)
    logging.basicConfig(handlers=handlers, force=True)
