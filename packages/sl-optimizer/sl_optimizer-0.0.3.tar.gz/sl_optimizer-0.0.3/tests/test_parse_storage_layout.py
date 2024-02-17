import json

import pytest
from jsonschema.exceptions import ValidationError

from sl_optimizer import parse_storage_layout
from sl_optimizer.errors import LayoutError
from sl_optimizer.utils import validate_storage_layout
from tests.utils import get_fixture_path


@pytest.fixture
def storage():
    filepath = get_fixture_path("uniswap_v3_factory_storage.json")
    with open(filepath) as f:
        storage_layout = json.load(f)

    return storage_layout


def test_parse_storage_layout(storage):
    parse_storage_layout(data=storage)


def test_parse_storage_layout_fail():
    with pytest.raises(LayoutError):
        parse_storage_layout(data={})


def test_validate_storage_layout_raises_validation_error():
    with pytest.raises(ValidationError):
        validate_storage_layout(data={})
