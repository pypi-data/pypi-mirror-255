# Copyright (c) 2024 to present Vladyslav Novotnyi and individual contributors.
"""
Just contains constants.
"""
__all__ = (
    "SLOT_SIZE",
    "STORAGE_LAYOUT_JSON_SCHEMA",
)

SLOT_SIZE: int = 32
STORAGE_LAYOUT_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://example.com/storage_layout.schema.json",
    "title": "Storage layout",
    "type": "object",
    "properties": {
        "storage": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "astId": {"type": "integer"},
                    "contract": {"type": "string"},
                    "label": {"type": "string"},
                    "offset": {"type": "integer"},
                    "slot": {"type": "string"},
                    "type": {"type": "string"},
                },
                "required": ["astId", "contract", "label", "offset", "slot", "type"],
            },
            "minItems": 1,
        },
        "types": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "encoding": {"type": "string"},
                    "label": {"type": "string"},
                    "numberOfBytes": {"type": "string"},
                    "members": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "astId": {"type": "integer"},
                                "contract": {"type": "string"},
                                "label": {"type": "string"},
                                "offset": {"type": "integer"},
                                "slot": {"type": "string"},
                                "type": {"type": "string"},
                            },
                            "required": [
                                "astId",
                                "contract",
                                "label",
                                "offset",
                                "slot",
                                "type",
                            ],
                        },
                        "minItems": 1,
                    },
                    "key": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["encoding", "label", "numberOfBytes"],
            },
        },
    },
    "required": ["storage", "types"],
}
