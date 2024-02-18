from numerous.data_model import (
    ContainerDataModel,
    NumberFieldDataModel,
    TextFieldDataModel,
    ToolDataModel,
    dump_data_model,
)
from numerous.tools import container, tool


def test_dump_data_model_expected_tool_name() -> None:
    @tool
    class ToolWithAName:
        param: str

    data_model = dump_data_model(ToolWithAName)

    assert data_model.name == "ToolWithAName"


def test_dump_data_model_number_field() -> None:
    default_param_value = 5

    @tool
    class Tool:
        param: float = default_param_value

    data_model = dump_data_model(Tool)

    assert data_model == ToolDataModel(
        name="Tool",
        elements=[
            NumberFieldDataModel(name="param", default=default_param_value),
        ],
    )


def test_dump_data_model_text_field() -> None:
    default_param_value = "default string"

    @tool
    class Tool:
        param: str = default_param_value

    data_model = dump_data_model(Tool)

    assert data_model == ToolDataModel(
        name="Tool",
        elements=[
            TextFieldDataModel(name="param", default=default_param_value),
        ],
    )


def test_dump_data_model_container_field() -> None:
    default_param_value = "default string"

    @container
    class Container:
        param: str = default_param_value

    @tool
    class Tool:
        container: Container

    data_model = dump_data_model(Tool)

    assert data_model == ToolDataModel(
        name="Tool",
        elements=[
            ContainerDataModel(
                name="container",
                elements=[
                    TextFieldDataModel(name="param", default=default_param_value),
                ],
            ),
        ],
    )
