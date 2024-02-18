"""Define tools with a dataclass-like interface."""

from dataclasses import dataclass
from typing import Any, Callable, Type

from typing_extensions import dataclass_transform

from numerous.utils import ToolT


@dataclass_transform()
def tool(cls: Type[ToolT]) -> Type[ToolT]:
    """Define a tool."""
    cls.__tool__ = True  # type: ignore[attr-defined]
    return dataclass(cls)


@dataclass_transform()
def container(cls: Type[ToolT]) -> Type[ToolT]:
    """Define a container."""
    cls.__container__ = True  # type: ignore[attr-defined]
    return dataclass(cls)


def action(action: Callable[[ToolT], Any]) -> Callable[[ToolT], Any]:
    """Define an action."""
    action.__action__ = True  # type: ignore[attr-defined]
    return action
