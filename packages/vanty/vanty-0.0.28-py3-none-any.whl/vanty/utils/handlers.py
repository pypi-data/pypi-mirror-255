import rich


def process_output(line, stdin, process):
    """
    SH callback for processing output from a process
    """
    rich.print(line, end="")
    if "ERROR" in line:
        process.kill()
        return True
