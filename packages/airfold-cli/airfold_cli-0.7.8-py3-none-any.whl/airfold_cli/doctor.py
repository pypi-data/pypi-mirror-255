from typing import Annotated, Optional

from airfold_common.log import log
from airfold_common.models import FixResult, FixStatus, Issue
from typer import Context

from airfold_cli import app
from airfold_cli.api import AirfoldApi
from airfold_cli.models import Config
from airfold_cli.options import FixOption, ListChecksOption, with_global_options
from airfold_cli.root import catch_airfold_error
from airfold_cli.utils import load_config


@app.command("doctor")
@catch_airfold_error()
@with_global_options
def doctor(
    ctx: Context,
    fix: Annotated[Optional[bool], FixOption] = False,
    list_checks: Annotated[Optional[bool], ListChecksOption] = False,
) -> None:
    """Check your system for potential problems.
    \f

    Args:
        ctx: Typer context
        fix: automatically fix problems
        list_checks: list available checks

    """
    app.apply_options(ctx)
    config: Config = load_config()
    api = AirfoldApi(config.key, config.endpoint)

    if list_checks:
        print_checks(api.doctor_list_checks())
        return

    issues, fix_results = api.doctor_run(fix=fix)
    print_check_results(issues)

    if fix and len(fix_results) > 0:
        print_fix_results(fix_results)


def print_checks(checks: list[str]) -> None:
    """Print available checks."""
    for check in checks:
        app.console.print(check, style="general")


def print_check_results(issues: list[Issue]):
    if len(issues) == 0:
        app.console.print("[magenta]No issues found.[/magenta]")
        return
    else:
        app.console.print(f"[red]{len(issues)}[/red][magenta] issue(s) found:[/magenta]")
        for issue in issues:
            app.console.print(f"\t- [cyan]{issue.id}[/cyan]\t{issue.description}")


def print_fix_results(fix_results: list[FixResult]):
    for fr in fix_results:
        status_fmt = (
            f"[green]{fr.status.upper()}[/green]" if fr.status == FixStatus.FIXED else f"[red]{fr.status.upper()}[/red]"
        )
        app.console.print(f"\t- [cyan]{fr.issue.id}[/cyan]\t{status_fmt}\t{fr.message if len(fr.message) > 0 else ''}")
