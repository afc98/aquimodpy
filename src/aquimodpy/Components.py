class Component:
    """Base class for model components."""
    def __init__(self, model, component_type, parameters):
        self.model = model
        self.component_type = component_type
        self.parameters = parameters
        self.model.add_component(self.__class__.__name__, self)

class SoilZone(Component):
    def __init__(self, model, component, parameters):
        super().__init__(model, component, parameters)

class UnsatZone(Component):
    def __init__(self, model, component, parameters):
        super().__init__(model, component, parameters)

class SatZone(Component):
    def __init__(self, model, component, parameters):
        super().__init__(model, component, parameters)

class Observations:
    def __init__(self, model, obs_df, columns):
        self.model = model
        self.obs_df = obs_df
        self.columns = columns
        self.model.observations = self
