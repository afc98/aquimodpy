# aquimodpy

[![PyPI version](https://img.shields.io/pypi/v/aquimodpy.svg)](https://pypi.org/project/aquimodpy/)
[![Python versions](https://img.shields.io/pypi/pyversions/aquimodpy.svg)](https://pypi.org/project/aquimodpy/)
[![CI status](https://github.com/afc98/aquimodpy/actions/workflows/ci.yml/badge.svg)](https://github.com/afc98/aquimodpy/actions/workflows/ci.yml)
[![License](https://img.shields.io/pypi/l/aquimodpy.svg)](https://github.com/afc98/aquimodpy/blob/master/LICENSE)

A Python wrapper for the British Geological Survey's **AquiMod 2**, a lumped parameter groundwater model.

## Features
- **IDE Support**: Full autocompletion and parameter validation in modern editors.
- **Modular Design**: Support for all Soil Zone (FAO, NSSS, SMAP), Unsaturated Zone (Weibull), and Saturated Zone (Q3K3S1, VKD, SA1D, etc.) components.
- **Automated Configuration**: Generates all required input files (`Input.txt`, `Observations.txt`, and component-specific parameter files) with correct Windows-style formatting for Wine compatibility.
- **Simulation Modes**: Full support for Evaluation, Monte Carlo calibration, and SCE-UA global optimisation.
- **Cross-Platform**: Flexible execution support; specify your preferred command prefix (e.g., `["wine"]`, `["box86"]`) for running the Windows binary on non-Windows systems.
- **Data Integration**: Seamless integration with Pandas for observation input and result parsing.

## Installation
```bash
# Using pip
pip install aquimodpy

# Using uv
uv add aquimodpy
```

## Documentation
* [Latest release](https://afc98.github.io/aquimodpy/)

## Workflow Example: Calibration to Evaluation

This example demonstrates a complete real-world workflow: defining parameter ranges, running a Monte Carlo calibration, selecting the best parameter set, and performing a final evaluation.

```python
import pandas as pd
import matplotlib.pyplot as plt
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

# 6. Analyse and Plot Results
results = model.get_results()
sim_gwl = results['Sat']  # Saturated zone time series

print(f"Optimal parameters loaded. NSE: {calib_results['Fit']['NSE'].max():.2f}")
print(sim_gwl.head())

# Optional: Plotting with Matplotlib
# plt.plot(df['date'], df['observed_gwl_m'], 'k.', label='Observed')
# plt.plot(df['date'], sim_gwl['Head(m)'], 'r-', label='Simulated')
# plt.show()
```


## License and Attribution
This library is licensed under the **MIT License**.

This project provides a wrapper for **AquiMod 2**, which is owned by the British Geological Survey (BGS) and is licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

Please note that this library does not include the AquiMod 2 binary. You can download the AquiMod 2 software from the [official BGS website](https://www.bgs.ac.uk/technologies/software/aquimod/). Users are responsible for obtaining the binary independently and complying with the terms of the Open Government Licence as specified by the BGS.
