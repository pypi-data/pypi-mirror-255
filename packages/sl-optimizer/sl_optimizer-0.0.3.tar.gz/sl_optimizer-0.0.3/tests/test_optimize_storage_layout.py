import pytest

from sl_optimizer import get_number_of_slots, optimize_storage_layout
from tests.utils import get_storage_layout

layouts = [
    (get_storage_layout("simple_4_variables.json"), 2),
    (get_storage_layout("uniswap_v3_factory_storage.json"), 6),
    (get_storage_layout("sample_contract_1_storage.json"), 14),
]


@pytest.mark.parametrize("layout,expected", layouts)
def test_optimize_storage_layout_check_number_of_slots(layout, expected):
    storage, types = layout.get("storage"), layout.get("types")
    nstorage, ntypes = optimize_storage_layout(storage=storage, types=types)
    assert get_number_of_slots(storage=nstorage, types=ntypes) == expected
