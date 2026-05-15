# aquimodpy

aquimodpy is a python package that streamlines the process of running the Aquifer Modelling in Python (AQUIMODPY) model. It provides a user-friendly interface for setting up, running, and analyzing AQUIMODPY simulations.

## Installation
You can install aquimodpy using pip:

```bash
pip install aquimodpy
```

## Usage
Here's a simple example of how to use aquimodpy to run an AQUIMODPY simulation:

```python
import aquimodpy as aq

# Create an instance of the Model class
model = aq.Model(
    model_name='MyAquimodModel',
    executable_path='path/to/aquimod/executable',
    working_directory='path/to/working/directory',
    spinup_time=365,
    )

runner = aq.EvaluationRunner(model=model)

# Set up the soil zone module
soil_zone = aq.SoilZone(
    model=model,
    component="FAO",
    parameters={
        "0fc": 0.5, # Soil volumetric water content at field capacity
        "0wp": 0.5, # Soil volumetric water content at wilting point
        "Zr": 500,  # Maximum root depth of catchment vegetation (mm)
        "p": 0.5,   # Depletion factor of catchment vegetation
        "BFI": 0.5, # Catchment baseflow index
    })

# Set up the unsaturated zone module
unsat_zone = aq.UnsatZone(
    model=model,
    component="Weibull",
    parameters={
        "k": 3,        # Weibull shape parameter
        "lambda": 0.5, # Weibull scale parameter
    })

# Set up the saturated zone module
sat_zone = aq.SatZone(
    model=model,
    component="Q1T1S1",
    parameters={
        "delta_x": 3000, # Catchment length (m)
        "T1": 100,       # Transmissivity (m^2/day)
        "S": 0.01,       # Storage coefficient
        "z1": 100,       # Outlet elevation
    })

# Set up observations
obs = aq.Observations(
    model=model,
    obs_df=pd.load_csv('path/to/observations.csv'),
    columns={
        "DATE": "DATE",
        "RAIN": "RAIN",
        "PET": "PET",
        "SOIL_VWC": "SOIL_WC", # Map model's SOIL_VWC to user's SOIL_WC
        "GWL": "GWL",
        "ABS": "ABS",
    })

# Run the simulation
model.setup()
model.run()

# Analyze the results
results = model.get_results()
print(results)
```

