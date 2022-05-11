#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
from pathlib import Path


def main():
    """Main program"""
    filename = "config.yml"

    file = import_data(filename)

    result = generate_result(file)

    export_data(filename, result)


def export_data(filename, result):
    """Writes Porteus Kiosk ini content to file"""
    with open(Path(filename).stem + ".ini", "w+") as open_file:
        open_file.writelines(result)


def generate_result(file):
    """Convert valid yml input into Porteus Kiosk ini configs"""

    # loop through clients, populating each with GROUP data
    #   client = pop_with_group(client, groupname) ???
    #       check for field duplicates as you're populating
    #       could throw an error, could keep the CLIENT, could ask user
    # somehow find out if all clients have any entries among them that ALL share, these *could* be moved to GLOBAL (maybe just alert user?)
    # return result


def import_data(filename):
    """Imports yml input, validating by schema"""
    with open(filename, "r") as open_file:
        try:
            file = yaml.safe_load(open_file)  # TODO Create schema and validate by it
            return file
        except yaml.YAMLError as exc:
            print(exc)


if __name__ == "__main__":
    main()
