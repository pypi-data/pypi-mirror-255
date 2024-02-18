from __future__ import annotations

import rich

from vanty.cli import app


def main():
    app()


if __name__ == "__main__":
    rich.print("[bold green]Vanty[/bold green] - [bold blue]CLI[/bold blue]")
    main()
