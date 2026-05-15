class Runner:
    """Base class for all simulation runners."""
    def __init__(self, model):
        self.model = model

    def prepare(self):
        """Prepare the simulation (e.g., generate input files)."""
        raise NotImplementedError("Subclasses must implement prepare()")

    def run(self):
        """Execute the simulation."""
        raise NotImplementedError("Subclasses must implement run()")
