#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ruamel.yaml import YAML, YAMLError
from pathlib import Path
from tabulate import tabulate
import inflect
import json  # just for exporting sample data


def main():
    """Main program"""
    filename = "example_config.yml"

    file = import_data(filename)

    expanded = expand_groups(file)

    warn_global(
        list(file["CLIENTS"].values())
    )  # Can any config parameters be moved to GLOBAL?
    result = generate_results(expanded)

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


def generate_results(expanded):
    """"""
    result = ""
    result += client_to_ini({"GLOBAL": expanded["GLOBAL"]})
    clients = expanded["CLIENTS"]
    for client in dict(clients.items()):
        client_to_ini(client)

    # for each client (starting with GLOBAL) in expanded["CLIENTS"]
    #   write the header
    #   for key, value in sorted(client)
    #       match type(value):
    print("stop")
    return result


def client_to_ini(client):
    """"""
    result = ""
    ((client_name, client_configs),) = client.items()  # Split the top-level dict
    result += f"[[ {client_name.upper()} ]]\n"
    print(result)
    for key, value in dict(sorted(client_configs.items())).items():
        match type(value):  # This is what I need help with.
            case "dict":
                print("dict")
                new_line = f"{key}="
                for k, v in value:
                    new_line += f"{v}|{k}| "
                new_line = new_line[:-1]  # Trim the unneeded last space
            case "list":
                print("list")
                new_line = f"{key}="
                for i in value:
                    new_line += f"{i}|"
                new_line = new_line[:-1]  # Trim the unneeded last pipe
            case _:
                print(type(value))
                new_line = f"{key}={value}"

        print(f"{key}: {value}")
        result += new_line + "\n"
    print(result)
    return result


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
    isect = dict(
        pair
        for pair in values_dicts[0].items()
        if all((pair in d.items() for d in values_dicts[1:]))
    )
    p = inflect.engine()
    print(
        f'The following {p.plural("setting",len(isect))} {p.plural("is",len(isect))} shared among all clients.'
    )
    for key, value in isect.items():
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
