from typing import Optional

import rich
import typer
from airfold_common.log import set_verbosity
from rich.console import Console

from airfold_cli.options import GlobalOptions
from airfold_cli.tui.theme import MONOKAI_THEME
from airfold_cli.ui import UI


class AirfoldTyper(typer.Typer):
    def __init__(
        self,
        *args,
        console: Optional[Console] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.ui: UI = UI(console=console or self._get_console(GlobalOptions().prompt))

    def apply_options(self, ctx: typer.Context):
        options = get_global_options(ctx)
        if options.prompt != self.is_interactive():
            self.ui = UI(console=self._get_console(options.prompt))

        set_verbosity(options.verbose)

    @property
    def console(self):
        return self.ui.console

    @staticmethod
    def _get_console(prompt: Optional[bool] = None) -> Console:
        return rich.console.Console(
            highlight=False,
            color_system="auto",
            theme=MONOKAI_THEME,
            force_interactive=prompt,
            soft_wrap=True,  # make this configurable when needed
        )

    def is_interactive(self):
        """Check if the console is interactive."""
        return self.ui.console.is_interactive

    def is_terminal(self):
        """Check if the console is a terminal."""
        return self.ui.console.is_terminal

    def exit_with_error(self, message, code=1, **kwargs):
        """
        Print an error message and exit with a non-zero code
        """
        if message:
            self.ui.print_error(message, **kwargs)
        raise typer.Exit(code)

    def exit_with_success(self, message, **kwargs):
        """
        Print a success message and exit with a zero code
        """
        if message:
            self.ui.print_success(message, **kwargs)
        raise typer.Exit(0)


def get_global_options(
    ctx: typer.Context,
):
    """Get global options."""
    if not hasattr(ctx, "global_options"):
        ctx.global_options = GlobalOptions()  # type: ignore
    ctx.global_options.update_from_dict(ctx.params)  # type: ignore
    return ctx.global_options  # type: ignore
