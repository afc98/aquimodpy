import pytest
from unittest.mock import patch, MagicMock
import subprocess
import os
import pandas as pd
from aquimodpy.Model import Model
from aquimodpy.EvaluationRunner import EvaluationRunner
from aquimodpy.CalibrationRunner import CalibrationRunner
from aquimodpy.Components import FAO, Observations


def test_evaluation_runner_multiple_params(tmp_path):
    model = Model("Test", "exe", str(tmp_path))
    fao = FAO(model, 0.4, 0.1, 1000, 0.5, 0.8)

    # Set multiple parameter sets
    fao.parameters = [
        {
            "theta_fc(-)": 0.4,
            "theta_wp(-)": 0.1,
            "Z_r(mm)": 1000,
            "p(-)": 0.5,
            "BFI(-)": 0.8,
        },
        {
            "theta_fc(-)": 0.3,
            "theta_wp(-)": 0.1,
            "Z_r(mm)": 1000,
            "p(-)": 0.5,
            "BFI(-)": 0.8,
        },
    ]

    runner = EvaluationRunner(model)
    model.set_runner(runner)

    # We just want to test if it prepares files correctly without crashing
    # Mocking necessary files for prepare()
    os.makedirs(tmp_path, exist_ok=True)

    # prepare() calls model.observations.prepare() if present
    # let's add observations too
    obs_df = pd.DataFrame({"DATE": ["2020-01-01"], "RAIN": [1.0], "PET": [0.5]})
    Observations(model, obs_df, columns={"DATE": "DATE", "RAIN": "RAIN", "PET": "PET"})

    runner.prepare()

    # Check if FAO_eval.txt exists in Evaluation dir and has multiple lines
    params_file = os.path.join(tmp_path, "Evaluation", "FAO_eval.txt")
    assert os.path.exists(params_file)
    with open(params_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == 3  # Header + 2 data lines


def test_evaluation_runner_empty_list_params(tmp_path):
    model = Model("Test", "exe", str(tmp_path))
    fao = FAO(model, 0.4, 0.1, 1000, 0.5, 0.8)
    fao.parameters = []

    runner = EvaluationRunner(model)
    model.set_runner(runner)
    runner.prepare()
    # Should just continue without error


def test_calibration_runner_single_value_bounds(tmp_path):
    model = Model("Test", "exe", str(tmp_path))
    # FAO requires 5 params
    fao = FAO(model, 0.4, 0.1, 1000, 0.5, 0.8)
    # Use a single value for one parameter bound
    fao.parameters = {
        "theta_fc(-)": 0.4,  # single value
        "theta_wp(-)": [0.1, 0.2],
        "Z_r(mm)": (1000, 1000),
        "p(-)": [0.5, 0.5],
        "BFI(-)": [0.8, 0.8],
    }

    runner = CalibrationRunner(model)
    model.set_runner(runner)
    runner.prepare()

    params_file = os.path.join(tmp_path, "Calibration", "FAO_calib.txt")
    assert os.path.exists(params_file)
    with open(params_file, "r") as f:
        content = f.read()
        assert "0.4 0.4" in content  # Should have been converted to [0.4, 0.4]


def test_calibration_runner_bounds_none_trigger(tmp_path):
    # This targets line 35 of CalibrationRunner.py: "if bounds is None: continue"
    # We have to bypass FAO's validation to get here
    model = Model("Test", "exe", str(tmp_path))
    fao = FAO(model, 0.4, 0.1, 1000, 0.5, 0.8)
    # Manually remove a required parameter from fao.parameters
    del fao.parameters["theta_fc(-)"]

    runner = CalibrationRunner(model)
    model.set_runner(runner)
    runner.prepare()

    params_file = os.path.join(tmp_path, "Calibration", "FAO_calib.txt")
    with open(params_file, "r") as f:
        content = f.read()
        assert "theta_fc(-)" not in content


def test_runner_run_command():
    # Use absolute paths in test to match Model's internal expansion
    exe_path = os.path.abspath("aquimod2.exe")
    working_dir = os.path.abspath("/working/dir")

    model = Model("Test", exe_path, working_dir, exec_prefix=None)
    runner = EvaluationRunner(model)

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="Success")
        runner.run()

        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        assert args[0] == [exe_path, working_dir]


def test_runner_run_wine():
    exe_path = os.path.abspath("aquimod2.exe")
    working_dir = os.path.abspath("/working/dir")

    model = Model("Test", exe_path, working_dir, exec_prefix=["wine"])
    runner = EvaluationRunner(model)

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="Success")
        runner.run()

        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        assert args[0] == ["wine", exe_path, working_dir]


def test_runner_error_handling():
    model = Model("Test", "exe", "dir")
    runner = EvaluationRunner(model)

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "cmd", stderr="Model failed"
        )
        with pytest.raises(subprocess.CalledProcessError):
            runner.run()
