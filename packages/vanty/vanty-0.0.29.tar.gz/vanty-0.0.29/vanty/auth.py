import rich
import typer

from vanty._client import Client
from vanty.config import _store_user_config, config, user_config_path
from vanty.utils.console_printer import vlog

app = typer.Typer(name="auth", help="Manage tokens.", no_args_is_help=True)


@app.command(
    help="Set license token for connecting to advantch.com."
    "If not provided with the command, you will be prompted"
    " to enter your credentials."
)
def set(license_token: str):
    server_url = config.get("server_url")
    rich.print(f"Verifying token against [blue]{server_url}[/blue]")
    data = Client.verify(server_url, license_token)
    if data.is_valid:
        rich.print("[green]Token verified successfully[/green]")
        _store_user_config(
            {"token_id": data.token_id, "token_secret": data.token_secret}
        )
        rich.print(f"Token written to {user_config_path}")
        return data.token_id

    else:
        rich.print(
            "[red]Unable to verify invalid[/red]. "
            "Please check your license id and try again."
        )
        rich.print("If this problem persists, please contact support@advantch.com")
        return None


@app.command(help="Remove the token from the config file.")
def remove():
    _store_user_config({"token_id": None, "token_secret": None})
    vlog.info(f"Token removed from {user_config_path}")
    return None
