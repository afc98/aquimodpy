import pandas as pd
import os

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
    """Handles model observations and generates the required input file."""

    def __init__(self, model, obs_df, columns):
        """
        Initialize Observations.

        Args:
            model: The Model instance.
            obs_df: Pandas DataFrame containing observations.
            columns: Dictionary mapping required model columns to user DataFrame columns.
                     Required keys: DATE, RAIN, PET, SOIL_VWC, GWL, ABS.
        """
        self.model = model
        self.obs_df = obs_df.copy()
        self.columns = columns
        self.model.observations = self

    def write_obs_file(self):
        """Processes observations and writes them to 'Observations.txt' in the working directory."""
        
        # Create a working copy for processing
        df = self.obs_df.copy()

        # Map user columns to standard names used by the model
        rename_map = {v: k for k, v in self.columns.items()}
        df = df.rename(columns=rename_map)

        # Required columns for the output file
        headings = [
            "DAY",
            "MONTH",
            "YEAR",
            "RAIN",
            "PET",
            "SOIL_VWC",
            "GWL",
            "ABS"
        ]

        # Ensure DATE is present and convert to datetime
        if "DATE" not in df.columns:
            raise KeyError(
                f"Required column 'DATE' missing from DataFrame. "
                f"Ensure it is correctly mapped in the 'columns' dictionary."
            )
        
        df["DATE"] = pd.to_datetime(df["DATE"])

        # Create date component columns
        df["DAY"] = df["DATE"].dt.day
        df["MONTH"] = df["DATE"].dt.month
        df["YEAR"] = df["DATE"].dt.year

        # Ensure all required headings are present, fill missing with -9999
        for col in headings:
            if col not in df.columns:
                df[col] = -9999
        
        # Fill existing NaNs with -9999
        df = df.fillna(-9999)

        # Define output file path
        out_file = os.path.join(
            self.model.working_directory,
            "Observations.txt"
        )

        # Write to file
        with open(out_file, "w", newline='') as f:
            f.write("NUMBER OF OBSERVATIONS\n")
            f.write(f"{len(df)}\n")
            # Use to_csv for performance and reliability
            df[headings].to_csv(f, sep="\t", index=False, header=True)
