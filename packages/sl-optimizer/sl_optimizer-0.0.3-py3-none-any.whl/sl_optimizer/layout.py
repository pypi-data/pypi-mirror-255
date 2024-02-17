# Copyright (c) 2024 to present Vladyslav Novotnyi and individual contributors.
"""
Contains storage layout models.
"""
import copy
import json

from sl_optimizer.core import optimize_storage_layout
from sl_optimizer.utils import (
    check_file_exists,
    get_contact_name,
    get_number_of_slots,
    parse_storage_layout,
)

__all__ = (
    "StorageLayout",
    "OptimizedStorageLayout",
)


class BaseStorageLayout:
    def __init__(self, storage: list, types: dict):
        """Initialize the BaseStorageLayout with storage and types information.

        Args:
            storage: List containing storage information.
            types: Dictionary containing type information.
        """
        self.__storage = storage
        self.__types = types
        self.__contract_name = get_contact_name(self.__storage)
        self.__number_of_slots = get_number_of_slots(
            storage=self.__storage, types=self.__types
        )

    @property
    def storage(self) -> list:
        """Getter for the storage property."""
        return self.__storage

    @property
    def types(self) -> dict:
        """Getter for the types property."""
        return self.__types

    @property
    def contract_name(self) -> str:
        """Getter for the contract_name property."""
        return self.__contract_name

    @property
    def number_of_slots(self) -> int:
        """Getter for the number_of_slots property."""
        return self.__number_of_slots

    def save(self, filepath: str, force: bool = False) -> str:
        """Save the storage layout data to a JSON file.

        Args:
            filepath: Path to the file where the data will be saved.
            force: If True, overwrite the file even if it already exists.

        Returns:
            str: The filepath where the data is saved.
        """
        if not force:
            check_file_exists(filepath=filepath)

        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        return filepath

    def to_dict(self) -> dict:
        """Convert the storage layout data to a dictionary.

        Returns:
            dict: Dictionary representation of the storage layout data.
        """
        return {"storage": self.__storage, "types": self.__types}


class OptimizedStorageLayout(BaseStorageLayout):
    def __init__(self, storage: list = None, types: dict = None):
        """Initialize the OptimizedStorageLayout with storage and types information.

        Args:
            storage: List containing storage information.
            types: Dictionary containing type information.
        """
        super().__init__(storage=storage, types=types)

    def save(
        self,
        filepath: str = "optimized_storage_layout.json",
        force: bool = False,
    ):
        """Save the storage layout data to a JSON file.

        Args:
            filepath: Path to the file where the data will be saved. Default: optimized_storage_layout.json
            force: If True, overwrite the file even if it already exists.

        Returns:
            str: The filepath where the data is saved.
        """  # noqa: E501
        return super().save(filepath=filepath, force=force)


class StorageLayout(BaseStorageLayout):
    # todo: obviously overloaded __init__ method
    def __init__(self, data: dict = None, filepath: str = None):
        """Initialize the StorageLayout instance.

        Args:
            data: Storage layout data.
            filepath: Path to a file containing storage layout data.
        """
        if data is not None and filepath is not None:
            raise ValueError("Should have data or filepath, but not both.")
        elif data is None and filepath is None:
            raise ValueError("Should have data or filepath, but neither is provided.")
        elif filepath:
            with open(filepath, mode="r") as f:
                data = json.load(f)

        storage, types = parse_storage_layout(data=data)
        super().__init__(storage=storage, types=types)

    def optimize(self) -> "OptimizedStorageLayout":
        """Optimize the storage layout and return an instance of OptimizedStorageLayout.

        Returns:
            OptimizedStorageLayout: An optimized storage layout.
        """
        storage, types = optimize_storage_layout(storage=self.storage, types=self.types)
        return OptimizedStorageLayout(
            storage=copy.deepcopy(storage), types=copy.deepcopy(types)
        )
