"""Miscellaneous utilities."""


from typing import TypeVar


class _MissingType:
    pass


MISSING = _MissingType()

ToolT = TypeVar("ToolT")
