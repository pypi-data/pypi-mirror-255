"""Module for console helper functions.

Raises:
    Exception: If msg is not defined
"""
from rich.console import Console

error_console = Console(stderr=True, style="bold red")

console = Console()


def print_red(msg: str = None) -> None:
    """Print a message in red.

    Args:
        msg (str, optional): The message to be printed in red. Defaults to None.

    Raises:
        Exception: If msg is not defined
    """
    if msg is None or msg == "":
        raise Exception("msg was not defined")
    error_console.print(msg)


def print_green(msg: str = None) -> None:
    """Print a message in green.

    Args:
        msg (str, optional): The message to be printed in red. Defaults to None.

    Raises:
        Exception: If msg is not defined
    """
    if msg is None or msg == "":
        raise Exception("msg was not defined")

    console.print(f"[bold green]{msg}[/]")

def print_yellow(msg: str = None) -> None:
    """Print a message in yellow.

    Args:
        msg (str, optional): The message to be printed in red. Defaults to None.

    Raises:
        Exception: If msg is not defined
    """
    if msg is None or msg == "":
        raise Exception("msg was not defined")

    console.print(f"[bold yellow]{msg}[/]")
