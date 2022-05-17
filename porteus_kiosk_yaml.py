#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO create ultimate example yml (with every single config)
# TODO create lists of mutually inclusive/exclusive configs
# TODO puzzle out how to do mutually inclusive/exclusive configs across GLOBAL+client
# TODO create Schema
# TODO Finish implementing class model
# TODO Identify cases where lists/dicts need to be appended vs overwritten (additional_components)

from ruamel.yaml import YAML, YAMLError
from pathlib import Path
from tabulate import tabulate
import inflect


class Client:
    """A Client object. Has a name and a list of values."""

    def __init__(self, name, values):
        self.name = name
        self.values = values


class GlobalClient(Client):
    def __init__(self):
        super().__init__()


class Group:
    """A Group object. has a name and a list of values."""

    def __init__(self, name, values):
        self.name = name
        self.values = values


class Config:
    """A configuration. Consists of a name and value"""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __new__(cls, name, type):
        subclass_map = {subclass.feature: subclass for subclass in cls.__subclasses__()}
        subclass = subclass_map[type]
        instance = super(Config, subclass).__new__(subclass)
        return instance

    def ini_value(self):
        raise NotImplementedError


class ConfigSimple(Config):
    """A Config simple datatype as a value"""

    type = dict

    def __init__(self):
        super().__init__()

    def ini_value(self):
        return f"{self.name}={self.value}"


class ConfigDict(Config):
    """A Config with a Dict as a value"""

    def __init__(self):
        super().__init__()

    def ini_value(self):
        new_line = f"{self.name}="
        for k, v in self.value.items():
            new_line += f"{v}|{k}| "
        new_line = new_line[:-1]  # Trim extra space
        return new_line


class ConfigSequence(Config):
    """A Config with a sequence (List/Tuple) as a value"""

    def __init__(self):
        super().__init__()

    def ini_value(self):
        new_line = f"{self.name}="
        if self.name in ("homepage", "toggle_tabs"):
            delim = "|"
        else:
            delim = " "
        for i in self.value:
            new_line += f"{i}{delim}"
        new_line = new_line[:-1]  # Trim the unneeded last pipe
        return new_line


def main():
    """Main program"""
    filename = "config.yml"  # TODO point this at some kind of file selector

    file = import_data(filename)  # Loads up data

    expanded = expand_groups(file)  #

    warn_global(
        list(expanded.values())
    )  # Can any config parameters be moved to GLOBAL?
    result = generate_results(expanded)

    export_data(filename, result)


def export_data(filename, result):
    """Writes Porteus Kiosk ini content to file"""
    with open(Path(filename).stem + ".ini", "w+") as open_file:
        open_file.write(result)


def generate_results(expanded):
    """Loops through clients, building the final ini string"""
    result = ""
    result += client_to_ini("GLOBAL", expanded["GLOBAL"])
    clients = expanded["CLIENTS"]
    for name, configs in clients.items():
        result += client_to_ini(name, configs)
    return result


def client_to_ini(name, configs):
    """Takes a client name and configs dict, returns a client formatted as Porteus Kiosk ini"""
    result = ""
    result += f"[[ {name.upper()} ]]\n"
    configs_dict = dict(sorted(configs.items()))
    if name == "GLOBAL":
        kiosk_config = configs_dict.pop("kiosk_config")
        result += f"kiosk_config={kiosk_config}\n"
    for key, value in configs_dict.items():
        if type(value) == dict:
            new_line = f"{key}="
            for k, v in value.items():
                new_line += f"{v}|{k}| "
            new_line = new_line[:-1]  # Trim the unneeded last space
        elif type(value) == list:
            new_line = f"{key}="
            if key == "homepage":
                delim = "|"
            else:
                delim = " "
            for i in value:
                new_line += f"{i}{delim}"
            new_line = new_line[:-1]  # Trim the unneeded last pipe
        else:
            new_line = f"{key}={value}"
        result += new_line + "\n"
    result += "\n"
    print(result)
    return result


def expand_groups(file):
    """Loops through clients, adding the properties of their groups to their own"""

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
    if not isect:
        return
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
