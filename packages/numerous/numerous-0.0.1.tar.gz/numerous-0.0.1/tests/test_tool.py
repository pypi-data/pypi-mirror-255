from numerous.tools import container, tool


def test_initialize_decorated_tool() -> None:
    param_value = 5

    @tool
    class Tool:
        param: int = param_value

    instance = Tool()

    assert instance
    assert instance.param == param_value
    assert getattr(instance, "__tool__", False) is True


def test_initialize_decorated_container() -> None:
    param_value = 5

    @container
    class Container:
        param: int = param_value

    instance = Container()

    assert instance
    assert instance.param == param_value
    assert getattr(instance, "__container__", False) is True
