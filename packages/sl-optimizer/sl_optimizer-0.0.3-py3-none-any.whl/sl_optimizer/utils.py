# Copyright (c) 2024 to present Vladyslav Novotnyi and individual contributors.
"""
Provides utility functions.
"""
from math import ceil
from pathlib import Path

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from sl_optimizer.constants import SLOT_SIZE, STORAGE_LAYOUT_JSON_SCHEMA
from sl_optimizer.errors import LayoutError, StorageLayoutError


def check_file_exists(filepath: str):
    """Check if a file already exists. If it does, raise FileExistsError.

    Args:
        filepath: The path to the file.

    Raises:
        FileExistsError: If the file already exists.
    """
    if Path(filepath).exists():
        raise FileExistsError(f"The file '{filepath}' already exists.")


def parse_storage_layout(data: dict) -> tuple:
    """Parse storage layout data and extract 'storage' and 'types' information.

    Args:
        data: The storage layout data to be parsed.

    Returns:
        tuple: A tuple containing 'storage' and 'types' information.

    Raises:
        LayoutError: If the storage layout data is invalid or does not conform to the expected schema.
    """  # noqa: E501
    try:
        validate_storage_layout(data=data)
    except ValidationError as e:
        # todo: consider the error message
        raise LayoutError(f"Invalid storage layout data scheme. {e}")

    return data.get("storage"), data.get("types")


def validate_storage_layout(data: dict, schema: dict = STORAGE_LAYOUT_JSON_SCHEMA):
    """Validate the storage layout data against a provided JSON schema.

    Args:
        data: The storage layout data to be validated.
        schema: The JSON schema used for validation.

    Raises:
        ValidationError: If the data does not conform to the specified schema.
    """
    validate(instance=data, schema=schema)


def get_contact_name(storage: list) -> str:
    """Get a name of smart contact.

    Args:
        storage: The storage of smart contract.

    Returns:
        string: The smart contract name.

    Raises:
        StorageLayoutError: When an incorrect data scheme is provided.
    """
    # Example of `storage` data scheme:
    # [
    #     {
    #       "astId": 3,
    #       "contract": "SomeContract3.sol:ContractName",
    #       "label": "name",
    #       "offset": 0,
    #       "slot": "0",
    #       "type": "t_string_storage"
    #     }
    # ]
    try:
        return storage[0].get("contract").split(":")[1]
    except (AttributeError, TypeError, ValueError, KeyError, IndexError):
        raise StorageLayoutError


def get_number_of_slots(storage: list, types: dict) -> int:
    """Calculate the number of storage slots used.

    Args:
        storage: A list representing the current storage layout.
        types: A dictionary containing information about variable types.

    Returns:
        int: The number of storage slots.
    """
    last_variable = storage[-1]
    number_of_bytes = int(types.get(last_variable.get("type")).get("numberOfBytes"))
    slot = int(last_variable.get("slot")) + 1
    if number_of_bytes > SLOT_SIZE:
        return slot + ceil(number_of_bytes / SLOT_SIZE)

    return slot


def is_struct(label: str) -> bool:
    """Check if a given label represents a struct.

    Args:
        label: The label of variable type.

    Returns:
        bool: True if the label starts with "t_struct", indicating it is likely a struct; False otherwise.

    Example:

    >>> is_struct("t_struct(Person)")
    True

    >>> is_struct("t_uint256")
    False
    """  # noqa: E501
    return label.startswith("t_struct")
