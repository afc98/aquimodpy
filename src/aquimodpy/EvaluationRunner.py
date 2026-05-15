from .Runner import Runner

class EvaluationRunner(Runner):
    """Runner for standard evaluation simulations."""
    def prepare(self):
        print(f"Preparing evaluation for model: {self.model.model_name}")
        # Logic to generate Input.txt and other files for evaluation mode

    def run(self):
        print(f"Running evaluation for model: {self.model.model_name}")
        # Logic to call the underlying Aquimod executable
