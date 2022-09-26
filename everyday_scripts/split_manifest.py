#!/usr/bin/env python3

import sys
import os
import argparse
import logging
import yaml


def split_manifest(fs, dir, clean_dir):
    "Read an input stream fs and output split yamls to dir"
    if clean_dir:
        logging.info("Cleaning up output dir")
        for f in os.listdir(dir):
            path = os.path.join(dir, f)
            os.remove(path)
            logging.info("Deleted %s", path)
    for doc in yaml.safe_load_all(fs):
        if doc:
            if doc.get("kind"):
                try:
                    kind = doc["kind"]
                    name = doc["metadata"]["name"]
                    path = os.path.join(dir, f"{kind.lower()}-{name.lower()}.yaml")
                    with open(path, "w") as f:
                        yaml.dump(doc, f, indent=2)
                    logging.info("Wrote %s", path)
                except IndexError as e:
                    logging.warning(f"Skipping doc: {e}")


def main():
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--manifest", help="path to a manifest file. If not given will read from stdin")
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        default="output",
        help="Directory where all the individual yaml files will be dumped. Existing files will be overwritten!",
    )
    parser.add_argument(
        "-c", "--clean-output", dest="clean_output", default=False, help="Clean output dir before generating yaml"
    )
    args = parser.parse_args()
    input_file = sys.stdin
    if args.manifest:
        input_file = open(args.manifest)
    if not os.path.exists(args.output_dir):
        logging.fatal(f"Directory {args.output_dir} does not exist")
        sys.exit(1)
    elif not os.path.isdir(args.output_dir):
        logging.fatal(f"Directory {args.output_dir} is not a directory")
        sys.exit(1)
    split_manifest(input_file, args.output_dir, args.clean_output)
    if args.manifest:
        input_file.close()


if __name__ == "__main__":
    main()
