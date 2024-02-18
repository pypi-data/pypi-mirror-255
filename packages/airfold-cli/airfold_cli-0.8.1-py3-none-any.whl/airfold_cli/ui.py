from typing import Optional

from rich import box
from rich.console import Console
from rich.table import Table


class UI:
    """Terminal UI object"""

    def __init__(self, console: Console) -> None:
        self._console = console

    @property
    def console(self) -> Console:
        return self._console

    def print_table(self, columns: dict[str, str], data: list[dict], title: Optional[str] = None) -> None:
        """Constructs a table to display a list of items.

        Args:
            columns: The table columns.
            data: The list of items to display.
            title: The title of the table.
        """

        title = f"[bold]{title}" if title else None

        table = Table(title=title, show_lines=True)

        for column in columns.keys():
            table.add_column(column)

        for item in data:
            row_values = []
            for column in columns.values():
                row_values.append(str(item[column]))
            table.add_row(*row_values)

        table.box = box.SQUARE_DOUBLE_HEAD
        self.console.print(table)

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
