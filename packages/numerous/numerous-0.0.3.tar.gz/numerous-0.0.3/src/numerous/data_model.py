"""Tool data model for communication."""

import inspect
from dataclasses import dataclass
from typing import Any, Optional, Type

from numerous.tools import HTML
from numerous.utils import MISSING, ToolT


@dataclass(frozen=True)
class ElementDataModel:
    name: str


@dataclass(frozen=True)
class HTMLElementDataModel(ElementDataModel):
    default: str
    type: str = "html"


@dataclass(frozen=True)
class TextFieldDataModel(ElementDataModel):
    default: str
    type: str = "string"


@dataclass(frozen=True)
class NumberFieldDataModel(ElementDataModel):
    default: float
    type: str = "number"


@dataclass(frozen=True)
class ActionDataModel(ElementDataModel):
    type: str = "action"


@dataclass(frozen=True)
class ContainerDataModel(ElementDataModel):
    elements: list[ElementDataModel]
    type: str = "container"


@dataclass(frozen=True)
class ToolDataModel:
    name: str
    elements: list[ElementDataModel]


class ToolDataModelError(Exception):
    def __init__(self, cls: Type[ToolT], name: str, annotation: str) -> None:
        super().__init__(
            f"Invalid Tool. Unsupport field: {cls.__name__}.{name}: {annotation}",
        )


class ToolDefinitionError(Exception):
    def __init__(self, cls: Type[ToolT]) -> None:
        self.cls = cls
        super().__init__(
            f"Tool {self.cls.__name__} not defined with the @tool decorator",
        )


def dump_data_model(cls: Type[ToolT]) -> ToolDataModel:
    if not getattr(cls, "__tool__", False):
        raise ToolDefinitionError(cls)

    elements = _dump_element_data_models(cls)

    return ToolDataModel(name=cls.__name__, elements=elements)


def _dump_element_from_annotation(
    name: str,
    annotation: Any,  # noqa: ANN401
    default: Any,  # noqa: ANN401
) -> Optional[ElementDataModel]:
    if annotation is str:
        if not isinstance(default, str):
            default = ""
        return TextFieldDataModel(name=name, default=default)

    if annotation is float:
        if not isinstance(default, (float, int)):
            default = 0.0
        return NumberFieldDataModel(name=name, default=int(default))

    if annotation is HTML:
        if not isinstance(default, HTML):
            default = HTML("")
        return HTMLElementDataModel(name=name, default=default.html)

    if getattr(annotation, "__container__", False):
        return dump_container_data_model(name, annotation)

    return None


def _dump_element_data_models(cls: Type[ToolT]) -> list[ElementDataModel]:
    elements: list[ElementDataModel] = []
    annotations = cls.__annotations__ if hasattr(cls, "__annotations__") else {}
    for name, annotation in annotations.items():
        default = getattr(cls, name, MISSING)
        if elem := _dump_element_from_annotation(name, annotation, default):
            elements.append(elem)
        else:
            raise ToolDataModelError(cls, name, annotation)

    for name, func in inspect.getmembers(cls, inspect.isfunction):
        if getattr(func, "__action__", False):
            elements.append(ActionDataModel(name))

    return elements


class ContainerDefinitionError(Exception):
    def __init__(self, cls: Type[ToolT]) -> None:
        self.cls = cls
        super().__init__(
            f"Container {self.cls.__name__} not defined with the @container decorator",
        )


def dump_container_data_model(name: str, cls: Type[ToolT]) -> ContainerDataModel:
    if not getattr(cls, "__container__", False):
        raise ContainerDefinitionError(cls)

    elements = _dump_element_data_models(cls)

    return ContainerDataModel(name=name, elements=elements)
