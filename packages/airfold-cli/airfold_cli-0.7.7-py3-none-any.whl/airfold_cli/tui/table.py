from typing import Optional

from rich import box
from rich.console import Console
from rich.table import Table


def print_table(console: Console, columns: dict[str, str], data: list[dict], title: Optional[str] = None) -> None:
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
    console.print(table)
