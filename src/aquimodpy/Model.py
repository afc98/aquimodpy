class Model:
    """Main Model class to manage simulation configuration and components."""
    def __init__(self, model_name, executable_path, working_directory, spinup_time=0):
        self.model_name = model_name
        self.executable_path = executable_path
        self.working_directory = working_directory
        self.spinup_time = spinup_time
        self.components = {}
        self.observations = None
        self.runner = None

    def set_runner(self, runner):
        self.runner = runner

    def add_component(self, name, component):
        self.components[name] = component

    def setup(self):
        if not self.runner:
            raise ValueError("Runner must be set before calling setup()")
        self.runner.prepare()

    def run(self):
        if not self.runner:
            raise ValueError("Runner must be set before calling run()")
        self.runner.run()

    def get_results(self):
        # Logic to read output files
        pass
