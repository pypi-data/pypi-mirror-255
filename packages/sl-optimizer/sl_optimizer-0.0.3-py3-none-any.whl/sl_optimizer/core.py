# Copyright (c) 2024 to present Vladyslav Novotnyi and individual contributors.
"""
Contains the main function for optimizing the storage layout
and some auxiliary functions.
"""
import copy
from math import ceil

from sl_optimizer.constants import SLOT_SIZE
from sl_optimizer.utils import get_number_of_slots, is_struct

__all__ = "optimize_storage_layout"


def __first_fit(items: list, weights: dict, slot_size: int = SLOT_SIZE) -> tuple:
    """Apply the First-Fit algorithm for bin-packing.

    Args:
        items: A list of items to be packed.
        weights: A dictionary containing information about item types and their weights.
        slot_size: The size of each storage slot. Defaults to SLOT_SIZE = 32.

    Returns:
        tuple: A tuple containing the optimized storage and the total number of slots used.
    """  # noqa: E501
    optimized_storage = []
    total_slots = 0
    for item in items:
        # Try to place the item in an existing bin
        number_of_bytes = int(weights.get(item.get("type")).get("numberOfBytes"))
        for slot in optimized_storage:
            if slot.get("length") + number_of_bytes <= slot_size:
                item["slot"] = str(slot["slot_number"])
                item["offset"] = slot["length"]
                slot["variables"].append(item)
                slot["length"] += number_of_bytes
                break
        # If the item couldn't be placed in any existing bin, create a new bin
        else:
            item["slot"] = str(total_slots)
            optimized_storage.append(
                {
                    "variables": [item],
                    "length": number_of_bytes,
                    "slot_number": total_slots,
                }
            )
            if number_of_bytes > slot_size:
                total_slots += ceil(number_of_bytes / slot_size)
            else:
                total_slots += 1

    return [
        variable for slot in optimized_storage for variable in slot.get("variables")
    ], total_slots


def __first_fit_decreasing(items: list, weights: dict) -> tuple:
    """Apply the First-Fit Decreasing algorithm for `bin-packing`.

    Args:
        items: A list of items to be packed.
        weights: A dictionary containing information about item types and their weights.

    Returns:
        tuple: A tuple containing the optimized storage and the total number of slots used.
    """  # noqa: E501
    items = __sort_items(items=items, weights=weights)
    return __first_fit(items, weights)


def __sort_items(items: list, weights: dict):
    """Sort a list of items based on the number of bytes associated with each item's type.

    Args:
        items: A list of items to be sorted.
        weights: A dictionary containing information about item types and their weights.

    Returns:
        list: The sorted list of items.
    """  # noqa: E501
    return sorted(
        items,
        key=lambda variable: int(
            weights.get(variable.get("type")).get("numberOfBytes")
        ),
        reverse=True,
    )


def __optimize_storage_layout(storage: list, types: dict) -> tuple:
    """Recursively optimize the storage layout of variables.

    Args:
        storage: A list of variables representing the current storage layout.
        types: A dictionary containing information about variable types.

    Returns:
        tuple: A tuple containing the optimized storage layout and the total number of slots used.
    """  # noqa: E501
    for variable in storage:
        var_type_label = variable.get("type")
        # Check if the variable is a struct
        if is_struct(var_type_label):
            var_type = types.get(var_type_label)
            # Recursively optimize the layout of struct members
            var_storage, number_of_slots = __optimize_storage_layout(
                var_type.get("members"), types
            )
            if number_of_slots < int(var_type.get("numberOfBytes")) / SLOT_SIZE:
                var_type["members"] = var_storage
                var_type["numberOfBytes"] = str(number_of_slots * SLOT_SIZE)

    return __first_fit_decreasing(items=storage, weights=types)


def optimize_storage_layout(storage: list, types: dict) -> tuple:
    """Optimize the storage layout of variables.

    Args:
        storage: A list of variables representing the current storage layout.
        types: A dictionary containing information about variable types.

    Returns:
        tuple: A tuple containing the optimized storage layout and the modified types.
    """
    ntypes = copy.deepcopy(types)
    slots = get_number_of_slots(storage=storage, types=types)
    nstorage, nslots = __optimize_storage_layout(
        storage=copy.deepcopy(storage), types=ntypes
    )
    # if the number of new slots is less than the current one,
    # then the new storage structure and modified types are returned.
    if nslots < slots:
        return nstorage, ntypes

    return storage, types
