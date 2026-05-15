from .Runner import Runner

class EvaluationRunner(Runner):
    """Runner for standard evaluation simulations."""
    def prepare(self):
        print(f"Preparing evaluation for model: {self.model.model_name}")
        # Generate Observations.txt if observations are provided
        if self.model.observations:
            self.model.observations.write_obs_file()
        
        # Logic to generate Input.txt and other files for evaluation mode

    def run(self):
        print(f"Running evaluation for model: {self.model.model_name}")
        # Logic to call the underlying Aquimod executable
