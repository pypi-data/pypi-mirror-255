from enum import Enum
from pathlib import Path
from typing import Annotated, List, Optional, Union

import yaml
from airfold_common.format import ChFormat, Format
from airfold_common.project import (
    TRAILING_SPACE_RE,
    ProjectFile,
    create_file,
    dump_yaml,
    find_project_files,
    is_path_stream,
)
from deepdiff import DeepDiff  # type: ignore
from rich.console import Console, ConsoleOptions, RenderResult
from rich.markup import escape
from rich.rule import Rule
from rich.syntax import Syntax
from typer import Context

from airfold_cli.error import AirfoldError
from airfold_cli.options import (
    DryRunOption,
    OverwriteFileOption,
    PathArgumentNoStream,
    with_global_options,
)
from airfold_cli.prompts import prompt_overwrite_local_file
from airfold_cli.root import app, catch_airfold_error
from airfold_cli.tui.syntax import get_syntax_theme
from airfold_cli.utils import normalize_path_args


class FormatStatus(str, Enum):
    FIXED = "Fixed"
    REFORMATTED = "Reformatted"
    UNCHANGED = "Unchanged"


class FileHeader:
    def __init__(self, status: FormatStatus, file_path: Union[str, Path]):
        self.file_path = file_path
        self.status = status
        if status == FormatStatus.FIXED:
            self.path_prefix = f"[bold green]{status.value} [/]"
        elif status == FormatStatus.REFORMATTED:
            self.path_prefix = f"[bold blue]{status.value} [/]"
        else:
            self.path_prefix = ""

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Rule(
            f"{self.path_prefix}[b]{escape(str(self.file_path))}[/]",
            style="border",
            characters="▁",
        )


class UnchangedFileBody:
    """Represents a file that was not changed."""

    def __init__(self, file_path: Union[str, Path]):
        self.file = file_path

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Rule(characters="╲", style="hatched")
        yield Rule(" [blue]File was not changed ", characters="╲", style="hatched")
        yield Rule(characters="╲", style="hatched")
        yield Rule(style="border", characters="▔")


def load_file_strip_space(path: Path):
    res: list[ProjectFile] = []
    data = open(path).read()
    data = TRAILING_SPACE_RE.sub("", data)
    docs = list(yaml.safe_load_all(data))
    if len(docs) > 1:
        for doc in docs:
            res.append(create_file(doc, str(path)))
    elif len(docs) == 1:
        res.append(ProjectFile(name=path.stem, data=docs[0]))
    return res


@app.command("fmt")
@catch_airfold_error()
@with_global_options
def fmt(
    ctx: Context,
    path: Annotated[Optional[List[str]], PathArgumentNoStream] = None,
    dry_run: Annotated[bool, DryRunOption] = False,
    overwrite: Annotated[bool, OverwriteFileOption] = False,
) -> None:
    """Format local object files.
    \f

    Args:
        ctx: Typer context
        path: path to local object file(s)
        dry_run: print formatted files to stdout without saving them
        overwrite: overwrite existing files
    """
    app.apply_options(ctx)

    if not app.is_interactive() and not dry_run and not overwrite:
        raise AirfoldError("Use --overwrite in non-interactive mode")

    if dry_run and overwrite:
        app.ui.print_warning("--dry-run and --overwrite are mutually exclusive, ignoring --overwrite")

    args = normalize_path_args(path)
    paths: list[Path] = find_project_files(args)
    formatter: Format = ChFormat()

    for local_file in paths:
        # ignore stdin
        if is_path_stream(local_file):
            app.ui.print_warning(f"Reading from stdin is not allowed. Skipped.")
            continue

        project_files: list[ProjectFile] = load_file_strip_space(local_file)
        format_status: FormatStatus = FormatStatus.UNCHANGED
        formatted_files: list[ProjectFile] = []

        for pf in project_files:
            normalized_file: ProjectFile = ProjectFile(
                name=pf.name, data=formatter.normalize(pf.data.copy(), pf.name), pulled=pf.pulled
            )
            ddiff = DeepDiff(pf.data, normalized_file.data, exclude_paths=["name"])
            if ddiff:
                format_status = FormatStatus.FIXED
            formatted_files.append(normalized_file)

        yaml_data: str = dump_yaml([ff.data.copy() for ff in formatted_files], remove_names=len(formatted_files) == 1)
        if app.is_terminal():
            if format_status == FormatStatus.UNCHANGED:
                with open(local_file, "r") as f:
                    raw_data = f.read()
                    if raw_data != yaml_data:
                        format_status = FormatStatus.REFORMATTED

            app.console.print(FileHeader(format_status, local_file))
            if format_status == FormatStatus.UNCHANGED:
                app.console.print(UnchangedFileBody(local_file))
                continue
            else:
                app.console.print(Syntax(yaml_data, "yaml", theme=get_syntax_theme()))
        else:
            app.console.print("---\n" + dump_yaml([ff.data for ff in formatted_files], remove_names=False))

        if dry_run:
            continue

        store: bool = True
        if not overwrite:
            store = prompt_overwrite_local_file(str(local_file), console=app.console)

        if not store:
            continue

        with open(local_file, "w") as f:
            f.write(yaml_data)
