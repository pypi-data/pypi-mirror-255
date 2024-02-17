import hashlib
import logging
import os
import pathlib
import platform
import string
import sys

from datetime import datetime
from typing import Optional
from rich.console import Console

from .console_helper import print_yellow


error_console = Console(stderr=True, style="bold red")


def calculate_md5(file_path: str) -> str:
    """Calculate the md5 checksum for the specified file.

    Args:
        file_path (str): the file for which the md5 checksum will be calculated

    Returns:
        str: the calculated md5 checksum
    """
    md5_hash = hashlib.md5()
    logging.info(f"Will attempt to calculate the MD5 checksum for file '{file_path}'")

    with open(file_path, "rb") as file:
        # Read the file in chunks to efficiently handle large files
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)

    return md5_hash.hexdigest()


def get_file_creation_date(file_path: str) -> datetime:
    """Determine the creation date for the specified file.

    Args:
        file_path (str): the absolute path of the file

    Returns:
        datetime: the date the file was created according to the operating system
    """
    if platform.system() == "Windows":
        # On Windows, use creation time
        creation_time = os.path.getctime(file_path)
    else:
        # On Unix-based systems, use birth time (creation time)
        # Note: Not all file systems support birth time, and it might not be available on some systems.
        stat_info = os.stat(file_path)
        creation_time = stat_info.st_mtime

    # Convert the timestamp to a readable date
    creation_date = datetime.fromtimestamp(creation_time)

    return creation_date


def check_infile_status(infile: str, extension: Optional[str] = None) -> None:
    """Check if the file exists, if it is a regular file and whether it has
    content.

    Args:
        infile (str): the file to be checked

    Raises:
        None
    """

    error_ctr = 0

    if infile is None or infile == "":
        error_console.print(f"'{infile}' is not defined")
        error_ctr += 1
    else:
        if not os.path.exists(infile):
            error_ctr += 1
            error_console.print(f"'{infile}' does not exist")
        else:
            if not os.path.isfile(infile):
                error_ctr += 1
                error_console.print(f"'{infile}' is not a regular file")
            if os.stat(infile).st_size == 0:
                error_console.print(f"'{infile}' has no content")
                error_ctr += 1
            if extension is not None and not infile.endswith(extension):
                error_console.print(
                    f"'{infile}' does not have filename extension '{extension}'"
                )
                error_ctr += 1

    if error_ctr > 0:
        error_console.print(f"Detected problems with input file '{infile}'")
        sys.exit(1)


def check_indir_status(indir: str = None) -> None:
    """Check if the directory exists and is a regular directory.

    Args:
        indir (str): the directory to be checked
    """
    error_ctr = 0

    if indir is None or indir == '':
        error_console.print(f"'{indir}' is not defined")
        error_ctr += 1
    else:
        if not os.path.exists(indir):
            error_ctr += 1
            error_console.print(f"directory '{indir}' does not exist")
        else:
            if not os.path.isdir(indir):
                error_ctr += 1
                error_console.print(f"'{indir}' is not a regular directory")

    if error_ctr > 0:
        error_console.print(f"Detected problems with input directory '{indir}'")
        sys.exit(1)


def get_file_size(file_path: str) -> int:
    """Get the size of the specified file in bytes.

    Args:
        file_path (str): The path to the file to be checked.

    Raises:
        Exception: If the file does not exist.

    Returns:
        int: The size of the file in bytes.
    """
    # Check if the file exists
    if os.path.exists(file_path):
        # Get the file size in bytes
        file_size = os.path.getsize(file_path)
        return file_size
    else:
        raise Exception(f"The file '{file_path}' does not exist.")


def get_line_count(file_path: str) -> int:
    """Get the number of lines in the specified file.

    Args:
        file_path (str): The path to the file to be checked.

    Returns:
        int: The number of lines in the file.
    """
    # if is_binary_file(file_path):
    #     print(f"Unable to get line count for binary file '{file_path}'")
    #     return None
    try:
        with open(file_path, 'r') as file:
            line_count = sum(1 for line in file)
        return line_count
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def is_binary_file(file_path: str, block_size: int = 1024) -> bool:
    """Check if the specified file is a binary file.

    Args:
        file_path (str): The path to the file to be checked.
        block_size (int, optional): The block size. Defaults to 1024.

    Returns:
        bool: If the file is binary, returns True. Otherwise, returns False.
    """
    try:
        with open(file_path, 'rb') as file:
            block = file.read(block_size)
            if not block:  # Empty file
                return False

            # Check for the presence of null bytes (indicative of binary files)
            if b'\x00' in block:
                return True

            # Check for a significant number of non-printable ASCII characters
            text_characters = set(string.printable)
            if not all(byte in text_characters or byte == b'\n' for byte in block):
                return True

            return False  # File is likely text

    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_file_list_from_directory(indir: str = None, extension: str = None) -> list:
    """Get the list of files in the specified directory
    :param indir: {str} - the directory to search for files
    :param extension: {str} - the file extension to filter on
    :returns file_list: {list} - the list of files found in the directory
    """
    if extension is None:
        logging.info(f"Going to search for files in directory '{indir}'")
    else:
        logging.info(f"Going to search for files with extension '{extension}' in directory '{indir}'")

    file_list = []
    for dirpath, dirnames, filenames in os.walk(indir):
        if 'venv' in dirpath:
            logging.info(f"Going to ignore files in directory '{dirpath}'")
            continue
        for name in filenames:
            file_path = os.path.normpath(os.path.join(dirpath, name))
            if os.path.isfile(file_path):
                if extension is not None:
                    if file_path.endswith(f'.{extension}'):
                        file_list.append(file_path)
                else:
                    file_list.append(file_path)

    return file_list

def check_outdir_status(outdir: str) -> None:

    if os.path.exists(outdir):
        timestamp = str(datetime.now().strftime("%Y-%m-%d-%H%M%S"))
        bakdir = os.path.join(outdir, f".{timestamp}.bak")
        os.rename(outdir, bakdir)
        logging.info(f"Renamed directory '{outdir}' to '{bakdir}'")
        print_yellow(f"Renamed directory '{outdir}' to '{bakdir}'")

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory '{outdir}'")
        print_yellow(f"Created directory '{outdir}'")

def check_outfile_status(outfile: str) -> None:

    if os.path.exists(outfile):
        timestamp = str(datetime.now().strftime("%Y-%m-%d-%H%M%S"))
        bakfile = os.path.join(outfile, f".{timestamp}.bak")
        os.rename(outfile, bakfile)
        logging.info(f"Moved output file '{outfile}' to '{bakfile}'")
        print_yellow(f"Move file '{outfile}' to '{bakfile}'")
