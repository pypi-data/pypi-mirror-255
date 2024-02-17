#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Insert values into file with placeholders."""
import os
import sys
import click
import logging
import pathlib

from rich.console import Console
from typing import Optional

from . import constants
from .click_helper import validate_verbose
from .console_helper import print_red, print_yellow, print_green
from .file_utils import check_infile_status
from .manager import Manager as TemplateToolkitManager


error_console = Console(stderr=True, style="bold red")

console = Console()


@click.command()
@click.option('--infile', type=click.Path(exists=True), help="Required: The input file that contains key-value pairs to drive the placeholder substitution.")
@click.option('--logfile', help="Optional: The log file.")
@click.option('--outdir', help=f"Optional: The directory where the log file and output file will be written - default is '{constants.DEFAULT_OUTDIR}'.")
@click.option('--outfile', help="Optional: The output file.")
@click.option('--template_file', type=click.Path(exists=True), help="Required: The input template file that contains placeholders to be substituted.")
@click.option('--verbose', is_flag=True, help=f"Optional: Will print more info to STDOUT - default is '{constants.DEFAULT_VERBOSE}'.", callback=validate_verbose)
def main(infile: str, logfile: Optional[str], outdir: Optional[str], outfile: Optional[str], template_file: str, verbose: Optional[bool]):
    """Perform placeholder substitutions."""
    error_ctr = 0

    if infile is None:
        print_red("--infile was not specified")
        error_ctr += 1

    if template_file is None:
        print_red("--template_file was not specified")
        error_ctr += 1

    if error_ctr > 0:
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    check_infile_status(template_file, "tt")
    check_infile_status(infile, "yaml")

    if outdir is None:
        outdir = constants.DEFAULT_OUTDIR
        print_yellow(f"--outdir was not specified and therefore was set to '{outdir}'")

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
        print_yellow(f"Created output directory '{outdir}'")

    if logfile is None:
        logfile = os.path.join(
            outdir,
            os.path.splitext(os.path.basename(__file__))[0] + '.log'
        )
        print_yellow(f"--logfile was not specified and therefore was set to '{logfile}'")

    logging.basicConfig(
        filename=logfile,
        format=constants.DEFAULT_LOGGING_FORMAT,
        level=constants.DEFAULT_LOGGING_LEVEL,
    )

    manager = TemplateToolkitManager(
        verbose=verbose
    )

    manager.make_substitutions(
        key_val_file=infile,
        template_file=template_file,
        outfile=outfile,
    )

    if verbose:
        console.print(f"The log file is '{logfile}'")
        print_green(f"Execution of '{os.path.abspath(__file__)}' completed")


if __name__ == "__main__":
    main()
