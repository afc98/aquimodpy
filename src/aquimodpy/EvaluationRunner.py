from typing import TYPE_CHECKING
from .Runner import Runner
import os

if TYPE_CHECKING:
    from .Model import Model


class EvaluationRunner(Runner):
    """Runner for standard evaluation simulations."""

    def prepare(self) -> None:
        """Prepares evaluation simulation."""
        super().prepare()
        # Generate component evaluation files
        self.write_component_eval_files()

    def write_component_eval_files(self) -> None:
        """Writes *_eval.txt files in the Evaluation directory."""
        eval_dir = os.path.join(self.model.working_directory, "Evaluation")

        components = [self.model.soil_zone, self.model.unsat_zone, self.model.sat_zone]

        for comp in components:
            if comp:
                comp_name = comp.__class__.__name__
                file_path = os.path.join(eval_dir, f"{comp_name}_eval.txt")

                if isinstance(comp.parameters, dict):
                    # Single parameter set - use REQUIRED_PARAMETERS order
                    headers = comp.REQUIRED_PARAMETERS
                    values = [str(comp.parameters.get(h)) for h in headers]
                    with open(file_path, "w", newline="") as f:
                        f.write("\t".join(headers) + "\r\n")
                        f.write("\t".join(values) + "\r\n")
                elif isinstance(comp.parameters, list):
                    # Multiple parameter sets (list of dicts)
                    if not comp.parameters:
                        continue
                    headers = comp.REQUIRED_PARAMETERS
                    with open(file_path, "w", newline="") as f:
                        f.write("\t".join(headers) + "\r\n")
                        for p_set in comp.parameters:
                            if isinstance(p_set, dict):
                                values = [str(p_set.get(h)) for h in headers]
                                f.write("\t".join(values) + "\r\n")
                # DataFrame support could be added here too
