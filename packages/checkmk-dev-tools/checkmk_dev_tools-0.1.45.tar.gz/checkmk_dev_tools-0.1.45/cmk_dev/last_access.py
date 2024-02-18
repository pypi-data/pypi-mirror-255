#!/usr/bin/env python3

import glob
import logging
import os
import sys
from datetime import datetime
from pathlib import Path


def log() -> logging.Logger:
    """Convenience function retrieves 'our' logger"""
    return logging.getLogger("last-access")


def get_lastest_access(directory):
    # print(directory)
    list_of_files = [path for path in Path(directory).rglob("*") if path.is_file()]
    if not list_of_files:
        # print(directory, "empty")
        return
    latest_file = max(list_of_files, key=os.path.getctime)
    latest_access = datetime.fromtimestamp(os.path.getctime(latest_file))
    log().debug(f":(%s %s %s)", latest_access, directory, latest_file.relative_to(directory))
    return latest_access, latest_file


def main():
    latest_access = {
        path: access_data
        for path in map(Path, sys.argv[1:])
        if (access_data := get_lastest_access(path))
    }

    for path, access_data in sorted(latest_access.items(), key=lambda e: e[1]):
        if access_data is None:
            continue
        latest_access, latest_file = access_data
        print(f"{latest_access} {path} {latest_file.relative_to(path)}")


if __name__ == "__main__":
    main()
