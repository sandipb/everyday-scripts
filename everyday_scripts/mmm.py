#!/usr/bin/env python3
#
# mmm src --images=xxx --videos=xxx
#
import argparse
import logging
import sys
import os
from datetime import timedelta
from time import perf_counter
from mimetypes import guess_type, init as mt_init, add_type
from typing import Callable, Dict, List
from xml.etree import ElementTree
from pathlib import Path
from itertools import islice
import shutil
from collections import defaultdict

import trio
import requests
import humanize

from everyday_scripts.scriptlib import *

EXTERNAL_MIMETYPE_SRC = "https://raw.githubusercontent.com/ImageMagick/ImageMagick/main/config/mime.xml"
MIME_TYPES_FN = "mime.types"
EXTRA_EXT_TYPES = {
    ".xmp": "image",  # adobe correction files
    ".dop": "image",  # dxo correction files
}
PARALLELISM = 5


class Metrics:
    moves = 0
    copies = 0
    errors = 0
    type_counts: dict = defaultdict(int)

    @classmethod
    def stats(cls):
        print("\nSTATS:")
        for attr in ["moves", "copies", "errors"]:
            print(f"  - {attr:5}\t: {cls.__dict__[attr]:5}")
        print(f"  - types\t:")
        for k in sorted(cls.type_counts.keys()):
            print(f"  \t- {k}\t: {cls.type_counts[k]:5}")


def init_mimetypes():
    search_paths = [MIME_TYPES_FN, os.path.join(str(Path(__file__).resolve().parent), MIME_TYPES_FN)]  # current dir
    for path in search_paths:
        if os.path.exists(path):
            logging.debug("Using %s for type detection", path)
            mt_init([path])
            return


def type_for_file(path: str) -> str | None:
    ftype = guess_type(path)[0]
    if ftype:
        return ftype.split("/")[0].lower()
    _, ext = os.path.splitext(path)
    if ext.lower() in EXTRA_EXT_TYPES:
        return EXTRA_EXT_TYPES[ext.lower()].lower()
    return None


def find_files(src: str, dest_map: Dict[str, str]):
    """
    Generator to find files and types

    Given a path to search, returns a list of tuple(origin_path, destination_root)
    """
    for root, _, files in os.walk(src):
        for f in files:
            full_path = os.path.join(root, f)
            ftype = type_for_file(f)
            if (ftype is not None) and (ftype in dest_map):
                final_path = replace_path(full_path, src, dest_map[ftype])
                Metrics.type_counts[ftype] += 1
                yield (full_path, final_path)
            else:
                logging.debug("Skipping file with unknown file type: %s", full_path)


async def move_a_file(src: str, dst: str, args: argparse.Namespace):
    action = "move"
    method: Callable = shutil.move
    if args.copy:
        action = "copy"
        method = shutil.copyfile
        Metrics.copies += 1
    else:
        Metrics.moves += 1

    if args.dry_run:
        print(f"[{action.upper()}]", src, "->", dst)
    else:
        if logging.getLogger().getEffectiveLevel() == logging.INFO:
            print(f"[{action.upper()}]", src, "->", dst)
        try:
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            method(src, dst)
        except Exception as e:
            logging.error("Could not %s %s -> %s: %s", action, src, dst, e)
            Metrics.errors += 1


async def move_files(src: str, dest_map: Dict[str, str], args: argparse.Namespace):
    gen = find_files(src, dest_map)
    while True:
        chunk = list(islice(gen, PARALLELISM))
        if not chunk:
            return
        async with trio.open_nursery() as nursery:
            for orig_path, final_path in chunk:
                nursery.start_soon(move_a_file, orig_path, final_path, args)


def replace_path(path: str, src: str, dst: str) -> str:
    """
    Replace the parent dir src in path with dst

    >>> replace_path("/Users/sandipb/a/b/c/nnnn/hello.txt", "/Users/sandipb/", "/usr/bin")
    '/usr/bin/a/b/c/nnnn/hello.txt'
    """
    path = str(Path(path).resolve())
    src = str(Path(src).resolve())
    relative_path = str(Path(path).relative_to(src))
    return os.path.join(dst, relative_path)


def download_mt(url=EXTERNAL_MIMETYPE_SRC):
    # Never clobber
    if os.path.exists(MIME_TYPES_FN):
        logging.fatal("Not overwriting existing '%s' file in local directory", MIME_TYPES_FN)
        sys.exit(1)

    try:
        logging.debug("Downloading reference mime types from %s", url)
        response = requests.get(url)
        response.raise_for_status()
        tree = ElementTree.fromstring(response.content)
        count = 0
        with open(MIME_TYPES_FN, "w") as fp:
            fp.write(f"# Mime types generated from {url}\n\n")
            for el in tree.findall("mime"):
                attribs = el.attrib
                if "pattern" in attribs:
                    typen = attribs["type"]
                    patn = attribs["pattern"]
                    if patn.startswith("*."):
                        patn = patn.replace("*.", "")
                    elif ("[" in patn) or ("*" in patn):
                        logging.debug("Ignoring complex pattern '%s' for '%s'", patn, typen)
                        continue
                    print(typen, patn, sep="\t\t", file=fp)
                    count += 1
        logging.info("Generated '%s' with %d entries", MIME_TYPES_FN, count)
    except Exception as e:
        logging.fatal("Could not download mime type data: %s", e)
        sys.exit(1)


def parse_destinations(dmap: List[str]) -> Dict[str, str]:
    destinations: Dict[str, str] = dict()
    for entry in dmap:
        comps = entry.split("=", 1)
        if len(comps) != 2:
            logging.fatal("Invalid destination specifier: %s", entry)
            sys.exit(1)
        tname, tdest = [t.strip() for t in comps]
        tdest = valid_dir_or_quit(tdest, f"Destination dir for {tname}")
        destinations[tname.lower()] = tdest

    return destinations


def valid_dir_or_quit(path: str, name: str) -> str:
    if not path:
        logging.fatal(f"{name} is required")
        sys.exit(1)

    rpath = str(Path(path).resolve().expanduser())
    if not os.path.isdir(rpath):
        logging.fatal(f"Invalid {name}: {rpath}")
        sys.exit(1)
    return rpath


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="List actions")
    parser.add_argument("--debug", "-d", action="store_true", help="Debug level logging")
    # parser.add_argument("--image", "-I", help="Base target directory for images")
    # parser.add_argument("--video", "-V", help="Base target directory for videos")
    parser.add_argument("--mt-download", "-m", action="store_true", help="Download mime types reference")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Dry run")
    parser.add_argument("--copy", "-c", action="store_true", help="Copy, don't move")
    parser.add_argument("src", metavar="SOURCE_DIR", help="Source directory")
    parser.add_argument("dst", metavar="DST_PATTERN", nargs="+", help="Destination patterns in TYPE:DIRECTORY format")
    args = parser.parse_args()
    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    logging_init(log_level=log_level)
    sig_quit_clean()

    if args.mt_download:
        download_mt()
        sys.exit(0)

    src = valid_dir_or_quit(args.src, "Source directory")
    destinations = parse_destinations(args.dst)
    logging.info("Moving files from '%s' using rules: %s", src, destinations)

    init_mimetypes()
    start = perf_counter()
    trio.run(move_files, src, destinations, args)
    elapsed = round(perf_counter() - start, 2)
    print(f"Operation completed in: {humanize.precisedelta(timedelta(seconds=elapsed))}")
    Metrics.stats()


if __name__ == "__main__":
    main()
