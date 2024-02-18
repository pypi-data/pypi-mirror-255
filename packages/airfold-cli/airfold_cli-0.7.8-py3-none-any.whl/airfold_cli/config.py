import os
from typing import Optional, Union

from rich.console import Console
from typer import Context

from airfold_cli.api import AIRFOLD_API_URL, AirfoldApi
from airfold_cli.error import AirfoldError, APIError
from airfold_cli.models import Config, Project, ProjectProfile, UserProfile
from airfold_cli.options import with_global_options
from airfold_cli.prompts import prompt_api_key
from airfold_cli.root import app, catch_airfold_error
from airfold_cli.utils import load_config, save_config


def do_config(
    console: Console,
) -> None:
    ok = False
    identity: Optional[Union[UserProfile, ProjectProfile]] = None
    api_key: str = ""
    try:
        config = load_config()
        endpoint = config.endpoint
    except AirfoldError:
        endpoint = os.environ.get("AIRFOLD_API_URL", AIRFOLD_API_URL)
    console.print(f"[green]Configuring for API URL: {endpoint}[/green]")
    while not ok:
        try:
            api_key = prompt_api_key(console)
            identity = AirfoldApi(api_key, endpoint).get_identity()
            if isinstance(identity, UserProfile):
                console.print(f"[yellow]User-scoped API key used, please use workspace-scoped key[/yellow]")
                continue
            ok = True
        except APIError as e:
            console.print(
                f"[red]Authenticating with API key failed ({str(e)}), " "please check the key content/validity[/red]"
            )

    assert identity is not None

    api = AirfoldApi(api_key=api_key, endpoint=endpoint)
    org_id: str = ""
    proj_id: str = ""
    if isinstance(identity, UserProfile):
        org_id = identity.organizations[0].id
        res = api.list_projects()
        projects: list[Project] = []
        if res.ok:
            projects.extend([Project(**data) for data in res.json()])
        assert len(projects) > 0
        proj_id = projects[0].id
    else:
        org_id = identity.org_id
        proj_id = identity.project_id

    path_to_config = save_config(Config(key=api_key, endpoint=api.endpoint, org_id=org_id, proj_id=proj_id))
    console.print(f"\n:rocket: config successfully set up!")
    console.print(f"You can manually modify it in: [cyan]'{path_to_config}'[/cyan]")


@app.command("config")
@catch_airfold_error()
@with_global_options
def configure(
    ctx: Context,
) -> None:
    """Configure Airfold CLI.
    \f

    Args:
        ctx: Typer context
    """
    app.apply_options(ctx)

    if not app.is_interactive():
        raise AirfoldError("Cannot run config in non-interactive mode.")

    do_config(app.console)
