import json

import pytest
from deepdiff import DeepDiff

from sl_optimizer import StorageLayout
from sl_optimizer.errors import LayoutError
from tests.utils import get_fixture_path, get_storage_layout


@pytest.fixture
def layout():
    filepath = get_fixture_path("uniswap_v3_factory_storage.json")
    with open(filepath) as f:
        layout = json.load(f)

    return layout


@pytest.fixture
def sl(layout):
    return StorageLayout(data=layout)


sls = [
    (
        StorageLayout(filepath=str(get_fixture_path("simple_4_variables.json"))),
        get_storage_layout("expected_simple_4_variables.json"),
    ),
    (
        StorageLayout(
            filepath=str(
                get_fixture_path("sample_optimization_is_not_applied_storage.json")
            )
        ),
        get_storage_layout("sample_optimization_is_not_applied_storage.json"),
    ),
]


class TestStorageLayout:
    def test_init_with_no_args(self):
        with pytest.raises(ValueError):
            StorageLayout()

    def test_init_with_both_args(self):
        with pytest.raises(ValueError):
            StorageLayout(data={}, filepath="file.txt")

    def test_init_with_filepath_arg_file_does_not_exist(self):
        with pytest.raises(FileNotFoundError):
            StorageLayout(filepath="file.txt")

    def test_init_with_filepath_arg_file_exists(self):
        StorageLayout(filepath=str(get_fixture_path("uniswap_v3_factory_storage.json")))

    def test_init_with_data_arg_wrong_schema(self):
        with pytest.raises(LayoutError):
            StorageLayout(data={})

    def test_init_with_data_arg(self, layout):
        StorageLayout(data=layout)

    def test_check_properties(self, layout):
        sl = StorageLayout(data=layout)

        assert id(layout.get("storage")) == id(sl.storage)
        with pytest.raises(AttributeError):
            sl.storage = None

        assert id(layout.get("types")) == id(sl.types)
        with pytest.raises(AttributeError):
            sl.types = None

    def test_contract_name(self, layout):
        sl = StorageLayout(data=layout)
        assert sl.contract_name == "UniswapV3Factory"
        with pytest.raises(AttributeError):
            sl.contract_name = None

    def test_number_of_slots(self, layout):
        sl = StorageLayout(data=layout)
        assert sl.number_of_slots == 6
        with pytest.raises(AttributeError):
            sl.number_of_slots = None

    @pytest.mark.parametrize("sl,expected", sls)
    def test_optimize(self, sl: StorageLayout, expected: dict):
        osl = sl.optimize()
        assert not DeepDiff(osl.to_dict(), expected)

    def test_save(self, tmp_path, sl: StorageLayout):
        file_path = tmp_path / "test_file.json"
        sl.save(filepath=str(file_path))
        assert file_path.exists()

    def test_save_fail(self, tmp_path, sl: StorageLayout):
        file_path = tmp_path / "test_file.json"
        file_path.touch()

        with pytest.raises(FileExistsError):
            sl.save(str(file_path))

    def test_save_with_force_option(self, tmp_path, sl: StorageLayout):
        file_path = tmp_path / "test_file.json"
        file_path.touch()
        sl.save(str(file_path), force=True)
        assert file_path.exists()
        # additional check of file contents
        with open(file_path) as f:
            data = json.load(f)

        assert not DeepDiff(sl.to_dict(), data)
