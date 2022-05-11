#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from ruamel.yaml import YAML, YAMLError
from pathlib import Path
from tabulate import tabulate
import json


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
        # client_data = populate_with_group(client_data, file["GROUPS"])
        result.update({client_name: client_data})
        # somehow find out if all clients have any entries among them that ALL share, these *could* be moved to GLOBAL (maybe just alert user?)
        # return result
    #     config_dict = result.values()
    #     common_configs = set.intersection(*tuple(set(d.keys()) for d in config_dict))
    #     identical_configs = [
    #         {key: val}
    #         for (key, val) in config_dict
    #         if set(list(config_dict.values())) == val
    #     ]

    # print("yes")

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
    print(common_key_vals)

    return result


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
