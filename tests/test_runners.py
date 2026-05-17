import pytest
from unittest.mock import patch, MagicMock
import subprocess
import os
from aquimodpy.Model import Model
from aquimodpy.EvaluationRunner import EvaluationRunner


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
