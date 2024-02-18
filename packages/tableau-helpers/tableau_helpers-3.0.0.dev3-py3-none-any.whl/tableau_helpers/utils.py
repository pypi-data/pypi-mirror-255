import lzma
from pathlib import Path
import shutil
import tempfile
from typing import Union
from urllib.request import urlopen

tempdir = tempfile.TemporaryDirectory()
tmppath = Path(tempdir.name)


def download_file(url: str, dir: Path = tmppath) -> Path:
    filename = url.rsplit("/", 1)[-1]
    filepath = Path(dir, filename)
    with urlopen(url) as response:
        with filepath.open(mode="w+b") as f:
            shutil.copyfileobj(response, f)
    return filepath


def try_unzip(arg: Path):
    tmp = Path(tempdir.name, arg.with_suffix("").name)
    if arg.suffix == ".xz":
        with lzma.open(arg) as decompressed:
            with tmp.open(mode="w+b") as f:
                shutil.copyfileobj(decompressed, f)
        return try_unzip(tmp)
    return arg


def path_or_url(arg: Union[Path, str]) -> Path:
    result = arg
    if isinstance(arg, Path):
        result = arg
    if isinstance(arg, str):
        if arg.startswith("https://"):
            result = download_file(url=arg)
        else:
            result = Path(arg)
    else:
        raise TypeError

    return result
