from __future__ import annotations

import subprocess
import sys
import shutil
import os
from subprocess import run
from typing import Optional

import typer
from honcho.manager import Manager
from rich import print
from rich.prompt import Prompt
from typer import Typer

from vanty.constants import env_template
from vanty.config import config

app = Typer(
    name="dev",
    help="Development commands for initializing the project,"
    " running the app, run migrations, etc.",
    no_args_is_help=True,
)


@app.command()
def docs():
    """Open the docs in browser"""
    print("[green] Opening The Starter Kit docs")
    typer.launch("https://www.advantch.com/docs/")


@app.command()
def create_env():
    """
    Check if .env file is available if not create.
    """
    env_exists = os.path.exists(".env")
    example_env_exits = os.path.exists(".env-example")
    print("[green] Checking for .env file[/green]...")
    if not env_exists:
        create_env = Prompt.ask(
            "[green]It seems you have not created a .env file yet. "
            "Would you like to create one from the default template? (y/n) [/green]"
        )

        if create_env.lower() in ["y", "yes"]:
            # copy .env-example to .env
            if example_env_exits:
                shutil.copy("env-example", ".env")
            else:
                # make a new .env file from template
                # write from envtemplate string
                with open(".env", "w") as f:
                    f.write(env_template)
            print("Env file created successfully!")
        else:
            print(
                "You will have to create a new .env file "
                "manually to run the containers."
            )

    else:
        print("[green] .env file already exists. Exiting![/green]")


@app.command()
def init():
    """Builds the docker stack"""
    try:
        run(["docker-compose", "build"])
        run(["pnpm", "install"])
        print("[green] Project initialized successfully [/green]")
        # check if env file available
        create_env()
        print("[green] Run `vanty dev migrate` to run database migrations [/green]")
        print("[green] Run `vanty dev start` to run the project. [/green]")

        print(
            "[green] Run `vanty dev create-superuser`"
            " to create a new superuser [/green]"
        )

    except subprocess.CalledProcessError as e:
        print(e.output)
        raise e


@app.command()
def build_container(container: str):
    """Rebuilds a docker container"""
    try:
        run(["docker-compose", "build", container])
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise e


@app.command()
def start():
    """
    Starts the docker stack.
    Uses honcho to run the separate processes.
    Runs:
    - docker-compose up
    - vite dev port 5173
    - vite ssr port 13714
    """
    print("[green] Starting the app...")
    manager = Manager()
    try:
        manager.add_process("docker stack", "docker-compose up")
        # v14.0 issue, with running vite in docker
        package_manager = config.get("package_manager", "pnpm")
        manager.add_process("vite dev", f"{package_manager} run dev")
        if config.get("ssr_enabled", False):
            manager.add_process("vite ssr", "node ./assets/frontend/server.js")
        manager.loop()
        sys.exit(manager.returncode)
    except KeyboardInterrupt:
        print("Stopping the app...")
    except subprocess.CalledProcessError as e:
        print(e)


@app.command()
def migrate(options: Optional[str] = None):
    """
    Runs migrations in docker
    Assumes you are running the project in docker containers.
    """
    commands = [
        "docker-compose",
        "run",
        "--rm",
        "django",
        "python",
        "manage.py",
        "migrate",
    ]
    if options:
        # parse options
        options = options.split(" ")
        commands += options
    try:
        run(commands)
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise e


@app.command()
def make_migrations(options: Optional[str] = None):
    """
    Create migrations.
    Assumes you are running the project in docker containers.
    """
    commands = [
        "docker-compose",
        "run",
        "--rm",
        "django",
        "python",
        "manage.py",
        "makemigrations",
    ]

    if options:
        # parse options
        options = options.split(" ")
        commands += options
    try:
        run(commands)
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise e


@app.command()
def create_superuser():
    """
    Creates a verified superuser.
    This extends the default django command to create a verified superuser.
    """
    email = typer.prompt("What is the email of the superuser?")
    try:
        run(
            [
                "docker-compose",
                "run",
                "--rm",
                "django",
                "python",
                "manage.py",
                "create_verified_superuser",
                email,
            ]
        )
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise e


@app.command()
def stripe_cli(
    url: str = "http://localhost:8000/billing/webhooks/",
):
    """
    Connect to Stripe CLI.
    By default, it will forward events to the local dev server. on
    http://localhost:8000/billing/webhooks/
    """
    print("[green] Opening Stripe CLI")
    # check if stripe cli is installed
    try:
        run(["stripe", "version"])
    except FileNotFoundError:
        print("[red] Stripe CLI is not installed. Please install it first.")
        print("[yellow] https://stripe.com/docs/stripe-cli#install")
        return
    commands = [
        "stripe",
        "listen",
        "--forward-to",
        url,
    ]
    run(commands)


@app.command()
def run_tests(app: str = None, file: str = None):
    """
    Runs tests for a specific Django app and file.
    """
    fstring = None
    if file and file.endswith(".py"):
        file = file[:-3]
    if app and file:
        fstring = f"apps/{app}/tests/{file}.py" if app and file else ""
    elif app:
        fstring = f"apps/{app}/tests/"
        
    if fstring:
        print(f"[green] Running tests for {fstring}")
    else:
        print("[green] Running all tests")

    # errors will not be raised as they are handled by pytest
    try:
        commands = [
                "docker-compose",
                "run",
                "--rm",
                "django",
                "pytest",
            ]
        if fstring:
            commands.append(fstring)
        subprocess.run(commands, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[red] Tests failed with error: {e}")
        # do not raise error as it is handled by pytest
    except Exception as e:
        print(f"[red] Tests failed. Error: {e}")


@app.command()
def copy_statics():
    """Copies static files to the static directory"""
    print("[green] Copying static files")
    try:
        subprocess.run(
            [
                "docker-compose",
                "run",
                "--rm",
                "django",
                "python",
                "manage.py",
                "collectstatic",
                "--noinput",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[red] Copying static files failed with error: {e}")
        raise e


@app.command()
def run_admin(command: str):
    """Run django admin command"""
    print(f"[green] Running your django admin command: {command}")
    try:
        subprocess.run(
            [
                "docker-compose",
                "run",
                "--rm",
                "django",
                "python",
                "manage.py",
                command,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[red] Running django admin command failed with error: {e}")
        raise e
