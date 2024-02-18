import rich


class CliPrinter:
    """
    Printing pretty logs. For logging to file, use logging module
    """

    def __init__(self, name=None):
        self.name = name or "vanty: log"

    def debug(self, msg):
        rich.print(
            f"[bold blue]{self.name}[/bold blue] -"
            f" [bold green]DEBUG[/bold green] - {msg}"
        )

    def info(self, msg):
        rich.print(
            f"[bold blue]{self.name}[/bold blue] -"
            f" [bold green]INFO[/bold green] - {msg}"
        )

    def warning(self, msg):
        rich.print(
            f"[bold blue]{self.name}[/bold blue] -"
            f" [bold green]WARNING[/bold green] - {msg}"
        )

    def error(self, msg):
        rich.print(
            f"[bold blue]{self.name}[/bold blue] -"
            f" [bold green]ERROR[/bold green] - {msg}"
        )


vlog = CliPrinter()
