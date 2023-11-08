#!/usr/bin/python3
#
# Mounting a set of bind mounts at startup on a Linux machine. Mainly written for Synology
# machines.
import sys
import os
from pathlib import Path
import json
import logging
import subprocess
import typing
from io import StringIO

DRYRUN = bool(os.getenv("DRYRUN", ""))
logprefix = ""
if DRYRUN:
    logprefix = "[DRYRUN] "
logging.basicConfig(level=logging.INFO, format=logprefix + "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
if DRYRUN:
    logging.info("Running in dryrun mode")

default_config = """
{
    "/volume1/homes": "/home",
    "/volume1/dropbox_sandip/photos_backup/photos": "/volume1/photos"
}
"""
mountpoint = "/home/linuxbrew/.linuxbrew/bin/mountpoint"


def load_config(config_path: typing.Union[str, typing.TextIO]):
    """
    >>> from io import StringIO
    >>> data = StringIO(default_config)
    >>> sorted(load_config(data).keys())
    ['/volume1/dropbox_sandip/photos_backup/photos', '/volume1/homes']
    """
    if isinstance(config_path, str):
        data = Path(config_path).read_text()
    else:
        data = config_path.read()
    return json.loads(data)


def mount(config: dict):
    for src, dst in config.items():
        try:
            # create mount point if necessary
            if not os.path.exists(dst):
                logging.info("Creating mount point %s", dst)
                if not DRYRUN:
                    Path(dst).mkdir(exist_ok=True)
            if os.path.exists(mountpoint) and os.access(mountpoint, os.X_OK):
                rc = subprocess.call(f"{mountpoint} -q {dst}", shell=True)
                if rc == 0:
                    logging.info("Skipping mounting '%s' to '%s' as '%s' is already a mountpoint", src, dst, dst)
                    continue
            logging.info("Mounting '%s' to '%s'", src, dst)
            if not DRYRUN:
                subprocess.check_output(f"/bin/mount --bind {src} {dst}", shell=True)
        except Exception as e:
            logging.error("Could not mount '%s' to '%s': %s", src, dst, e)


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            data = StringIO(default_config)
            config = load_config(data)
        else:
            config = load_config(sys.argv[1])
    except Exception as e:
        logging.error("Could not load config file %s: %s", sys.argv[1], e)
        sys.exit(1)
    mount(config)
