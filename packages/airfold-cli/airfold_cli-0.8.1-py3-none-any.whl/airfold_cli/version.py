from typer import Exit, Option, echo


def version_callback(value: bool):
    if value:
        from importlib.metadata import version

        echo(f"Airfold CLI Version: {version('airfold-cli')}")
        raise Exit()


VersionOption: bool = Option(
    None,
    "--version",
    callback=version_callback,
    is_eager=True,
    help="Return Airfold CLI version",
)
