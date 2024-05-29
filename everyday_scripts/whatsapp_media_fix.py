"""Whatsapp images/videos when downloaded have the timestamp when it was 
"""
import argparse
import os
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(message)s")


def get_file_modification_time(file_path: str) -> str:
    """Get the file modification time in the format YYYY:MM:DD HH:MM:SS"""
    mod_time = os.path.getmtime(file_path)
    return datetime.fromtimestamp(mod_time).strftime("%Y:%m:%d %H:%M:%S")


def update_timestamp(file_path: str, dryrun: bool) -> None:
    """Update the timestamp of the file to the file modification time"""
    new_timestamp = get_file_modification_time(file_path)
    logging.info(f"Processing file: {file_path}")

    # Command to read current timestamp
    read_cmd = ["exiftool", "-DateTimeOriginal", file_path]
    result = subprocess.run(read_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    original_timestamp = result.stdout.strip() or "No original timestamp found"

    logging.info(f"Original Timestamp: {original_timestamp}")
    logging.info(f"New Timestamp: {new_timestamp}")

    if not dryrun:
        # Command to update timestamp
        update_cmd = ["exiftool", f"-DateTimeOriginal={new_timestamp}", "-overwrite_original", file_path]
        subprocess.run(update_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("Timestamp updated.")
    else:
        logging.info("Dry run: Timestamp not updated.")


def process_files(paths: list[str], dryrun: bool) -> None:
    for path in paths:
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    update_timestamp(os.path.join(root, file), dryrun)
        else:
            update_timestamp(path, dryrun)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update media file timestamps to match file modification time.")
    parser.add_argument("paths", nargs="+", help="Directory or list of files to process")
    parser.add_argument("--dryrun", "-d", action="store_true", help="Show what would be done without actual update")
    args = parser.parse_args()

    process_files(args.paths, args.dryrun)
