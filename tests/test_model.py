import pytest
import os
import pandas as pd
from aquimodpy.Model import Model


def test_model_path_expansion():
    model = Model("Test", "~/test_exe", "~/test_dir")
    # Expanding ~ should happen
    assert os.path.isabs(model.executable_path)
    assert os.path.isabs(model.working_directory)
    assert "test_exe" in model.executable_path


def test_simulation_mode_config():
    model = Model("Test", "exe", "dir")

    # Test evaluation mode (default)
    assert model.simulation_mode == "e"
    assert model.eval_params == [1, "g"]

    # Test MC mode
    model.set_simulation_mode("m", n_runs=500, threshold=0.8, variable="s")
    assert model.simulation_mode == "m"
    assert model.mc_params == [500, 0.8, 100, "s"]

    # Test SCE mode
    model.set_simulation_mode("s", n_loops=10, n_complexes=5)
    assert model.simulation_mode == "s"
    assert model.sce_params == [10, 5, -1, -1, "g"]


def test_objective_function_config():
    model = Model("Test", "exe", "dir")
    model.set_objective_function(2, 0.5, 0.1)
    assert model.obj_func == [2, 0.5, 0.1]


def test_get_results_mock(tmp_path):
    working_dir = tmp_path / "results"
    working_dir.mkdir()
    (working_dir / "Output").mkdir()

    # Create mock output file
    out_file = working_dir / "Output" / "FAO_TimeSeries1.out"
    with open(out_file, "w") as f:
        f.write("Day Month Year theta(-)\n")
        f.write("1 1 2020 0.35\n")
        f.write("2 1 2020 0.34\n")

    fit_file = working_dir / "Output" / "fit_eval.out"
    with open(fit_file, "w") as f:
        f.write("ObjectiveFunction\n")
        f.write("0.95\n")

    from aquimodpy.Components import FAO

    model = Model("Test", "exe", str(working_dir))
    FAO(model, theta_fc=0.4, theta_wp=0.1, Z_r=1000, p=0.5, BFI=0.8)

    results = model.get_results(run_number=1)
    assert "Soil" in results
    assert "Fit" in results
    assert results["Soil"]["theta(-)"].iloc[0] == 0.35
    assert results["Fit"]["ObjectiveFunction"].iloc[0] == 0.95
