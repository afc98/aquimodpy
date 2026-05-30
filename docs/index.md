# Welcome to aquimodpy

`aquimodpy` is a Python wrapper for the British Geological Survey's **AquiMod 2**, a lumped parameter groundwater model. It provides a clean, Pythonic interface to define complex hydrogeological models.

## Overview
This library allows you to:
- Define soil, unsaturated, and saturated zone components using intuitive named arguments.
- Seamlessly integrate with Pandas for input data and model observation.
- Manage simulation runs (evaluation, Monte Carlo calibration, and SCE-UA optimisation) through dedicated runner classes.
- Run the original AquiMod 2 Windows binary on Linux environments using Wine.

## Workflow Example: Calibration to Evaluation

This example demonstrates a complete real-world workflow: defining parameter ranges, running a Monte Carlo calibration, selecting the best parameter set, and performing a final evaluation.

```python
import pandas as pd
from aquimodpy import Model, FAO, Weibull, Q3K3S1, Observations, CalibrationRunner, EvaluationRunner

# 1. Initialise Model & Define Components
# We specify ranges [min, max] for parameters we want to calibrate
model = Model(
    model_name="MySimulation",
    executable_path="~/AquiMod2/AquiMod2.exe",
    working_directory="./sim_results",
    exec_prefix=["wine"] # Required for Linux
)

FAO(model, theta_fc=0.3, theta_wp=0.1, Z_r=[500, 2500], p=0.5, BFI=[0.1, 0.9])
Weibull(model, k=[0.5, 5.0], lambda_=10.0)
Q3K3S1(model, dx=1000, K3=10, K2=5, K1=1, S=[1e-4, 1e-2], z3=50, z2=40, z1=30, alpha=1)

# 2. Load Forcing Data and Observations
df = pd.read_csv("my_data.csv", parse_dates=["date"])
Observations(model, df, {
    "DATE": "date", 
    "RAIN": "rainfall_mm", 
    "PET": "pet_mm", 
    "GWL": "observed_gwl_m"
})

# 3. Step 1: Run Monte Carlo Calibration
model.set_runner(CalibrationRunner(model))
model.set_simulation_mode('m', n_runs=10000)
model.setup()
model.run()

# 4. Step 2: Load the Best Parameter Set
# Find the run with the highest Nash-Sutcliffe Efficiency (NSE)
calib_results = model.get_results()
best_run_idx = calib_results['Fit']['NSE'].idxmax()
model.load_parameters(calib_results, index=best_run_idx)

# 5. Step 3: Run Final Evaluation (Historical Simulation)
model.set_runner(EvaluationRunner(model))
model.set_simulation_mode('e')
model.setup()
model.run()

# 6. Analyse Results
results = model.get_results()
print(f"Optimal parameters loaded. NSE: {calib_results['Fit']['NSE'].max():.2f}")
print(results['Sat'].head())
```


## API Reference
Navigate through the core components of the library:

- [Model Configuration](api.md#aquimodpy.Model)
- [Observation Handling](api.md#aquimodpy.Components.Observations)
- [Soil Components](api.md#aquimodpy.Components.FAO)
- [Unsaturated Zone](api.md#aquimodpy.Components.Weibull)
- [Saturated Zone](api.md#aquimodpy.Components.Q3K3S1)
- [Simulation Runners](api.md#aquimodpy.EvaluationRunner)
