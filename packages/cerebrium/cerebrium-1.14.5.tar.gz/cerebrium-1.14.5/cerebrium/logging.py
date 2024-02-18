from typing import List, Union
import re
import os
import sys
from yaspin.core import Yaspin  # type: ignore
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text
import logging
from termcolor import colored

# Create a console object
console = Console(highlight=False)

# Setup logging globally
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Include timestamp with milliseconds
    datefmt="%Y-%m-%d %H:%M:%S.%f",
    handlers=[
        RichHandler(
            console=console,
            rich_tracebacks=False,
            show_path=False,
            show_level=False,
            show_time=True,
            markup=True,
            highlighter=None,  # Explicitly disable syntax highlighting for log messages
        )
    ],
)

logger = logging.getLogger("rich")

error_messages = {
    "disk quota exceeded": "💾 You've run out of space in your /persistent-storage. \n"
    "You can add more by running the command: `cerebrium storage increase-capacity <the_amount_in_GB>`"
}  # Error messages to check for


def log_formatted_response(log_line: str):
    ##This function removes timestamps and prints based on the color passed (ie: INFO, ERROR etc)

    pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,9}Z(?: \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}: WARNING\/MainProcess\])?|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,9}Z \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+"
    log_line = re.sub(pattern, "", log_line)
    log_line = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+", "", log_line)
    log_line = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z", "", log_line)

    if not log_line.strip():
        return  # Skip logging if the line is empty or whitespace

    # Check if the log line contains "disk quota exceeded"
    if "disk quota exceeded" in log_line.lower():
        if error_msg := error_messages.get("disk quota exceeded"):
            # Format and print the error message
            formatted_msg = f"\n🚨 Build failed! \n" f"{error_msg}"
            logger.error(f"[red]{formatted_msg}[/red]")
            return

    colourise_log(log_line)
    if log_line.lower() in error_messages:
        logger.error(log_line)


def colourise_log(log: str):
    # Adjust regex to capture the log message after the delimiter
    # Use \s* to match any amount of whitespace
    if re.search(r"\|\s*INFO\s*\|", log):
        log = re.sub(r"\|\s*INFO\s*\|(.*)", "", log)
        logger.info(log.strip())
        return
    elif re.search(r"\|\|\s*DEBUG\s*\|\|", log):
        if os.getenv("ENV") != "prod":  # we only log debut on dev/local
            log = re.sub(r"\|\|\s*DEBUG\s*\|\|(.*)\|\|\s*END DEBUG\s*\|\|", r"\1", log)
            logger.info(f"[yellow]{log.strip()}[/yellow]")
            return
    elif re.search(r"\|\|\s*ERROR\s*\|\|", log) or "ERROR:" in log:
        log = re.sub(r"\|\|\s*ERROR\s*\|\|(.*)\|\|\s*END ERROR\s*\|\|", r"\1", log)
        log = log.replace("ERROR:", "").strip()
        logger.error(f"[red]{log.strip()}[/red]")
        return

    # logger.info(escaped_message)
    logger.info(log.strip())


def cerebrium_log(
    message: str,
    prefix: str = "",
    level: str = "INFO",
    attrs: List[str] = [],
    color: str = "",
    end: str = "\n",
    spinner: Union[Yaspin, None] = None,
):
    """User friendly coloured logging

    Args:
        message (str): Error message to be displayed
        prefix (str): Prefix to be displayed. Defaults to empty.
        level (str): Log level. Defaults to "INFO".
        attrs (list, optional): Attributes for colored printing. Defaults to None.
        color (str, optional): Color to print in. Defaults depending on log level.
        end (str, optional): End character. Defaults to "\n".
    """

    level = level.upper()
    default_prefixes = {"INFO": "Info: ", "WARNING": "Warning: ", "ERROR": "Error: "}
    default_colors = {"INFO": None, "WARNING": "yellow", "ERROR": "red"}
    prefix = prefix or default_prefixes.get(level, "")

    # None is default for unused variables to avoid breaking termcolor
    log_color = color or default_colors.get(level, "")
    prefix = colored(f"{prefix}", color=log_color, attrs=["bold"])
    message = colored(f"{message}", color=log_color, attrs=attrs)

    # spinners don't print nicely and keep spinning on errors. Use them if they're there
    if spinner:
        spinner.write(prefix)  # type: ignore
        spinner.text = ""
        if level == "ERROR":
            spinner.fail(message)
            spinner.stop()
        else:
            spinner.write(message)  # type: ignore
    else:
        print(prefix, end=end)
        print(message)

    if level == "ERROR":
        sys.exit(1)
