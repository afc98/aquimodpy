import pytest
from typing import Any
from aquimodpy.Model import Model
from aquimodpy.Components import SoilZone


class DummyComponent(SoilZone):
    REQUIRED_PARAMETERS = ["param1"]
    MAP = {"p1": "param1"}

    def __init__(self, model: Model, component_id: int = 1, **kwargs: Any) -> None:
        merged_kwargs = {"param1": 0.0}
        merged_kwargs.update(kwargs)
        super().__init__(model, component_id, **merged_kwargs)


def test_component_param_list_long():
    model = Model("Test", "exe", "dir")
    with pytest.raises(
        ValueError,
        match=r"Invalid range for parameter 'param1': expected \[min, max\] but got 3 value\(s\).",
    ):
        DummyComponent(model, 1, p1=[1, 2, 3])


def test_component_param_list_short():
    model = Model("Test", "exe", "dir")
    with pytest.raises(
        ValueError,
        match=r"Invalid range for parameter 'param1': expected \[min, max\] but got 1 value\(s\).",
    ):
        DummyComponent(model, 1, p1=[1])


def test_component_min_max_order():
    model = Model("Test", "exe", "dir")
    with pytest.raises(
        ValueError,
        match=r"Invalid range for parameter 'param1': \[2, 1\]. Min must be less than max.",
    ):
        DummyComponent(model, 1, p1=[2, 1])


def test_component_param_numeric():
    model = Model("Test", "exe", "dir")
    with pytest.raises(TypeError, match=r"Parameter 'param1' must be numeric."):
        DummyComponent(model, 1, p1=["a", "b"])
