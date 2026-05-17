from typing import TYPE_CHECKING
from .Runner import Runner
import os

if TYPE_CHECKING:
    from .Model import Model


class CalibrationRunner(Runner):
    """Runner for Monte Carlo and SCE-UA calibration simulations."""

    def prepare(self) -> None:
        """Prepares calibration simulation."""
        super().prepare()
        # Generate component calibration files
        self.write_component_calib_files()

    def write_component_calib_files(self) -> None:
        """Writes *_calib.txt files in the Calibration directory."""
        calib_dir = os.path.join(self.model.working_directory, "Calibration")

        components = [self.model.soil_zone, self.model.unsat_zone, self.model.sat_zone]

        for comp in components:
            if comp:
                comp_name = comp.__class__.__name__
                file_path = os.path.join(calib_dir, f"{comp_name}_calib.txt")

                # Ensure parameters are written in the correct order specified in REQUIRED_PARAMETERS
                if isinstance(comp.parameters, dict):
                    with open(file_path, "w", newline="") as f:
                        for param_name in comp.REQUIRED_PARAMETERS:
                            bounds = comp.parameters.get(param_name)
                            if bounds is None:
                                continue  # Should not happen due to validation

                            # Ensure bounds is a list/tuple of two values
                            if (
                                not isinstance(bounds, (list, tuple))
                                or len(bounds) != 2
                            ):
                                # If it's a single value, treat it as fixed
                                b = [bounds, bounds]
                            else:
                                b = list(bounds)

                            f.write(f"{param_name}\r\n")
                            f.write(f"{b[0]} {b[1]}\r\n\r\n")
