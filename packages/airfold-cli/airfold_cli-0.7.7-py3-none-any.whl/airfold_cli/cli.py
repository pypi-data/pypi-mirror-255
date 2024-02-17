from typing import Optional

import rich
import typer
from airfold_common.log import set_verbosity
from rich.console import Console

from airfold_cli.options import GlobalOptions
from airfold_cli.tui.theme import MONOKAI_THEME


class AirfoldTyper(typer.Typer):
    def __init__(
        self,
        *args,
        console: Optional[Console] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.console: Console = console or self._get_console(GlobalOptions())

    def apply_options(self, ctx: typer.Context):
        options = get_global_options(ctx)
        if options.prompt != self.console.is_interactive:
            self.console = self._get_console(options)

        set_verbosity(options.verbose)

    @staticmethod
    def _get_console(options: GlobalOptions) -> Console:
        return rich.console.Console(
            highlight=False,
            color_system="auto",
            theme=MONOKAI_THEME,
            force_interactive=options.prompt,
            soft_wrap=True,  # make this configurable when needed
        )

    def is_interactive(self):
        """Check if the console is interactive."""
        return self.console.is_interactive

    def exit_with_error(self, message, code=1, **kwargs):
        """
        Print an error message and exit with a non-zero code
        """
        if message:
            self.print_error(message, **kwargs)
        raise typer.Exit(code)

    def exit_with_success(self, message, **kwargs):
        """
        Print a success message and exit with a zero code
        """
        if message:
            self.print_success(message, **kwargs)
        raise typer.Exit(0)

    def print_warning(self, message, **kwargs):
        """
        Print a warning message
        """
        kwargs.setdefault("style", "warning")
        self.console.print(f":warning: [bold]WARNING:[/] {message}", **kwargs)

    def print_error(self, message, **kwargs):
        """
        Print an error message
        """
        kwargs.setdefault("style", "error")
        self.console.print(f":x: [bold]ERROR:[/] {message}", **kwargs)

    def print_info(self, message, **kwargs):
        """
        Print a tip message
        """
        kwargs.setdefault("style", "info")
        self.console.print(f":bulb: {message}", **kwargs)

    def print_success(self, message, **kwargs):
        """
        Print a success message
        """
        kwargs.setdefault("style", "success")
        self.console.print(f":heavy_check_mark: {message}", **kwargs)


def get_global_options(
    ctx: typer.Context,
):
    """Get global options."""
    if not hasattr(ctx, "global_options"):
        ctx.global_options = GlobalOptions()  # type: ignore
    ctx.global_options.update_from_dict(ctx.params)  # type: ignore
    return ctx.global_options  # type: ignore
