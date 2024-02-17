import json

import pytest

from sl_optimizer import get_number_of_slots
from tests.utils import get_fixture_path


@pytest.fixture
def storage_layout():
    filepath = get_fixture_path("uniswap_v3_factory_storage.json")
    with open(filepath) as f:
        storage_layout = json.load(f)

    return storage_layout


def test_get_number_of_slots(storage_layout):
    assert (
        get_number_of_slots(
            storage=storage_layout.get("storage"), types=storage_layout.get("types")
        )
        == 6
    )
