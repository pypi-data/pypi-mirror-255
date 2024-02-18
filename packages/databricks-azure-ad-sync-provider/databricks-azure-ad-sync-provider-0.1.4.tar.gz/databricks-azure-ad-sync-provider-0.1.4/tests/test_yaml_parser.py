import pytest

from src.databricks_azure_ad_sync_provider.yaml_parser import (
    is_azure_object_id,
    parse_yaml,
)


def test_raises_typeerror_when_no_groups_list():
    with pytest.raises(TypeError):
        parse_yaml("tests/test_files/no_groups_list.yaml")


@pytest.mark.parametrize(
    "object_id,result", [("123", False), ("cac07e36-df30-457a-bc31-4e92d71d07c5", True)]
)
def test_is_azure_object_id(object_id, result):
    assert is_azure_object_id(object_id) == result


@pytest.mark.parametrize(
    "filepath",
    ["invalid_object_id_in_groups.yaml", "invalid_object_id_in_exclude.yaml"],
)
def test_raises_valueerror_when_file_contains_invalid_object_id(filepath):
    with pytest.raises(ValueError):
        parse_yaml(f"tests/test_files/{filepath}")
