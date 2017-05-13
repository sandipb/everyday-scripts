#!/usr/bin/python
"""Convert a folder of images to forced labelled images

(c) 2017, Sandip Bhattacharya. Public domain.

JPEG files need to be in format ``YYYY-... TITLE ...IGNORED.jpg``. Check the TITLE_RE to find/edit your file format

Example: ``2017-04-20 Russian Ridge OSP 12.58.17-2.jpg``


"""
from __future__ import absolute_import
from __future__ import print_function


import argparse
import logging
import os
import sys
import re
import subprocess
from multiprocessing.pool import ThreadPool as Pool
# from multiprocessing import Pool
from functools import partial
from datetime import datetime


TITLE_RE = re.compile(r'^(?P<year>\d{4})-\S+ (?P<place>.*) \S+$')
MAX_PARALLEL = 5


def jpegs_in_dir(path):
    jpeg_re = re.compile(r'\.(jpg|JPEG|jpeg|JPG)$')
    file_list = filter(lambda x: os.path.isfile(os.path.join(path, x)) and jpeg_re.search(x),
                       os.listdir(path))
    return file_list


def image_width(path):
    try:
        out_str = subprocess.check_output(["identify",  "-format", "%w", path])
        return int(out_str)
    except:
        logging.exception("Could not find image width using ImageMagick")
        raise


def label_jpeg(input, output, label, width, height):
    try:
        subprocess.check_call(["convert -background '#0008' -fill white -gravity center "
                               "-size {width}x80 caption:'{label}' '{input}' +swap -gravity South "
                               "-geometry +0-3 -composite '{output}'".format(label=label,
                                                                             input=input,
                                                                             output=output,
                                                                             width=width,
                                                                             height=height)], shell=True)
    except:
        logging.exception("Could not label image using ImageMagick")
        raise


def process_image(name, input_dir, output_dir, label_size):
    logging.info("Processing %s", name)
    full_input_name = os.path.join(input_dir, name)
    full_output_name = os.path.join(output_dir, name)
    m = TITLE_RE.search(name)
    if not m:
        logging.warn("%s: Skipping file as it doesn't match expected naming convention", name)
        return
    label = "%s, %s" % (m.group('place'), m.group('year'))
    logging.info("%s: Label will be '%s' ", name, label)
    width = image_width(full_input_name)
    logging.info("%s: Found image width to be %d", name, width)
    label_jpeg(full_input_name, full_output_name, label, width, label_size)
    logging.info("%s: Added label to image", name)


if __name__ == "__main__":
    start = datetime.now()
    logging.basicConfig(level=logging.INFO, format="%(asctime)-15s [%(levelname)s] %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    parser = argparse.ArgumentParser(description="Convert a folder of images to labeled images")
    parser.add_argument("-i", "--input-dir", required=True, help="Directory of jpegs to convert")
    parser.add_argument("-o", "--output-dir", required=True, help="Directory where labeled images will be put")
    parser.add_argument("-s", "--size", type=int, default=80, help="Height of the labels (default: %(default)s)")

    args = parser.parse_args()
    input_dir, output_dir = os.path.abspath(args.input_dir), os.path.abspath(args.output_dir)
    if input_dir == output_dir:
        logging.fatal("Input and output directory can't be the same")
        sys.exit(1)

    for d in input_dir, output_dir:
        if not (os.path.isdir(d) and os.access(d, os.W_OK | os.R_OK)):
            logging.fatal("Cannot access %s", d)
            sys.exit(1)
    logging.info("Will convert jpegs from '%s' to '%s' with label height %d", input_dir, output_dir, args.size)

    file_list = jpegs_in_dir(input_dir)
    logging.info("Found %d jpeg files", len(file_list))
    pool = Pool(processes=MAX_PARALLEL)
    # inputs = [(f, input_dir, output_dir) for f in file_list]
    # logging.info("Found %d inputs: %s", len(inputs), inputs)
    pool.map(partial(process_image, input_dir=input_dir, output_dir=output_dir, label_size=args.size), file_list)
    pool.close()
    pool.join()
    end = datetime.now()
    logging.info("Converted %d files in %s", len(file_list), end - start)
