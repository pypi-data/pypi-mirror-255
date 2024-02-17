import json

import pytest

from sl_optimizer.errors import StorageLayoutError
from sl_optimizer.utils import get_contact_name

from .utils import get_fixture_path


@pytest.fixture
def storage():
    filepath = get_fixture_path("contract_name_storage.json")
    with open(filepath) as f:
        storage_layout = json.load(f)

    return storage_layout.get("storage")


def test_get_contact_name(storage):
    assert get_contact_name(storage=storage) == "ContractName"


def test_get_contact_name_fail():
    with pytest.raises(StorageLayoutError):
        get_contact_name(storage=[])
