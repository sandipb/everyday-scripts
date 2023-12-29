# Common library for all python code

import signal
import sys

# import subprocess
# import shlex
import logging

# import json
# import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from colorama import Fore, init

__all__ = [
    "colorama_init",
    "msg_info",
    "msg_error",
    "ask",
    "sig_quit_clean",
    "logging_init",
    "chunks",
]

urllib3.disable_warnings(InsecureRequestWarning)


def colorama_init():
    init(autoreset=True)


def msg_info(msg):
    print(Fore.BLUE + "*** " + msg)


def msg_error(msg):
    print(Fore.RED + "!!! " + msg)


def ask(msg: str) -> str:
    """
    Ask a yes/no question and return the user's choice.

    :param msg: The message to display to the user.
    :type msg: str
    :return: The user's choice, which can be 'y', 'n', or 'q'.
    :rtype: str
    """
    while True:
        choice = input(msg + "(y/n/q)").lower().strip()
        if choice and choice[0] in ("y", "n", "q"):
            choice = choice[0]
            break
        msg_error("Invalid input")
    return choice


def sig_quit_clean():
    """
    Sets up a signal handler for SIGINT (Ctrl+C) to gracefully exit the program.

    This function registers a signal handler for SIGINT that prints a message and exits the program
    when the user presses Ctrl+C.

    :return: None
    """

    def quit(sig, frame):
        print()
        logging.info("Interrupted. Exiting.")
        sys.exit(1)

    signal.signal(signal.SIGINT, quit)


def logging_init(verbose: bool = False, log_level: int | None = None):
    """
    Initialize the logging configuration.

    :param verbose: Whether to enable verbose logging. Default is False.
    :type verbose: bool
    :param log_level: The log level to set. If None, it will be set to DEBUG if verbose is True, else INFO.
    :type log_level: int or None
    """
    if log_level is None:
        log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format="[%(levelname)s] %(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(CustomFormatter())
    logging.getLogger().handlers = [handler]


# https://stackoverflow.com/a/56944256
class CustomFormatter(logging.Formatter):
    green = "\x1b[32m"
    grey = "\x1b[90m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    msg_format = "%(asctime)s [%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + msg_format + reset,
        logging.INFO: green + msg_format + reset,
        logging.WARNING: yellow + msg_format + reset,
        logging.ERROR: red + msg_format + reset,
        logging.CRITICAL: bold_red + msg_format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def chunks(ar, length):
    """Chop up list ar into lists of at max length l

    >>> list(map(lambda x: list(x), chunks(range(10), 3)))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    for idx in range(0, len(ar), length):
        yield ar[idx : idx + length]


if __name__ == "__main__":
    import doctest

    doctest.testmod()
