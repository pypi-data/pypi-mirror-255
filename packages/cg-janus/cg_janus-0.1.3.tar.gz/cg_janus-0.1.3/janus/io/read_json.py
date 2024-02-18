"""Read JSON module"""
import json
from pathlib import Path


class OrderedDictWithUnchangedOrder(dict):
    def __setitem__(self, key, value):
        if key not in self:
            super(OrderedDictWithUnchangedOrder, self).__setitem__(key, value)


def read_json(file_path: Path) -> any:
    """Read content in a json file."""
    with open(file_path, "r") as file:
        return json.load(file, object_pairs_hook=OrderedDictWithUnchangedOrder)
