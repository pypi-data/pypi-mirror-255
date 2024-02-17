from typing import Annotated, Generator, Optional

from airfold_common.format import ChFormat, Format
from airfold_common.plan import print_plan
from airfold_common.project import ProjectFile
from cachetools import TTLCache, cached
from rich.syntax import Syntax
from typer import Argument, Context

from airfold_cli import app
from airfold_cli.api import AirfoldApi
from airfold_cli.cli import AirfoldTyper
from airfold_cli.models import (
    Config,
    NamedParam,
    OutputDataFormat,
    PipeInfo,
    PipeInfoStatus,
)
from airfold_cli.options import (
    DryRunOption,
    ForceOption,
    OutputDataFormatOption,
    PipeParamOption,
    with_global_options,
)
from airfold_cli.root import catch_airfold_error
from airfold_cli.tui.syntax import get_syntax_theme
from airfold_cli.tui.table import print_table
from airfold_cli.utils import decode_short_uuid, dump_json, load_config

pipe_app = AirfoldTyper(
    name="pipe",
    help="Pipe commands.",
)

app.add_typer(pipe_app)


@cached(cache=TTLCache(maxsize=10000, ttl=5))
def get_pipe_names() -> list[str]:
    config: Config = load_config()
    api = AirfoldApi(config.key, config.endpoint)
    files = api.pull()
    formatter: Format = ChFormat()
    pipes: list[ProjectFile] = list(filter(lambda f: formatter.is_pipe(f.data), files))
    return [pipe.name for pipe in pipes]


def pipe_name_completion(cur: str) -> Generator[str, None, None]:
    """Pipe name completion."""
    try:
        pipe_names: list[str] = get_pipe_names()
        yield from filter(lambda name: name.startswith(cur), pipe_names) if cur else pipe_names
    except Exception as e:
        pass


@pipe_app.command("delete")
@catch_airfold_error()
@with_global_options
def delete(
    ctx: Context,
    name: Annotated[str, Argument(help="Pipe name", autocompletion=pipe_name_completion)],
    dry_run: Annotated[bool, DryRunOption] = False,
    force: Annotated[bool, ForceOption] = False,
) -> None:
    """Delete pipe.
    \f

    Args:
        ctx: Typer context
        name: pipe name
        dry_run: show plan without executing it
        force: force delete/overwrite even if data will be lost

    """
    pipe_app.apply_options(ctx)

    config: Config = load_config()
    api = AirfoldApi(config.key, config.endpoint)
    commands = api.pipe_delete(name=name, dry_run=dry_run, force=force)
    print_plan(commands, console=pipe_app.console)


@pipe_app.command("ls")
@catch_airfold_error()
@with_global_options
def ls(ctx: Context) -> None:
    """List pipes.
    \f

    Args:
        ctx: Typer context

    """
    pipe_app.apply_options(ctx)

    config: Config = load_config()
    api = AirfoldApi(config.key, config.endpoint)

    pipes_info: list[PipeInfo] = api.list_pipes()

    if not pipes_info:
        if pipe_app.console.is_interactive:
            pipe_app.console.print("\t[magenta]NO PIPES[/magenta]")
        return

    data: list[dict] = [pipe_info.dict(humanize=True) for pipe_info in pipes_info]
    if pipe_app.console.is_interactive:
        columns = {
            "Name": "name",
            "Status": "status",
            "Created": "created",
            "Updated": "updated",
        }
        print_table(pipe_app.console, columns, data=data, title=f"{len(pipes_info)} pipes")
    else:
        for pipe_info in pipes_info:
            app.console.print(dump_json(pipe_info.dict()))


@pipe_app.command("query")
@catch_airfold_error()
@with_global_options
def query(
    ctx: Context,
    name: Annotated[str, Argument(help="Pipe name", autocompletion=pipe_name_completion)],
    format: Annotated[OutputDataFormat, OutputDataFormatOption] = OutputDataFormat.NDJSON,
    params: Annotated[Optional[list[NamedParam]], PipeParamOption] = None,
) -> None:
    """Query pipe data.
    \f

    Args:
        ctx: Typer context
        name: pipe name
        format: output data format
        params: pipe parameter(key=value)

    """
    pipe_app.apply_options(ctx)

    config: Config = load_config()
    api = AirfoldApi(config.key, config.endpoint)

    jsons = api.pipe_get_data(
        name=name, output_format=format, params={p.name: p.value for p in params} if params else None
    )

    for json_data in jsons:
        app.console.print(Syntax(dump_json(json_data), "json", theme=get_syntax_theme()))


# @pipe_app.command("rename")
@catch_airfold_error()
@with_global_options
def rename(
    ctx: Context,
    name: Annotated[str, Argument(help="Pipe name", autocompletion=pipe_name_completion)],
    new_name: Annotated[str, Argument(help="New pipe name")],
    dry_run: Annotated[bool, DryRunOption] = False,
    force: Annotated[bool, ForceOption] = False,
) -> None:
    """Rename pipe.
    \f

    Args:
        ctx: Typer context
        name: pipe name
        new_name: new pipe name
        dry_run: show plan without executing it
        force: force delete/overwrite even if data will be lost
    """
    pipe_app.apply_options(ctx)

    config: Config = load_config()
    api = AirfoldApi(config.key, config.endpoint)
    commands = api.rename_pipe(name=name, new_name=new_name, dry_run=dry_run, force=force)
    print_plan(commands, console=pipe_app.console)
