# Common library for all python code

import signal
import sys
import subprocess
import shlex
import logging
import json
import requests
import urllib3

from colorama import Fore, Style, init

__all__ = [
    "colorama_init", "msg_info", "msg_error", "ask", 
    "sig_quit_clean", "logging_init",  "chunks",
]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def colorama_init():
    init(autoreset=True)

def msg_info(msg):
    print(Fore.BLUE + "*** " + msg)

def msg_error(msg):
    print(Fore.RED + "!!! " + msg)

def ask(msg: str) -> str:
    while True:
        choice = input(msg + "(y/n/q)").lower().strip()
        if choice and choice[0] in ("y", "n", "q"):
            choice = choice[0]
            break
        msg_error("Invalid input")
    return choice

def sig_quit_clean():
    def quit(sig, frame):
        print()
        logging.info("Interrupted. Exiting.")
        sys.exit(1)
    signal.signal(signal.SIGINT, quit)

def logging_init(verbose:bool = False):
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


def chunks(ar, l):
    """Chop up list ar into lists of at max length l
    
    >>> list(map(lambda x: list(x), chunks(range(10), 3)))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    for idx in range(0, len(ar), l):
        yield ar[idx:idx+l]

if __name__ == "__main__":
    import doctest
    doctest.testmod()