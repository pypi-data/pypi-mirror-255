#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import click

from rich.console import Console
from datetime import datetime
from typing import List

DEFAULT_PROJECT = "simple-template-toolkit"

EXECUTABLES = [
    "insert-lines",
    "make-substitutions",
]

DEFAULT_ALIAS_PREFIX = "jj"

error_console = Console(stderr=True, style="bold red")

console = Console()


def create_aliases_file(wrapper_scripts: List[str], outdir: str, prefix: str = DEFAULT_ALIAS_PREFIX) -> None:
    """Create a file with aliases for the wrapper scripts.

    Args:
        wrapper_scripts (List[str]): list of wrapper scripts
        outdir (str): output directory
    """
    outfile = os.path.join(outdir, f"{DEFAULT_PROJECT}-aliases.txt")

    with open(outfile, 'w') as of:
        of.write(f"## method-created: {os.path.abspath(__file__)}\n")
        of.write(f"## date-created: {str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))}\n")
        of.write(f"## created-by: {os.environ.get('USER')}\n")
        for wrapper_script in wrapper_scripts:
            alias = os.path.basename(wrapper_script).replace(".sh", "")
            line = f"alias {prefix}-{alias}='bash {wrapper_script}'"
            of.write(f"{line}\n")

    print(f"Wrote aliases file '{outfile}'")


def create_wrapper_script(executable: str, activate_script: str, outdir: str) -> str:
    wrapper_shell_script = os.path.join(outdir, f"{executable}.sh")

    with open(wrapper_shell_script, "w") as of:
        of.write("#!/bin/bash\n")
        of.write(f"## method-created: {os.path.abspath(__file__)}\n")
        of.write(f"## date-created: {str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))}\n")
        of.write(f"## created-by: {os.environ.get('USER')}\n")
        of.write(f"source {activate_script}\n")
        of.write(f"{executable} \"$@\"")

    print(f"Wrote wrapper shell script '{wrapper_shell_script}'")
    return wrapper_shell_script


@click.command()
@click.option(
    "--alias-prefix",
    type=str,
    help=f"Optional: The prefix to be applied to the aliases - default is '{DEFAULT_ALIAS_PREFIX}'",
)
def main(alias_prefix: str):
    """Create wrapper shell scripts and aliases."""
    error_ctr = 0

    if error_ctr > 0:
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    if alias_prefix is None:
        alias_prefix = DEFAULT_ALIAS_PREFIX
        console.print(f"[bold yellow]--alias-prefix was not specified and therefore was set to '{alias_prefix}'[/]")

    wrapper_scripts = []

    # Directory where the wrapper scripts will be created
    wrapper_scripts_dir = os.getcwd()
    make_script_dir = os.path.dirname(__file__)

    activate_script = os.path.join(
        make_script_dir,
        "..",
        "..",
        "..",
        "..",
        "bin",
        "activate"
    )

    if not os.path.exists(activate_script):
        raise Exception(f"Activate script '{activate_script}' does not exist")
    print(f"activate_script: {activate_script}")

    for executable in EXECUTABLES:
        wrapper_script = create_wrapper_script(executable, activate_script, wrapper_scripts_dir)
        wrapper_scripts.append(wrapper_script)

    create_aliases_file(wrapper_scripts, os.getcwd(), alias_prefix)

    console.print(f"[bold green]Execution of {os.path.abspath(__file__)} completed[/]")


if __name__ == "__main__":
    main()
