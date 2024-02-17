import re
import subprocess
import tempfile
from pathlib import Path
from typing import Annotated, List, Optional

from airfold_common.format import ChFormat, Format
from airfold_common.project import (
    LocalFile,
    ProjectFile,
    dump_project_files,
    find_project_files,
    get_local_files,
    load_files,
)
from typer import Context

from airfold_cli import app
from airfold_cli.api import AirfoldApi
from airfold_cli.models import Config
from airfold_cli.options import PathArgument, with_global_options
from airfold_cli.root import catch_airfold_error
from airfold_cli.tui.diff import render_diff
from airfold_cli.utils import load_config, normalize_path_args


def _git(cwd: Path, *args: str, quiet: bool = False) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        stderr=subprocess.DEVNULL if quiet else None,
    )


def _git_diff(dir_a: str, dir_b: str) -> str:
    diff_result: str = ""
    # `--no-index` implies `--exit-code`, need to catch exception
    try:
        diff_result = _git(Path(dir_a), "diff", "--no-index", dir_a, dir_b)
    except subprocess.CalledProcessError as e:
        if e.returncode != 1:
            raise e
        diff_result = e.output
    return diff_result


@app.command("diff")
@catch_airfold_error()
@with_global_options
def diff(
    ctx: Context,
    path: Annotated[Optional[List[str]], PathArgument] = None,
):
    """Diff between local and remote objects.
    \f

    Args:
        ctx: Typer context
        path: path to local object file(s), ('-' will read objects from stdin)
    """
    app.apply_options(ctx)
    config: Config = load_config()
    api = AirfoldApi(config.key, config.endpoint)

    args = normalize_path_args(path)
    paths: list[Path] = find_project_files(args)
    files = load_files(paths)
    formatter: Format = ChFormat()
    normalized_files = [ProjectFile(name=file.name, data=formatter.normalize(file.data, file.name)) for file in files]
    local_files = get_local_files(formatter, normalized_files)

    pulled_files = api.pull()
    pulled_local_files: List[LocalFile] = get_local_files(formatter, pulled_files)

    with tempfile.TemporaryDirectory() as local_files_tmp_dir:
        dump_project_files(local_files, local_files_tmp_dir)
        with tempfile.TemporaryDirectory() as pulled_local_files_tmp_dir:
            dump_project_files(pulled_local_files, pulled_local_files_tmp_dir)
            diff_result = _git_diff(pulled_local_files_tmp_dir, local_files_tmp_dir)
            render_diff(Path(local_files_tmp_dir), re.sub(r"\/tmp\/[^\/]+", "", diff_result), console=app.console)
