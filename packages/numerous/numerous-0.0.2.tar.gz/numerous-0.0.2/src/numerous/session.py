"""Tool sessions manages tool instances."""

import asyncio
import logging
import random
import string
import threading
import typing
from concurrent.futures import Future
from typing import Any, Callable, Generic, Optional, Type, Union

from numerous.data_model import (
    ActionDataModel,
    ContainerDataModel,
    ElementDataModel,
    NumberFieldDataModel,
    TextFieldDataModel,
    ToolDataModel,
    dump_data_model,
)
from numerous.generated.graphql.fragments import GraphContextParent
from numerous.generated.graphql.input_types import ElementInput
from numerous.updates import UpdateHandler
from numerous.utils import ToolT

from .generated.graphql.all_elements import (
    AllElementsSession,
    AllElementsSessionAllButton,
    AllElementsSessionAllElement,
    AllElementsSessionAllNumberField,
    AllElementsSessionAllTextField,
)
from .generated.graphql.client import Client
from .generated.graphql.updates import (
    UpdatesToolSessionEventToolSessionElementAdded,
    UpdatesToolSessionEventToolSessionElementRemoved,
    UpdatesToolSessionEventToolSessionElementUpdated,
)

alphabet = string.ascii_lowercase + string.digits
ToolSessionEvent = Union[
    UpdatesToolSessionEventToolSessionElementAdded,
    UpdatesToolSessionEventToolSessionElementRemoved,
    UpdatesToolSessionEventToolSessionElementUpdated,
]
ToolSessionElement = Union[
    AllElementsSessionAllElement,
    AllElementsSessionAllButton,
    AllElementsSessionAllNumberField,
    AllElementsSessionAllTextField,
]


AllElementsSession.model_rebuild()

log = logging.getLogger(__name__)


def get_client_id() -> str:
    return "".join(random.choices(alphabet, k=8))  # noqa: S311


class SessionElementTypeMismatchError(Exception):
    def __init__(self, sess_elem: ToolSessionElement, elem: ElementDataModel) -> None:
        super().__init__(
            f"{type(elem).__name__!r} does not match {type(sess_elem).__name__!r}",
        )


class SessionElementMissingError(Exception):
    def __init__(self, elem: ElementDataModel) -> None:
        super().__init__(f"Tool session missing required element '{elem.name}'")


class ThreadedEventLoop:

    """Wrapper for an asyncio event loop running in a thread."""

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop_forever,
            name="Event Loop Thread",
            daemon=True,
        )

    def start(self) -> None:
        """Start the thread and run the event loop."""
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        """Stop the event loop, and terminate the thread."""
        if self._thread.is_alive():
            self._loop.stop()

    def schedule(self, coroutine: typing.Awaitable[typing.Any]) -> Future[Any]:
        """Schedule a coroutine in the event loop."""
        return asyncio.run_coroutine_threadsafe(coroutine, self._loop)

    def _run_loop_forever(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()


class Session(Generic[ToolT]):
    def __init__(
        self,
        session_id: str,
        client_id: str,
        instance: ToolT,
        gql: Client,
    ) -> None:
        self._session_id = session_id
        self._client_id = client_id
        self._instance = instance
        self._gql = gql
        self._update_handler = UpdateHandler(instance)

    @staticmethod
    async def initialize(
        session_id: str,
        client_id: str,
        gql: Client,
        cls: Type[ToolT],
    ) -> "Session[ToolT]":
        """
        Initialize the session.

        Creates an instance, and validates it according to the remote tool session.
        """
        print(  # noqa: T201
            f"Running in session {session_id!r} as client {client_id!r}",
        )
        threaded_event_loop = ThreadedEventLoop()
        threaded_event_loop.start()
        result = await gql.all_elements(session_id)
        data_model = dump_data_model(cls)
        _validate_tool_session(data_model, result.session)
        _wrap_tool_class_setattr(threaded_event_loop, session_id, client_id, cls, gql)
        kwargs = _get_kwargs(cls, result.session, None)
        instance = cls(**kwargs)
        _add_element_ids(instance, None, None, result.session)
        return Session(session_id, client_id, instance, gql)

    async def run(self) -> None:
        """Run the tool."""
        async for update in self._gql.updates(self._session_id, self._client_id):
            self._update_handler.handle_update(update)


def _add_element_ids(
    instance: ToolT,
    element_id: Optional[str],
    parent_element_id: Optional[str],
    session: AllElementsSession,
) -> None:
    instance.__parent_element_id__ = parent_element_id  # type: ignore[attr-defined]
    instance.__element_names_to_ids__ = {  # type: ignore[attr-defined]
        elem.name: elem.id
        for elem in session.all
        if _element_parent_is(elem.graph_context.parent, element_id)
    }
    instance.__element_ids_to_names__ = {  # type: ignore[attr-defined]
        elem.id: elem.name
        for elem in session.all
        if _element_parent_is(elem.graph_context.parent, element_id)
    }


def _element_parent_is(
    graph_parent: Optional[GraphContextParent],
    parent_element_id: Optional[str],
) -> bool:
    graph_parent_id = graph_parent.id if graph_parent else None
    return (
        graph_parent_id is None and parent_element_id is None
    ) or graph_parent_id == parent_element_id


def get_setattr(
    loop: ThreadedEventLoop,
    gql: Client,
    old_setattr: Callable[[object, str, Any], None],
    session_id: str,
    client_id: str,
) -> Callable[[object, str, Any], None]:
    def send_number_field_update(value: float, element_id: str) -> None:
        done = threading.Event()

        async def update() -> None:
            try:
                await gql.update_element(
                    session_id=session_id,
                    client_id=client_id,
                    element=ElementInput(
                        elementID=element_id,
                        numberValue=value,
                    ),
                )
            finally:
                done.set()

        loop.schedule(update())

        done.wait()

    def send_text_field_update(value: str, element_id: str) -> None:
        done = threading.Event()

        async def update() -> None:
            try:
                await gql.update_element(
                    session_id=session_id,
                    client_id=client_id,
                    element=ElementInput(elementID=element_id, textValue=value),
                )
            finally:
                done.set()

        loop.schedule(update())

        done.wait()

    def setattr_override(
        instance: ToolT,
        name: str,
        value: Any,  # noqa: ANN401
    ) -> None:
        old_setattr(instance, name, value)
        element_names_to_ids: Optional[dict[str, str]] = getattr(
            instance,
            "__element_names_to_ids__",
            None,
        )
        if element_names_to_ids is None:
            return

        element_id = element_names_to_ids.get(name)
        if element_id is None:
            return

        if isinstance(value, str):
            send_text_field_update(value, element_id)
        elif isinstance(value, (float, int)):
            send_number_field_update(value, element_id)

    return setattr_override


def _wrap_tool_class_setattr(
    loop: ThreadedEventLoop,
    session_id: str,
    client_id: str,
    cls: Type[ToolT],
    gql: Client,
) -> None:
    annotations = cls.__annotations__ if hasattr(cls, "__annotations__") else {}
    for annotation in annotations.values():
        if not getattr(annotation, "__container__", False):
            continue
        _wrap_container_class_setattr(loop, session_id, client_id, cls, gql)
    new_setattr = get_setattr(loop, gql, cls.__setattr__, session_id, client_id)
    cls.__setattr__ = new_setattr  # type: ignore[method-assign, assignment]


def _wrap_container_class_setattr(
    loop: ThreadedEventLoop,
    session_id: str,
    client_id: str,
    cls: Union[Type[ToolT]],
    gql: Client,
) -> None:
    annotations = cls.__annotations__ if hasattr(cls, "__annotations__") else {}
    for annotation in annotations.values():
        if not getattr(annotation, "__container__", False):
            continue
        _wrap_container_class_setattr(loop, session_id, client_id, annotation, gql)
    new_setattr = get_setattr(loop, gql, cls.__setattr__, session_id, client_id)
    cls.__setattr__ = new_setattr  # type: ignore[method-assign, assignment]


def _validate_tool_session(
    data_model: ToolDataModel,
    session: AllElementsSession,
) -> None:
    session_elements = {sess_elem.name: sess_elem for sess_elem in session.all}
    for elem in data_model.elements:
        if elem.name not in session_elements:
            raise SessionElementMissingError(elem)
        sess_elem = session_elements[elem.name]
        _validate_element(elem, sess_elem)


def _validate_element(elem: ElementDataModel, sess_elem: ToolSessionElement) -> None:
    valid_text_element = isinstance(elem, TextFieldDataModel) and isinstance(
        sess_elem,
        AllElementsSessionAllTextField,
    )
    valid_number_element = isinstance(elem, NumberFieldDataModel) and isinstance(
        sess_elem,
        AllElementsSessionAllNumberField,
    )
    valid_action_element = isinstance(elem, ActionDataModel) and isinstance(
        sess_elem,
        AllElementsSessionAllButton,
    )
    valid_container_element = (
        isinstance(elem, ContainerDataModel)
        and isinstance(sess_elem, AllElementsSessionAllElement)
        and sess_elem.typename__ == "Container"
    )
    if not (
        valid_text_element
        or valid_number_element
        or valid_action_element
        or valid_container_element
    ):
        raise SessionElementTypeMismatchError(sess_elem, elem)


def _get_kwargs(
    cls: Type[ToolT],
    session: AllElementsSession,
    parent_element_id: Optional[str],
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    annotations = cls.__annotations__ if hasattr(cls, "__annotations__") else {}
    for element in session.all:
        if element.graph_context.parent is not None:
            continue
        if element.typename__ == "Button":
            continue
        kwargs[element.name] = _get_kwarg_value(
            annotations[element.name],
            session,
            element,
            parent_element_id,
        )
    return kwargs


class SessionElementAnnotationMismatchError(Exception):
    def __init__(self, sess_elem: ToolSessionElement, annotation: type) -> None:
        sess_name = type(sess_elem).__name__
        ann_name = type(annotation).__name__
        super().__init__(f"{sess_name!r} does not match annotation {ann_name!r}")


def _get_kwarg_value(
    value_type: type,
    session: AllElementsSession,
    element: ToolSessionElement,
    parent_element_id: Optional[str],
) -> Any:  # noqa: ANN401
    if isinstance(element, AllElementsSessionAllNumberField):
        if value_type is not float:
            raise SessionElementAnnotationMismatchError(element, value_type)
        return element.number_value

    if isinstance(element, AllElementsSessionAllTextField):
        if value_type is not str:
            raise SessionElementAnnotationMismatchError(element, value_type)
        return element.text_value

    if (
        isinstance(element, AllElementsSessionAllElement)
        and element.typename__ == "Container"
    ):
        if not getattr(value_type, "__container__", False):
            raise SessionElementAnnotationMismatchError(element, value_type)
        return _get_container_kwarg_value(
            value_type,
            session,
            element,
            parent_element_id,
        )

    raise SessionElementAnnotationMismatchError(element, value_type)


class ContainerInitializeElementError(Exception):
    def __init__(self, container: AllElementsSessionAllElement) -> None:
        name = container.typename__
        super().__init__(f"cannot initialize non-container element {name!r}")


class ContainerInitializeAnnotationError(Exception):
    def __init__(self, container_cls: Type[ToolT]) -> None:
        name = type(container_cls).__name__
        super().__init__(f"cannot initialize non-container annotation {name!r}")


def _get_container_kwarg_value(
    container_cls: Type[ToolT],
    session: AllElementsSession,
    container: AllElementsSessionAllElement,
    parent_element_id: Optional[str],
) -> Any:  # noqa: ANN401
    if container.typename__ != "Container":
        raise ContainerInitializeElementError(container)

    if not getattr(container_cls, "__container__", False):
        raise ContainerInitializeAnnotationError(container_cls)

    annotations = (
        container_cls.__annotations__
        if hasattr(container_cls, "__annotations__")
        else {}
    )

    children = {
        e.name: e
        for e in session.all
        if e.graph_context.parent and e.graph_context.parent.id == container.id
    }

    kwargs = {
        name: _get_kwarg_value(annotation, session, children[name], container.id)
        for name, annotation in annotations.items()
        if name in children
    }

    instance = container_cls(**kwargs)
    _add_element_ids(instance, container.id, parent_element_id, session)
    return instance
