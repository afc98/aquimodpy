import pytest
import pandas as pd
import os
from aquimodpy.Model import Model
from aquimodpy.Components import FAO, Weibull, Q3K3S1, Q1K1S1, Observations
from aquimodpy.EvaluationRunner import EvaluationRunner
from aquimodpy.CalibrationRunner import CalibrationRunner


@pytest.fixture
def temp_working_dir(tmp_path):
    d = tmp_path / "model_run"
    d.mkdir()
    return str(d)


def test_evaluation_setup(temp_working_dir):
    model = Model("TestModel", "mock_exe", temp_working_dir)

    # Setup components
    FAO(model, theta_fc=0.4, theta_wp=0.1, Z_r=1000, p=0.5, BFI=0.8)
    Weibull(model, k=2.0, lambda_=5.0)
    Q3K3S1(model, dx=1000, K3=10, K2=5, K1=1, S=0.01, z3=50, z2=40, z1=30, alpha=1)

    # Setup observations
    dates = pd.date_range("2020-01-01", periods=10)
    obs_df = pd.DataFrame(
        {"DATE": dates, "RAIN": [1.0] * 10, "PET": [0.5] * 10, "GWL": [45.0] * 10}
    )
    Observations(
        model, obs_df, {"DATE": "DATE", "RAIN": "RAIN", "PET": "PET", "GWL": "GWL"}
    )

    runner = EvaluationRunner(model)
    model.set_runner(runner)
    model.set_simulation_mode("e", n_runs=1, variable="g")
    model.spinup_time = 5

    model.setup()

    # Verify files
    assert os.path.exists(os.path.join(temp_working_dir, "Input.txt"))
    assert os.path.exists(os.path.join(temp_working_dir, "Observations.txt"))
    assert os.path.exists(os.path.join(temp_working_dir, "Evaluation", "FAO_eval.txt"))

    with open(os.path.join(temp_working_dir, "Input.txt"), "r") as f:
        content = f.read()
        assert "1 1 1" in content
        assert "e" in content
        assert "5" in content


def test_calibration_setup(temp_working_dir):
    model = Model("CalibModel", "mock_exe", temp_working_dir)

    # Setup components with bounds
    FAO(model, theta_fc=[0.3, 0.5], theta_wp=0.1, Z_r=1000, p=0.5, BFI=0.8)
    Weibull(model, k=[1.0, 7.0], lambda_=[1.0, 20.0])
    Q1K1S1(model, dx=500, K1=[0.1, 10.0], S=[0.001, 0.1], z1=20, alpha=[0, 1])

    runner = CalibrationRunner(model)
    model.set_runner(runner)
    model.set_simulation_mode("m", n_runs=1000, threshold=0.7)

    model.setup()

    assert os.path.exists(
        os.path.join(temp_working_dir, "Calibration", "FAO_calib.txt")
    )
    assert os.path.exists(
        os.path.join(temp_working_dir, "Calibration", "Weibull_calib.txt")
    )
    assert os.path.exists(
        os.path.join(temp_working_dir, "Calibration", "Q1K1S1_calib.txt")
    )

    with open(os.path.join(temp_working_dir, "Calibration", "FAO_calib.txt"), "r") as f:
        content = f.read()
        assert "theta_fc(-)" in content
        assert "0.3 0.5" in content
