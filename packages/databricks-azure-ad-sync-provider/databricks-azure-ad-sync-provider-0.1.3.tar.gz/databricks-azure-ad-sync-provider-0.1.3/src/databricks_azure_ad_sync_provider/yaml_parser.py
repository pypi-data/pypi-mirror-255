"""
This library is used to parse yaml file
"""

import re

import yaml


def parse_yaml(path):
    with open(path) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    # Check if groups list exists in yaml file
    if "groups" not in data:
        raise TypeError("File doesn't contain mandatory list 'groups'.")

    # Check if all items have the structure of an azure object id
    for item in data["groups"]:
        if not is_azure_object_id(item):
            raise ValueError(f"{item} is not a valid Azure Object Id.")
    if "exclude" in data:
        for item in data["exclude"]:
            if not is_azure_object_id(item):
                raise ValueError(f"{item} is not a valid Azure Object Id.")
    else:
        data["exclude"] = []
    return data["groups"], data["exclude"]


def is_azure_object_id(value: str) -> bool:
    rx = "[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}"
    x = re.search(rx, value)
    return x is not None
