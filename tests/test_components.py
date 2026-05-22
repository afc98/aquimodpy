from typing import Any
import pytest
import os
from aquimodpy.Model import Model
from aquimodpy.Components import FAO, Weibull, Q1K1S1, SoilZone, Component


class DummyComponent(SoilZone):
    REQUIRED_PARAMETERS = ["param1"]
    MAP = {"p1": "param1"}

    def __init__(self, model: Model, component_id: int = 1, **kwargs: Any) -> None:
        super().__init__(model, component_id, **kwargs)


def test_component_base_missing_params():
    model = Model("Test", "exe", "dir")
    with pytest.raises(ValueError, match="Missing required parameters"):
        DummyComponent(model, 1, p2="wrong")


def test_component_unfriendly_names():
    model = Model("Test", "exe", "dir")
    # Passing "param1" directly instead of "p1"
    c = DummyComponent(model, 1, param1=10)
    assert c.parameters["param1"] == 10


def test_component_validation():
    model = Model("Test", "exe", "dir")

    # Test valid initialization
    fao = FAO(model, theta_fc=0.4, theta_wp=0.1, Z_r=1000, p=0.5, BFI=0.8)
    assert fao.parameters["theta_fc(-)"] == 0.4

    # Test missing parameters
    with pytest.raises(TypeError):  # Missing required arguments in constructor
        FAO(model, theta_fc=0.4)


def test_weibull_keyword_handling():
    model = Model("Test", "exe", "dir")
    wb = Weibull(model, k=2.0, lambda_=5.0)
    assert wb.parameters["lambda(-)"] == 5.0
    assert wb.parameters["k(-)"] == 2.0


def test_component_overwrite_warning():
    model = Model("Test", "exe", "dir")
    FAO(model, theta_fc=0.4, theta_wp=0.1, Z_r=1000, p=0.5, BFI=0.8)

    with pytest.warns(UserWarning, match="Replacing existing SoilZone component"):
        FAO(model, theta_fc=0.3, theta_wp=0.1, Z_r=1000, p=0.5, BFI=0.8)


def test_sat_zone_parameters():
    model = Model("Test", "exe", "dir")
    sat = Q1K1S1(model, dx=1000, K1=0.5, S=0.01, z1=10, alpha=1)
    assert sat.parameters["deltaX(m)"] == 1000
    assert sat.parameters["K_1(m/d)"] == 0.5
    assert sat.parameters["S(-)"] == 0.01
    assert sat.parameters["z_1(m)"] == 10
