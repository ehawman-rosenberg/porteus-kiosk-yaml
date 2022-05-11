#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from ruamel.yaml import YAML, YAMLError
from pathlib import Path
from tabulate import tabulate
import inflect
from pprint import pprint


def main():
    """Main program"""
    filename = "example_config.yml"

    file = import_data(filename)

    result = generate_result(file)

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


def generate_result(file):
    """Convert valid yml input into Porteus Kiosk ini configs"""
    result = {}
    # Loop through clients
    for client_name, client_data in file["CLIENTS"].items():
        client_data = populate_with_group(
            client_data, file["GROUPS"]
        )  # TODO find out how best to structure expanding/formatting/filtering this data (multiple functions)
        result.update({client_name: client_data})
    #     config_dict = result.values()
    #     common_configs = set.intersection(*tuple(set(d.keys()) for d in config_dict))
    #     identical_configs = [
    #         {key: val}
    #         for (key, val) in config_dict
    #         if set(list(config_dict.values())) == val
    #     ]

    # print("yes")
    warn_global(result)

    return result


def warn_global(result):
    """
    Alerts the user if one or more key:value pairs are shared amongst ALL clients,
    and are therefore candidates to be made GLOBAL configs.
    """
    key_list = set(
        [
            key
            for entry in [[*result[mac_addr].keys()] for mac_addr in result]
            for key in entry
        ]
    )
    by_key = {
        key: [result[mac_addr].get(key) for mac_addr in result] for key in key_list
    }
    common_key_vals = {
        key: [v for v in val if v is not None][0]
        for key, val in by_key.items()
        if all(item == [v for v in val if v is not None][0] for item in val)
    }
    p = inflect.engine()
    print(
        f"The following {p.plural('setting',len(common_key_vals))} {p.plural('is',len(common_key_vals))} shared among all clients."
    )
    for key, value in common_key_vals.items():
        print(f"  - {key}: {value}")
    print("Consider making these configs GLOBAL.")


def populate_with_group(client, groups):
    """Adds group properties to a member client"""
    for group in client["groups"]:
        for key, value in groups[group].items():
            if key not in client.keys():
                client.update({key: value})
            else:
                print(
                    f"{key} already exists in {client}! Which value would you like to keep?"
                )
                print(tabulate([[client[key], value]], headers=["Client", "Group"]))
                answer = input("Which value should be kept? c/g ").lower()
                if answer == "c":
                    client.update({key: value})
    del client["groups"]
    return client


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
