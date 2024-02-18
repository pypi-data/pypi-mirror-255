import rich
import typer
from vanty.config import config

app = typer.Typer(name="auth", help="Manage tokens.", no_args_is_help=True)


@app.command(
    help="Echo configuration settings. "
)
def show_config():
    user_config = config()
    # echo the user config
    typer.echo(rich.box.Box(str(user_config), title="User Config"))
