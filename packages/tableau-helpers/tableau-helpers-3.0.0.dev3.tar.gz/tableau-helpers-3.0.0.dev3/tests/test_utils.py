from pathlib import Path
from typing import Optional

def textfile_diff(filepath_a: Path, filepath_b: Path) -> Optional[str]:
    """
    returns True when no differences are found.
    """
    with open(filepath_a, 'r') as file_a, open(filepath_b, 'r') as file_b:
        does_not_match = any([line != file_b.readline() for line in file_a])
        if does_not_match is True:
            return False
        file_b_at_eof = (file_b.read(1) == '')
    return file_b_at_eof
