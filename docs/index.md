# Welcome to aquimodpy

`aquimodpy` is a Python wrapper for the British Geological Survey's **AquiMod 2**, a lumped parameter groundwater model. It provides a clean, Pythonic interface to define complex hydrogeological models.

## Overview
This library allows you to:
- Define soil, unsaturated, and saturated zone components using intuitive named arguments.
- Seamlessly integrate with Pandas for input data and model observation.
- Manage simulation runs (evaluation, Monte Carlo calibration, and SCE-UA optimization) through dedicated runner classes.
- Run the original AquiMod 2 Windows binary on Linux environments using Wine.

## Quick Start
```python
import pandas as pd
from aquimodpy import Model, FAO, Weibull, Q3K3S1, Observations, EvaluationRunner

# Initialize the model
model = Model("MySim", "~/path/to/AquiMod2.exe", "./results")

# Configure components
FAO(model, theta_fc=0.4, theta_wp=0.1, Z_r=1000, p=0.5, BFI=0.8)
Weibull(model, k=2.0, lambda_=5.0)
Q3K3S1(model, dx=1000, K3=10, K2=5, K1=1, S=0.01, z3=50, z2=40, z1=30, alpha=1)

# Set observations and run
df = pd.read_csv("data.csv")
Observations(model, df, {"DATE": "date", "RAIN": "rain", "PET": "pet", "GWL": "gwl"})

model.set_runner(EvaluationRunner(model))
model.run()
```

## API Reference
Navigate through the core components of the library:

- [Model Configuration](api.md#aquimodpy.Model)
- [Observation Handling](api.md#aquimodpy.Components.Observations)
- [Soil Components](api.md#aquimodpy.Components.FAO)
- [Unsaturated Zone](api.md#aquimodpy.Components.Weibull)
- [Saturated Zone](api.md#aquimodpy.Components.Q3K3S1)
- [Simulation Runners](api.md#aquimodpy.EvaluationRunner)
