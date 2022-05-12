#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ruamel.yaml import YAML, YAMLError
from pathlib import Path
from tabulate import tabulate
import inflect


def main():
    """Main program"""
    filename = "example_config.yml"

    file = import_data(filename)

    expanded = expand_groups(file)

    warn_global(
        file["CLIENTS"].values()
    )  # Can any config parameters be moved to GLOBAL?

    result = generate_result(expanded)

    export_data(filename, result)


def export_data(filename, result):
    """Writes Porteus Kiosk ini content to file"""
    with open(Path(filename).stem + ".ini", "w+") as open_file:
        try:
            yaml = YAML(typ="safe")
            yaml.default_flow_style = False
            yaml.dump(result, open_file)
        except YAMLError as exc:
            print(exc)


def generate_result(expanded):
    """"""
    result = []
    result.append(generate_header("GLOBAL"))

    # turn GLOBAL into a "client" and add it to (the front of) expanded["CLIENTS"]
    # delete GLOBAL
    # for each client (starting with GLOBAL) in expanded["CLIENTS"]
    #   write the header
    #   for key, value in sorted(client)
    #       match type(value):
    print("stop")


def generate_header(client_name):
    return f"[[ {client_name} ]]"


def expand_groups(file):
    """Convert valid yml input into Porteus Kiosk ini configs"""

    if "GROUPS" in file:  # Do we even need to be here?
        # Loop through clients
        for client_name, client_data in file["CLIENTS"].items():
            if "groups" in client_data:
                for group in client_data["groups"]:
                    if not group in file["GROUPS"]:
                        raise KeyError(f"{group} is not a valid group!")
                    for key, value in file["GROUPS"][group].items():
                        client_data.update({key: value})
                del client_data["groups"]
            file["CLIENTS"].update({client_name: client_data})
    del file["GROUPS"]

    return file


def warn_global(values_dicts):
    """
    Alerts the user if one or more key:value pairs are shared amongst ALL clients,
    and are therefore candidates to be made GLOBAL configs.
    """
    # key_list = set(
    #     [
    #         key
    #         for entry in [[*result[mac_addr].keys()] for mac_addr in result]
    #         for key in entry
    #     ]
    # )
    # by_key = {
    #     key: [result[mac_addr].get(key) for mac_addr in result] for key in key_list
    # }
    # common_key_vals = {
    #     key: [v for v in val if v is not None][0]
    #     for key, val in by_key.items()
    #     if all(item == [v for v in val if v is not None][0] for item in val)
    # }
    isect = dict(
        pair
        for pair in list(values_dicts)[0].items()
        if all((pair in d.items() for d in list(values_dicts)[1:]))
    )  # TODO troubleshoot

    print(isect)
    p = inflect.engine()
    print(
        f'The following {p.plural("setting",len(common_key_vals))} {p.plural("is",len(common_key_vals))} shared among all clients.'
    )
    for key, value in common_key_vals.items():
        print(f"  - {key}: {value}")
    print("Consider making these configs GLOBAL.")


def import_data(filename):
    """Imports yml input, validating by schema"""
    with open(filename, "r") as open_file:
        try:
            yaml = YAML(typ="safe")
            file = yaml.load(open_file)  # TODO Create schema and validate by it
            return file
        except YAMLError as exc:
            print(exc)


if __name__ == "__main__":
    main()
