import rich
import typer

from vanty._client import Client
from vanty.config import config

app = typer.Typer(name="project", help="Manage project files", no_args_is_help=True)


@app.command(help="Downloads project files from advantch.com.")
def download(project_id=None):
    """
    Download project files from advantch.com.
    :return:
    """

    token_id = config.get("token_id")
    if token_id is None:
        rich.print(
            "[red]Please run `vanty auth set <license-token>` to set your token.[/red]"
        )
        raise typer.Exit(code=1)

    rich.print("[green]Downloading project files...[/green]")
    Client().download(project_id=project_id)


@app.command(help="Print current configuration.")
def print_config():
    """
    Print current configuration.
    :return:
    """
    rich.print("[green]Current configuration:[/green]")
    rich.print(config)
