import argparse
from datetime import timezone, datetime
import time
import os
import pytz
import shutil
import sys

DESCRIPTION = """Parse time in filename and renaming it in different format.

Example:
  $ filename_time_parse --source-format "%m%d%Y_%H%M%S" --source-zone America/Los_Angeles \\
                        --dst-format "File-%Y-%m-%d--%H-%M-%S-%Z" --dst-zone  Europe/Berlin \\
                        ~/Movies/big/01132020_162200.mov 
  /Users/sandipb/Movies/big/File-2020-01-14--01-22-00-CET.mov
"""
current_tz = time.tzname[1 if time.daylight else 0]


class TSFile:
    def __init__(self, path: str, src_fmt: str, src_zone: str):
        self.orig_file = path
        self.src_fmt = src_fmt
        self.src_zone = pytz.timezone(src_zone)
        self.dirname = os.path.dirname(self.orig_file)
        self.basename = os.path.basename(self.orig_file)
        self.dt = self.parse()

    def parse(self) -> datetime:
        root, _ = os.path.splitext(self.basename)
        dt = datetime.strptime(root, self.src_fmt)
        return self.src_zone.localize(dt, bool(time.daylight))

    def format(self, fmt: str, zone: str) -> str:
        dzone = pytz.timezone(zone)
        dt = self.dt.astimezone(dzone)
        root = dt.strftime(fmt)
        _, ext = os.path.splitext(self.basename)
        base = root + ext
        return os.path.join(self.dirname, base)


def main():
    parser = argparse.ArgumentParser(
        "filename_time_parse", description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--rename", "-r", action="store_true", help="Rename file in new format")
    parser.add_argument("--source-format", "-s", required=True, help="Source file format in strftime format")
    parser.add_argument("--dst-format", "-d", required=True, help="Destination file format in strftime format")

    parser.add_argument("--source-zone", "-z", default="UTC", help="Source time zone name (default: %(default)s)")
    parser.add_argument("--dst-zone", "-Z", default="UTC", help="Destination time zone name (default: %(default)s)")
    parser.add_argument("file", metavar="FILENAME", help="Target filename")
    args = parser.parse_args()
    tsfile = TSFile(args.file, args.source_format, args.source_zone)
    new_name = tsfile.format(args.dst_format, args.dst_zone)
    print(new_name)
    if args.rename:
        shutil.move(args.file, new_name)
        print("Renamed.", file=sys.stderr)


if __name__ == "__main__":
    main()
