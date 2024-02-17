import pytest

from sl_optimizer import optimize_storage_layout
from tests.utils import get_storage_layout

layouts = [
    get_storage_layout("sample_optimization_is_not_applied_storage.json"),
    get_storage_layout("uniswap_v3_factory_storage.json"),
]


@pytest.mark.parametrize("layout", layouts)
def test_optimization_is_not_applied(layout):
    storage, types = layout.get("storage"), layout.get("types")
    nstorage, ntypes = optimize_storage_layout(storage=storage, types=types)
    assert id(storage) == id(nstorage)
    assert id(ntypes) == id(types)
