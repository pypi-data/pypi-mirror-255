import importlib.util
import json
import os.path
import sys
from pathlib import Path
from time import sleep, time
from typing import Annotated, Callable

from airfold_common.error import AirfoldError
from rich.syntax import Syntax
from typer import Argument, Context, Option

from airfold_cli import app
from airfold_cli.api import AirfoldApi
from airfold_cli.cli import AirfoldTyper
from airfold_cli.models import Config
from airfold_cli.options import with_global_options
from airfold_cli.root import catch_airfold_error
from airfold_cli.tui.syntax import get_syntax_theme
from airfold_cli.utils import load_config

CLI_DIR = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../airfold_cli")
TEMPLATES = {"http_log": f"{CLI_DIR}/events/http_log.py"}

gen_app = AirfoldTyper(
    name="generate",
    help="Generate events.",
)

app.add_typer(gen_app)


def load_gen_func(templ_path: str) -> Callable[[], str]:
    file_path = Path(templ_path)
    module_name = file_path.stem
    spec = importlib.util.spec_from_file_location(module_name, templ_path)
    assert spec
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore
    return getattr(module, "generate")


@gen_app.command("events")
@catch_airfold_error()
@with_global_options
def generate_events(
    ctx: Context,
    templ_name: Annotated[str, Argument(help="Event template name or path to file.", show_default=False)],
    src_name: Annotated[str, Option("--send", help="Source to send events to.")] = "",
    limit: Annotated[int, Option("--limit", help="Limit amount of events.")] = -1,
    eps: Annotated[int, Option("--eps", help="Send events per second.")] = 1,
) -> None:
    gen_app.apply_options(ctx)
    config: Config = load_config()

    if not os.path.exists(templ_name):
        file_path = TEMPLATES.get(templ_name)
    else:
        file_path = templ_name
    if not file_path:
        raise AirfoldError(f"Template not found: {templ_name}")

    generate = load_gen_func(file_path)
    event = generate()
    if not src_name:
        app.console.print(Syntax(json.dumps(json.loads(event), indent=2), "json", theme=get_syntax_theme()))
        return
    api = AirfoldApi(config.key, config.endpoint)
    delay = 1.0 / eps
    emitted = 0
    try:
        while limit < 0 or emitted < limit:
            start = time()
            res = api.send_events(src_name, [event])
            app.console.print(res)
            emitted += 1
            wait = max(0.0, delay - time() + start)
            sleep(wait)
            event = generate()
    except KeyboardInterrupt:
        app.console.print(f"\nSent {emitted} events, shutting down")
