from __future__ import annotations

import requests
import typer
import rich

from vanty.auth import app as auth
from vanty.dev import app as dev
from vanty.project import app as project
from vanty.scaffold.startapp import app as scaffold
from vanty.admin import app as admin
from vanty.community import app as community

from importlib.metadata import distribution


def fetch_current_installed_version():
    return distribution("vanty").version


def fetch_latest_version_from_pypi():
    url = "https://pypi.org/pypi/vanty/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["info"]["version"]
    return None


def check_version():
    current_version = fetch_current_installed_version()
    latest_version = fetch_latest_version_from_pypi()
    if latest_version and current_version != latest_version:
        rich.print(
            f"[bold red]A newer version {latest_version} is available on PyPI. "
            f"You are running {current_version}.[/bold red]"
        )
    else:
        rich.print("[bold green]You are running the latest version.[/bold green]")


app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="markdown",
    help="""
    Vanty is the fastest way to launch new SaaS, AI and Internal products.

    Visit https://www.advantch.com/ for documentation and more information

    """,
)
app.add_typer(auth)
app.add_typer(dev)
app.add_typer(project)
app.add_typer(scaffold)
app.add_typer(admin)
app.add_typer(community)


@app.command()
def version():
    """Version check"""
    check_version()
