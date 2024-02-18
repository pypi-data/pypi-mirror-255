from typing import Annotated, Dict, Optional

from airfold_common.project import is_path_stream
from rich.syntax import Syntax
from typer import Context

from airfold_cli.api import AirfoldApi
from airfold_cli.models import Config
from airfold_cli.options import OutputPathArgument, with_global_options
from airfold_cli.root import app, catch_airfold_error
from airfold_cli.tui.syntax import get_syntax_theme
from airfold_cli.utils import dump_json, load_config


def graph_all(config: Config | None = None) -> Dict:
    api = AirfoldApi.from_config(config or load_config())
    return api.graph()


@app.command("graph")
@catch_airfold_error()
@with_global_options
def graph(ctx: Context, path: Annotated[Optional[str], OutputPathArgument] = None) -> None:
    """Dump graph of runtime objects in json format to file or stdout.
    \f

    Args:
        ctx: Typer context
        path: file to dump into, ('-' will dump objects to stdout)

    """
    app.apply_options(ctx)

    json_data = graph_all()
    if path and not is_path_stream(path):
        with open(path, "w") as file:
            file.write(dump_json(json_data))
    else:
        app.console.print(Syntax(dump_json(json_data), "json", theme=get_syntax_theme()))
