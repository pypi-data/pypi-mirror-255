import typer

app = typer.Typer(name="auth", help="Manage tokens.", no_args_is_help=True)


@app.command(
    help=(
            "Initialize a starter project. "
            "\n Options are: "
            "\n 1. django-react \n 2. django-vue"
    )
)
def init_starter(name="django"):
    """
    Fetches and initialises the starter project. Git must be installed.
    """
    # echo the user config
    typer.echo("This will git clone the starter project")
    typer.echo("Coming soon")
