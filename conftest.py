import io

import pytest
import ruamel.yaml
from comments_sort import map_sort_before, seq_sort_before, sorted_index


@pytest.fixture(scope="module")
def prepare_yaml():
    yaml = ruamel.yaml.YAML()
    yield yaml


class Helpers:
    @staticmethod
    def yaml_to_str(yaml, obj):
        stream = io.StringIO()
        yaml.dump(obj, stream)
        return stream.getvalue()

    @staticmethod
    def sort_map_and_str(yaml, yaml_str, sorted_args={}) -> str:
        obj = yaml.load(yaml_str)
        sorted_keys = sorted(obj.keys(), **sorted_args)
        obj_sorted = map_sort_before(obj, sorted_keys)
        return Helpers.yaml_to_str(yaml, obj_sorted)

    @staticmethod
    def sort_seq_and_str(yaml, yaml_str, sorted_args={}) -> str:
        obj = yaml.load(yaml_str)
        sorted_indices = sorted_index(obj, **sorted_args)
        obj_sorted = seq_sort_before(obj, sorted_indices)
        return Helpers.yaml_to_str(yaml, obj_sorted)


@pytest.fixture(scope="module")
def helpers():
    return Helpers
