import json
from typing import Annotated, Any, Optional

from airfold_common.format import ChFormat, Format
from airfold_common.plan import print_plan
from airfold_common.project import ProjectFile, dump_yaml
from airfold_common.utils import find_files, is_path_stream
from rich.progress import TaskID
from rich.syntax import Syntax
from typer import Argument, Context

from airfold_cli import app
from airfold_cli.api import AirfoldApi
from airfold_cli.cli import AirfoldTyper
from airfold_cli.models import Config, SchemaFormat, SourceInfo
from airfold_cli.options import (
    DryRunOption,
    ForceOption,
    PathOrURL,
    SourceNameArgument,
    with_global_options,
)
from airfold_cli.root import catch_airfold_error
from airfold_cli.tui.progress import IngestProgress
from airfold_cli.tui.syntax import get_syntax_theme
from airfold_cli.tui.table import print_table
from airfold_cli.utils import (
    dump_json,
    get_file_name,
    get_file_size,
    get_file_type,
    is_url,
    load_config,
    load_data_file,
)

source_app = AirfoldTyper(
    name="source",
    help="Source commands.",
)

app.add_typer(source_app)


@source_app.command("delete")
@catch_airfold_error()
@with_global_options
def delete(
    ctx: Context,
    name: Annotated[str, SourceNameArgument],
    dry_run: Annotated[bool, DryRunOption] = False,
    force: Annotated[bool, ForceOption] = False,
) -> None:
    """Delete source.
    \f

    Args:
        ctx: Typer context
        name: source name
        dry_run: show plan without executing it
        force: force delete/overwrite even if data will be lost

    """
    source_app.apply_options(ctx)

    config: Config = load_config()
    api = AirfoldApi(config.key, config.endpoint)
    commands = api.source_delete(name=name, dry_run=dry_run, force=force)
    print_plan(commands, console=source_app.console)


@source_app.command("ls")
@catch_airfold_error()
@with_global_options
def ls(ctx: Context) -> None:
    """List sources.
    \f

    Args:
        ctx: Typer context

    """
    source_app.apply_options(ctx)

    config: Config = load_config()
    api = AirfoldApi(config.key, config.endpoint)
    sources_info: list[SourceInfo] = api.list_sources()

    if not sources_info:
        if source_app.console.is_interactive:
            source_app.console.print("\t[magenta]NO SOURCES[/magenta]")
        return

    data: list[dict] = [pipe_info.dict(humanize=True) for pipe_info in sources_info]
    if source_app.console.is_interactive:
        columns = {
            "Name": "name",
            "Rows": "rows",
            "Bytes": "bytes",
            "Errors": "errors",
            "Created": "created",
            "Updated": "updated",
        }
        print_table(source_app.console, columns, data=data, title=f"{len(sources_info)} sources")
    else:
        for source_info in sources_info:
            app.console.print(dump_json(source_info.dict()))


# @source_app.command("rename")
@catch_airfold_error()
@with_global_options
def rename(
    ctx: Context,
    name: Annotated[str, SourceNameArgument],
    new_name: Annotated[str, Argument(help="New source name")],
    dry_run: Annotated[bool, DryRunOption] = False,
    force: Annotated[bool, ForceOption] = False,
) -> None:
    """Rename source.
    \f

    Args:
        ctx: Typer context
        name: source name
        new_name: new source name
        dry_run: show plan without executing it
        force: force delete/overwrite even if data will be lost

    """
    source_app.apply_options(ctx)

    config: Config = load_config()
    api = AirfoldApi(config.key, config.endpoint)
    commands = api.rename_source(name=name, new_name=new_name, dry_run=dry_run, force=force)
    print_plan(commands, console=source_app.console)


@source_app.command("append")
@catch_airfold_error()
@with_global_options
def append(
    ctx: Context,
    name: Annotated[str, SourceNameArgument],
    path: Annotated[list[str], PathOrURL],
) -> None:
    """Append data to source.
    \f

    Args:
        ctx: Typer context
        name: source name
        path: path to local file(s) or URL(s)

    """
    source_app.apply_options(ctx)

    config: Config = load_config()
    api = AirfoldApi(config.key, config.endpoint)

    paths: list[str] = []

    for p in list(set(path)):
        if is_url(p):
            paths.append(p)
        else:
            paths.extend([str(f) for f in find_files(p)])

    with IngestProgress() as progress:
        total_task = progress.add_task("Ingesting...", total=len(paths), progress_type="overall")
        for path_or_url in paths:
            if is_path_stream(path_or_url):
                source_app.print_warning(f"Cannot append data from stdin: {path_or_url}. Skipping.")
                continue

            file_type: Optional[str] = get_file_type(path_or_url)
            if not file_type:
                source_app.print_warning(f"Failed to detect file type for: {path_or_url}. Skipping.")
                continue

            ingest_task: TaskID = progress.add_task(
                f"",
                path_or_url=path_or_url,
                total=get_file_size(path_or_url),
                start=True,
                progress_type="ingest",
            )

            for chunk in load_data_file(path_or_url, file_type, chunk_size=200):
                events_chunk: list[str] = list(chunk.apply(lambda x: x.to_json(), axis=1))
                api.send_events(src_name=name, events=events_chunk)
                progress.update(ingest_task, advance=sum([len(e.encode("utf-8")) for e in events_chunk]))
            progress.update(total_task, advance=1)


@source_app.command("create")
@catch_airfold_error()
@with_global_options
def create(
    ctx: Context,
    path: Annotated[list[str], PathOrURL],
) -> None:
    """Create source.
    \f

    Args:
        ctx: Typer context
        path: path to local file(s) or URL(s)


    """
    source_app.apply_options(ctx)

    config: Config = load_config()
    api = AirfoldApi(config.key, config.endpoint)

    paths: list[str] = []

    for p in list(set(path)):
        if is_url(p):
            paths.append(p)
        else:
            paths.extend([str(f) for f in find_files(p)])

    source_schema: dict[str, Any] = {}
    for path_or_url in paths:
        if is_path_stream(path_or_url):
            source_app.print_warning(f"Cannot get data from stdin: {path_or_url}. Skipping.")
            continue

        file_type: Optional[str] = get_file_type(path_or_url)
        if not file_type:
            source_app.print_warning(f"Failed to detect file type for: {path_or_url}. Skipping.")
            continue

        for chunk in load_data_file(path_or_url, file_type, chunk_size=50):
            events_chunk: list[str] = list(chunk.apply(lambda x: x.to_json(), axis=1))
            source_schema = api.infer_schema(events=events_chunk, schema_format=SchemaFormat.YAML)
            if not source_schema.get("name"):
                source_schema["name"] = get_file_name(path_or_url)
            break
        break

    source_data: str = dump_yaml(source_schema.copy(), remove_names=True)
    app.console.print(Syntax(source_data, "yaml", theme=get_syntax_theme()))
    file_name: str = f'{source_schema["name"]}.yaml'
    open(f"{file_name}", "w").write(source_data)
    if source_app.is_interactive():
        source_app.print_success(f"Source saved to: {file_name}")
