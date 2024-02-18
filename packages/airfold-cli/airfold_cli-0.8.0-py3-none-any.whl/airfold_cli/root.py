from functools import wraps
from textwrap import dedent

import typer
from airfold_common.log import log
from rich.traceback import install

from airfold_cli.cli import AirfoldTyper
from airfold_cli.error import AirfoldError, ConflictError
from airfold_cli.options import with_global_options
from airfold_cli.version import VersionOption

install()

app = AirfoldTyper(no_args_is_help=True, short_help="-h", rich_markup_mode="rich")


def print_doctor_run_recommendation():
    """
    Print a recommendation to run the doctor command
    """
    return app.ui.print_info(
        dedent(
            """\
        To diagnose and identify possible issues, run :point_right: [cyan]af doctor[/cyan] :point_left:
        """
        )
    )


def catch_airfold_error():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ConflictError as e:
                log.error(e)
                app.ui.print_error(e)
                print_doctor_run_recommendation()
                app.exit_with_error("")
            except AirfoldError as e:
                log.error(e)
                app.exit_with_error(str(e))

        return wrapper

    return decorator


def is_interactive():
    """Check if the console is interactive."""
    return app.is_interactive()


@app.callback()
def default(
    version: bool = VersionOption,
) -> None:
    pass


@app.callback()
@with_global_options
def main(
    ctx: typer.Context,
    version: bool = VersionOption,
):
    app.apply_options(ctx)


def entrypoint():
    """Application entrypoint."""

    app()


if __name__ == "__main__":
    entrypoint()
