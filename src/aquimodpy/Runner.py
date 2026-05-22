from typing import TYPE_CHECKING
import os
import subprocess

if TYPE_CHECKING:
    from .Model import Model


class Runner:
    """Base class for all simulation runners.

    Attributes:
        model (Model): The Model instance.
    """

    def __init__(self, model: "Model") -> None:
        """Initializes the runner with a model instance.

        Args:
            model (Model): The Model instance.
        """
        self.model: "Model" = model

    def prepare(self) -> None:
        """Prepares the simulation (e.g., generates input files)."""
        # Ensure directories exist
        for folder in ["Evaluation", "Calibration", "Output"]:
            os.makedirs(
                os.path.join(self.model.working_directory, folder), exist_ok=True
            )

        # Generate Observations.txt if observations are provided
        if self.model.observations:
            self.model.observations.write_obs_file()

        # Generate Input.txt
        self.write_input_file()

    def write_input_file(self) -> None:
        """Writes the Input.txt file."""
        file_path = os.path.join(self.model.working_directory, "Input.txt")

        # Determine component IDs
        soil_id = self.model.soil_zone.component_id if self.model.soil_zone else 0
        unsat_id = self.model.unsat_zone.component_id if self.model.unsat_zone else 0
        sat_id = self.model.sat_zone.component_id if self.model.sat_zone else 0

        # Format output switches (Y/N) with spaces
        switches = " ".join(["Y" if s else "N" for s in self.model.output_switches])

        lines = [
            "Component IDs",
            f"{soil_id} {unsat_id} {sat_id}",
            "",
            "Simulation mode",
            f"{self.model.simulation_mode}",
            "",
            "Monte Carlo parameters",
            " ".join(map(str, self.model.mc_params)),
            "",
            "SCE-UA parameters",
            " ".join(map(str, self.model.sce_params)),
            "",
            "Evaluation parameters",
            " ".join(map(str, self.model.eval_params)),
            "",
            "Objective function and parameters",
            " ".join(map(str, self.model.obj_func)),
            "",
            "Spin-up period",
            f"{self.model.spinup_time}",
            "",
            "Write model output files",
            f"{switches}",
        ]

        # Use CRLF for Windows/Wine compatibility
        with open(file_path, "w", newline="") as f:
            f.write("\r\n".join(lines) + "\r\n")

    def run(self) -> None:
        """Executes the simulation."""
        print(
            f"Running {self.model.simulation_mode} for model: {self.model.model_name}"
        )

        command = self.model.exec_prefix + [
            self.model.executable_path,
            self.model.working_directory,
        ]

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error running Aquimod 2: {e.stderr}")
            print(f"Output: {e.output}")
            raise
