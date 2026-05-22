import pytest
import os
import pandas as pd
import warnings
from aquimodpy.Model import Model
from aquimodpy.Components import FAO, Weibull, Q1K1S1


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
    assert model.spinup_time == 365
    assert model.obj_func == [1]
    assert model.output_switches == [True, True, True]

    # Test MC mode
    model.set_simulation_mode("m", n_runs=500, threshold=0.8, variable="s")
    assert model.simulation_mode == "m"
    assert model.mc_params == [500, 0.8, 100, "s"]

    # Test SCE mode
    model.set_simulation_mode("s", n_loops=10, n_complexes=5)
    assert model.simulation_mode == "s"
    assert model.sce_params == [10, 5, -1, -1, "g"]


def test_model_invalid_mode():
    model = Model("Test", "exe", "dir")
    with pytest.raises(ValueError, match="Mode must be 'e'"):
        model.set_simulation_mode("invalid")


def test_model_set_simulation_mode_params():
    model = Model("Test", "exe", "dir")

    # Test SCE mode
    model.set_simulation_mode(
        "s", n_loops=20, n_complexes=10, n_offspring=5, n_evolution=2, variable="q"
    )
    assert model.sce_params == [20, 10, 5, 2, "q"]

    # Test Evaluation mode
    model.set_simulation_mode("e", n_runs=5, variable="h")
    assert model.eval_params == [5, "h"]


def test_model_set_output_switches():
    model = Model("Test", "exe", "dir")
    model.set_output_switches(soil=False, unsat=True, sat=False)
    assert model.output_switches == [False, True, False]


def test_model_load_parameters_success():
    model = Model("Test", "exe", "dir")
    fao = FAO(model, 0.4, 0.1, 1000, 0.5, 0.8)
    df = pd.DataFrame(
        [
            {
                "theta_fc(-)": 0.35,
                "theta_wp(-)": 0.12,
                "Z_r(mm)": 1100,
                "p(-)": 0.55,
                "BFI(-)": 0.85,
            }
        ]
    )
    model.load_parameters({"Soil_Params": df}, index=0)
    assert fao.parameters["theta_fc(-)"] == 0.35
    assert fao.parameters["Z_r(mm)"] == 1100


def test_model_load_parameters_warnings():
    model = Model("Test", "exe", "dir")
    FAO(model, 0.4, 0.1, 1000, 0.5, 0.8)

    # Empty results
    with pytest.warns(UserWarning, match="Could not load parameters"):
        model.load_parameters({"Soil_Params": pd.DataFrame()})

    # Index out of range
    df = pd.DataFrame([{"theta_fc(-)": 0.35}])
    with pytest.warns(UserWarning, match="Could not load parameters"):
        model.load_parameters({"Soil_Params": df}, index=5)


def test_model_setup_run_no_runner():
    model = Model("Test", "exe", "dir")
    with pytest.raises(ValueError, match="Runner must be set before calling setup"):
        model.setup()
    with pytest.raises(ValueError, match="Runner must be set before calling run"):
        model.run()


def test_model_run_success():
    model = Model("Test", "exe", "dir")

    class MockRunner:
        def __init__(self) -> None:
            self.called = False

        def run(self) -> None:
            self.called = True

    runner = MockRunner()
    model.set_runner(runner)  # type: ignore
    model.run()
    assert runner.called


def test_model_add_invalid_component():
    model = Model("Test", "exe", "dir")

    class NotAComponent:
        pass

    with pytest.raises(ValueError, match="Unknown component type"):
        model.add_component(NotAComponent())  # type: ignore


def test_model_replacement_warnings():
    model = Model("Test", "exe", "dir")

    # SoilZone replacement
    FAO(model, 0.4, 0.1, 1000, 0.5, 0.8)
    with pytest.warns(UserWarning, match="Replacing existing SoilZone component"):
        FAO(model, 0.3, 0.1, 1000, 0.5, 0.8)

    # UnsatZone replacement
    Weibull(model, 2.0, 5.0)
    with pytest.warns(UserWarning, match="Replacing existing UnsatZone component"):
        Weibull(model, 3.0, 6.0)

    # SatZone replacement
    Q1K1S1(model, 1000, 0.5, 0.01, 10, 1)
    with pytest.warns(UserWarning, match="Replacing existing SatZone component"):
        Q1K1S1(model, 2000, 0.6, 0.02, 20, 1)


def test_model_init_with_params():
    model = Model(
        "Test",
        "exe",
        "dir",
        simulation_mode="m",
        spinup_time=500,
        obj_func=[2, 0.5],
        output_switches=[True, False, True],
    )
    assert model.simulation_mode == "m"
    assert model.spinup_time == 500
    assert model.obj_func == [2, 0.5]
    assert model.output_switches == [True, False, True]


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


def test_model_get_results_calibration(tmp_path):
    model = Model("Test", "exe", str(tmp_path))
    FAO(model, 0.4, 0.1, 1000, 0.5, 0.8)
    model.simulation_mode = "m"

    output_dir = os.path.join(tmp_path, "Output")
    os.makedirs(output_dir, exist_ok=True)

    # Create mock calib output
    calib_out = os.path.join(output_dir, "FAO_calib.out")
    with open(calib_out, "w") as f:
        f.write("theta_fc(-) BFI(-)\n")
        f.write("0.4 0.8\n")

    fit_out = os.path.join(output_dir, "fit_calib.out")
    with open(fit_out, "w") as f:
        f.write("Obj\n0.9\n")

    results = model.get_results()
    assert "Soil_Params" in results
    assert "Fit" in results
    assert results["Soil_Params"]["theta_fc(-)"].iloc[0] == 0.4


def test_model_get_results_file_not_found(tmp_path, capsys):
    model = Model("Test", "exe", str(tmp_path))
    FAO(model, 0.4, 0.1, 1000, 0.5, 0.8)
    model.simulation_mode = "e"

    # Create Output dir but no file
    os.makedirs(os.path.join(tmp_path, "Output"), exist_ok=True)

    results = model.get_results(run_number=99)
    captured = capsys.readouterr()
    assert "Warning: Time series file" in captured.out
    assert "Soil" not in results
