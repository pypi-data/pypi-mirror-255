import logging
import os
import yaml

from pathlib import Path
from rich.console import Console
from typing import Dict, List, Optional

from . import constants
from .file_utils import check_infile_status, check_outfile_status


error_console = Console(stderr=True, style="bold red")

console = Console()



class Manager:
    """Class for managing a placeholder substitutions and line insertions."""

    def __init__(self, **kwargs):
        """Constructor for Manager."""
        self.template_file = kwargs.get("template_file", None)
        self.key_val_file = kwargs.get("key_val_file", None)
        self.outdir = kwargs.get("outdir", None)
        self.outfile = kwargs.get("outfile", None)
        self.verbose = kwargs.get("verbose", constants.DEFAULT_VERBOSE)

        self._found_keys_lookup = {}
        self._found_keys_ctr = 0

        logging.info(f"Instantiated Manager in file '{os.path.abspath(__file__)}'")

    def _get_lookup(self, key_val_file: str) -> Dict[str, str]:
        """Derive the lookup from the key-value pairs YAML file.

        Args:
            key_val_file (str): The key-value pairs YAML file.

        Returns:
            Dict[str, str]: The lookup.
        """
        logging.info(f"Will load contents of key-value file '{key_val_file}'")
        lookup = yaml.safe_load(Path(key_val_file).read_text())
        return lookup

    def make_substitutions(self, key_val_file: Optional[str], template_file: Optional[str], outfile: Optional[str]) -> None:
        """Perform the placeholder substitutions using the template file.

        Args:
            key_val_file (str): The path of the file that contains the key-value pairs.
            template_file (str): The path of the template file that contains the placeholders.
            outfile (Optional[str]): The path of the output file to be created.
        """
        if outfile is None:
            outfile = self.outfile
            if outfile is None:
                raise ValueError("outfile must be specified")

        if template_file is None:
            template_file = self.template_file
            if template_file is None:
                raise ValueError("template_file must be specified")

        check_infile_status(template_file, "tt")
        check_infile_status(key_val_file, "yaml")

        check_outfile_status(outfile)
        lookup: Dict[str, List[str]] = self._get_lookup(key_val_file)

        # Some values will themselves have some placholder values
        # that will need to be substituted with the placeholders that
        # are keys.
        for key in lookup:
            for current_key, val in lookup.items():
                if key == current_key:
                    continue
                if key in val:
                    lookup[current_key] = val.replace(key, lookup[key])


        with open(template_file, "r") as tf:
            with open(outfile, "w") as of:
                for line in tf:
                    for key, value in lookup.items():
                        if key not in self._found_keys_lookup:
                            self._found_keys_lookup[key] = 0
                        if key in line:
                            line = line.replace(key, value)
                            self._found_keys_lookup[key] += 1
                            self._found_keys_ctr += 1

                    of.write(line)

        console.print(f"Created output file '{outfile}'")
        logging.info(f"Created output file '{outfile}'")

        self._report_substitution_status(lookup)

    def _report_substitution_status(self, lookup: Dict[str, int]) -> None:
        """Print the found keys lookup.

        Args:
            lookup (Dict[str, int]): The lookup of found keys.
        """
        if self._found_keys_ctr > 0:
            console.print("Found keys lookup:")
            logging.info("Found keys lookup:")

            for key, count in self._found_keys_lookup.items():
                console.print(f"Found placeholder '{key}' on '{count}' lines in template file '{self.template_file}'")
                logging.info(f"Found placeholder '{key}' on '{count}' lines in template file '{self.template_file}'")
        else:
            console.print(f"None of the placeholders were substituted in template file '{self.template_file}' given the key-value pairs defined in file '{self.key_val_file}'")
            logging.warning(f"None of the placeholders were substituted in template file '{self.template_file}' given the key-value pairs defined in file '{self.key_val_file}'")

        for key in lookup:
            if key not in self._found_keys_lookup:
                error_console.print(f"Did not find placeholder '{key}' in template file '{self.template_file}'")
                logging.warning(f"Did not find placeholder '{key}' in template file '{self.template_file}'")


    def insert_lines(
        self,
        key_val_file: str,
        template_file: str,
        outfile: Optional[str]) -> None:
        """Perform the placeholder substitutions using the template file.

        Args:
            key_val_file (str): The path of the file that contains the key-value pairs.
            template_file (str): The path of the template file that contains the placeholders.
            outfile (Optional[str]): The path of the output file to be created.
        """
        if outfile is None:
            outfile = self.outfile
            if outfile is None:
                raise ValueError("outfile must be specified")

        check_infile_status(template_file, "tt")
        check_infile_status(key_val_file, "yaml")

        check_outfile_status(outfile)

        lookup: Dict[str, List[str]] = self._get_lookup(key_val_file)

        with open(self.template_file, "r") as template_file:
            with open(outfile, "w") as output_file:
                for line in template_file:
                    for key, outlines in lookup.items():
                        if key in line:
                            self._found_keys_lookup[key] += 1
                            self._found_keys_ctr += 1
                            for outline in outlines:
                                output_file.write(f"{outline}\n")

                    output_file.write(line)

        console.print(f"Created output file '{outfile}'")
        logging.info(f"Created output file '{outfile}'")

        self._report_substitution_status(lookup)
