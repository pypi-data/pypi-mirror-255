from rich.console import Console
from rich.prompt import Prompt


def prompt(msg: str, **kwargs):
    """Prompt the user for input with consistent styling"""
    return Prompt.ask(f"[bold][green]?[/] {msg}[/]", **kwargs)


def prompt_api_key(console: Console) -> str:
    api_key = prompt(f"Api key", console=console)
    return api_key


def prompt_overwrite_local_file(path: str, console: Console) -> bool:
    return (
        prompt(
            f"File already exists {path}. Overwrite it with formatted version?",
            console=console,
            choices=["y", "n"],
        )
        == "y"
    )


def prompt_store_file(default_path: str, console: Console) -> str:
    return prompt(f"File is not stored. Enter path:", default=default_path, console=console)
