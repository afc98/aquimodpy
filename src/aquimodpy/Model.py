from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
import pandas as pd
import os
import warnings
from .Components import SoilZone, UnsatZone, SatZone

if TYPE_CHECKING:
    from .Components import Component, SoilZone, UnsatZone, SatZone, Observations
    from .Runner import Runner


class Model:
    """Manages simulation configuration, components, and execution.

    Attributes:
        model_name (str): Name of the simulation.
        executable_path (str): Absolute path to the AquiMod 2 binary.
        working_directory (str): Absolute path to the simulation working directory.
        exec_prefix (List[str]): Command prefix for running the binary.
        soil_zone (SoilZone, optional): Soil zone component instance.
        unsat_zone (UnsatZone, optional): Unsaturated zone component instance.
        sat_zone (SatZone, optional): Saturated zone component instance.
        observations (Observations, optional): Observations component instance.
        runner (Runner, optional): Runner instance (e.g., CalibrationRunner, EvaluationRunner).
        simulation_mode (str): 'e' (evaluation), 'm' (Monte Carlo), or 's' (SCE-UA).
        spinup_time (int): Number of days for simulation spin-up.
        obj_func (List[Any]): Objective function ID and parameters.
        output_switches (List[bool]): Which component output files to write [soil, unsat, sat].
        mc_params (List[Any]): Parameters for Monte Carlo simulation.
        sce_params (List[Any]): Parameters for SCE-UA simulation.
        eval_params (List[Any]): Parameters for evaluation simulation.
    """

    def __init__(
        self,
        model_name: str,
        executable_path: str,
        working_directory: str,
        exec_prefix: Optional[List[str]] = None,
        *,
        simulation_mode: str = "e",
        spinup_time: int = 365,
        obj_func: Optional[List[Any]] = None,
        output_switches: Optional[List[bool]] = None,
    ) -> None:
        """Initializes the model.

        Args:
            model_name (str): Name of the simulation.
            executable_path (str): Path to the AquiMod 2 binary.
            working_directory (str): Path to the working directory.
            exec_prefix (List[str], optional): Command prefix for running the binary (e.g., ["wine"]). Defaults to None.
            simulation_mode (str): 'e' (evaluation), 'm' (Monte Carlo), or 's' (SCE-UA). Defaults to 'e'.
            spinup_time (int): Number of days for simulation spin-up. Defaults to 365.
            obj_func (List[Any], optional): Objective function ID and parameters. Defaults to [1].
            output_switches (List[bool], optional): Which component output files to write [soil, unsat, sat]. Defaults to [True, True, True].
        """

        self.model_name: str = model_name
        self.executable_path: str = os.path.abspath(os.path.expanduser(executable_path))
        self.working_directory: str = os.path.abspath(
            os.path.expanduser(working_directory)
        )
        self.exec_prefix: List[str] = exec_prefix if exec_prefix is not None else []

        self.soil_zone: Optional["SoilZone"] = None
        self.unsat_zone: Optional["UnsatZone"] = None
        self.sat_zone: Optional["SatZone"] = None

        self.observations: Optional["Observations"] = None
        self.runner: Optional["Runner"] = None

        # Configuration parameters
        self.simulation_mode: str = simulation_mode
        self.spinup_time: int = spinup_time
        self.obj_func: List[Any] = obj_func if obj_func is not None else [1]
        self.output_switches: List[bool] = (
            output_switches if output_switches is not None else [True, True, True]
        )

        # Simulation specific parameters (defaults)
        self.mc_params: List[Any] = [10000, 0.5, 100, "g"]
        self.sce_params: List[Any] = [100, 50, -1, -1, "g"]
        self.eval_params: List[Any] = [1, "g"]

    def set_runner(self, runner: "Runner") -> None:
        """Sets the runner for the model simulation.

        Args:
            runner: A runner instance (e.g., EvaluationRunner, CalibrationRunner).
        """
        self.runner = runner

    def add_component(self, component: "Component") -> None:
        """Categorizes and stores the component.

        Args:
            component (Component): An instance of a model component (SoilZone, UnsatZone, or SatZone).

        Raises:
            ValueError: If the component type is unknown.
        """

        if isinstance(component, SoilZone):
            if self.soil_zone is not None:
                warnings.warn(
                    f"Replacing existing SoilZone component: {type(self.soil_zone).__name__} with {type(component).__name__}"
                )
            self.soil_zone = component
        elif isinstance(component, UnsatZone):
            if self.unsat_zone is not None:
                warnings.warn(
                    f"Replacing existing UnsatZone component: {type(self.unsat_zone).__name__} with {type(component).__name__}"
                )
            self.unsat_zone = component
        elif isinstance(component, SatZone):
            if self.sat_zone is not None:
                warnings.warn(
                    f"Replacing existing SatZone component: {type(self.sat_zone).__name__} with {type(component).__name__}"
                )
            self.sat_zone = component
        else:
            raise ValueError(f"Unknown component type: {type(component)}")

    def set_simulation_mode(self, mode: str, **kwargs: Any) -> None:
        """Configures simulation mode and its parameters.

        Args:
            mode (str): 'e' (evaluation), 'm' (Monte Carlo), or 's' (SCE-UA).
            **kwargs: Parameters for the chosen mode (e.g., n_runs, threshold, variable).

        Raises:
            ValueError: If an invalid mode is provided.
        """
        if mode not in ["e", "m", "s"]:
            raise ValueError(
                "Mode must be 'e' (evaluation), 'm' (Monte Carlo), or 's' (SCE-UA)"
            )
        self.simulation_mode = mode
        if mode == "m":
            self.mc_params = [
                kwargs.get("n_runs", self.mc_params[0]),
                kwargs.get("threshold", self.mc_params[1]),
                kwargs.get("n_max", self.mc_params[2]),
                kwargs.get("variable", self.mc_params[3]),
            ]
        elif mode == "s":
            self.sce_params = [
                kwargs.get("n_loops", self.sce_params[0]),
                kwargs.get("n_complexes", self.sce_params[1]),
                kwargs.get("n_offspring", self.sce_params[2]),
                kwargs.get("n_evolution", self.sce_params[3]),
                kwargs.get("variable", self.sce_params[4]),
            ]
        elif mode == "e":
            self.eval_params = [
                kwargs.get("n_runs", self.eval_params[0]),
                kwargs.get("variable", self.eval_params[1]),
            ]

    def set_objective_function(self, obj_id: int, *params: Any) -> None:
        """Sets the objective function ID and parameters.

        Args:
            obj_id (int): Objective function ID.
            *params: Objective function parameters.
        """
        self.obj_func = [obj_id, *params]

    def set_output_switches(
        self, soil: bool = True, unsat: bool = True, sat: bool = True
    ) -> None:
        """Sets which component output files should be written.

        Args:
            soil (bool): Write soil output (True/False).
            unsat (bool): Write unsaturated output (True/False).
            sat (bool): Write saturated output (True/False).
        """
        self.output_switches = [soil, unsat, sat]

    def load_parameters(
        self, calibration_results: Dict[str, pd.DataFrame], index: int = 0
    ) -> None:
        """Updates component parameters from calibration results.

        Args:
            calibration_results (Dict[str, pd.DataFrame]): Dictionary of DataFrames returned by get_results().
            index (int, optional): The row index in the results DataFrames to load. Defaults to 0.
        """
        mapping = [
            (self.soil_zone, "Soil_Params"),
            (self.unsat_zone, "Unsat_Params"),
            (self.sat_zone, "Sat_Params"),
        ]

        for comp, key in mapping:
            if comp and key in calibration_results:
                df = calibration_results[key]
                if not df.empty and index < len(df):
                    comp.parameters = {
                        str(k): v for k, v in df.iloc[index].to_dict().items()
                    }
                else:
                    warnings.warn(
                        f"Could not load parameters for {key}: result is empty or index out of range."
                    )

    def setup(self) -> None:
        """Prepares simulation files."""
        if not self.runner:
            raise ValueError("Runner must be set before calling setup()")
        self.runner.prepare()

    def run(self) -> None:
        """Executes the simulation."""
        if not self.runner:
            raise ValueError("Runner must be set before calling run()")
        self.runner.run()

    def get_results(self, run_number: int = 1) -> Dict[str, pd.DataFrame]:
        """Reads output files and returns them as DataFrames.

        In evaluation mode ('e'), it reads time series for the specified run_number.
        In calibration mode ('m' or 's'), it reads the parameter sets and fit metrics.

        Args:
            run_number (int, optional): Run number for time series. Defaults to 1.

        Returns:
            Dict[str, pd.DataFrame]: Dictionary of DataFrames containing model outputs.
        """
        output_dir = os.path.join(self.working_directory, "Output")
        results: Dict[str, pd.DataFrame] = {}

        components = [
            (self.soil_zone, "Soil"),
            (self.unsat_zone, "Unsat"),
            (self.sat_zone, "Sat"),
        ]

        # Read calibration parameter sets if in calibration mode
        if self.simulation_mode in ["m", "s"]:
            for comp, type_name in components:
                if comp:
                    comp_name = comp.__class__.__name__
                    file_name = f"{comp_name}_calib.out"
                    file_path = os.path.join(output_dir, file_name)
                    if os.path.exists(file_path):
                        results[f"{type_name}_Params"] = pd.read_csv(
                            file_path, sep=r"\s+"
                        )

        # Read time series results (only created in evaluation mode or if explicitly requested)
        if self.simulation_mode == "e":
            for comp, type_name in components:
                if comp:
                    comp_name = comp.__class__.__name__
                    file_name = f"{comp_name}_TimeSeries{run_number}.out"
                    file_path = os.path.join(output_dir, file_name)

                    if os.path.exists(file_path):
                        results[type_name] = pd.read_csv(file_path, sep=r"\s+")
                    else:
                        print(f"Warning: Time series file {file_path} not found.")

        # Also read fit_eval.out or fit_calib.out depending on mode
        fit_file = "fit_eval.out" if self.simulation_mode == "e" else "fit_calib.out"
        fit_path = os.path.join(output_dir, fit_file)
        if os.path.exists(fit_path):
            results["Fit"] = pd.read_csv(fit_path, sep=r"\s+")

        return results
