# Copyright (c) 2024 to present Vladyslav Novotnyi and individual contributors.
"""
Just contains imports.
"""

from sl_optimizer.core import optimize_storage_layout
from sl_optimizer.errors import LayoutError, StorageLayoutError
from sl_optimizer.layout import OptimizedStorageLayout, StorageLayout
from sl_optimizer.utils import (
    get_contact_name,
    get_number_of_slots,
    parse_storage_layout,
)

__all__ = (
    # main models
    "StorageLayout",
    "OptimizedStorageLayout",
    # main function
    "optimize_storage_layout",
    # utility functions
    "get_contact_name",
    "get_number_of_slots",
    "parse_storage_layout",
    # errors
    "LayoutError",
    "StorageLayoutError",
)
