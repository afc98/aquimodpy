# aquimodpy

A Python wrapper for the British Geological Survey's **AquiMod 2**, a lumped parameter groundwater model.

## Features

- **IDE Support**: Full autocompletion and parameter validation in modern editors.
- **Modular Design**: Support for all Soil Zone (FAO, NSSS, SMAP), Unsaturated Zone (Weibull), and Saturated Zone (Q3K3S1, VKD, SA1D, etc.) components.
- **Automated Configuration**: Generates all required input files (`Input.txt`, `Observations.txt`, and component-specific parameter files) with correct Windows-style formatting for Wine compatibility.
- **Simulation Modes**: Full support for Evaluation, Monte Carlo calibration, and SCE-UA global optimization.
- **Cross-Platform**: Flexible execution support; specify your preferred command prefix (e.g., `["wine"]`, `["box86"]`) for running the Windows binary on non-Windows systems.
- **Data Integration**: Seamless integration with Pandas for observation input and result parsing.

## Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/aquimodpy.git
cd aquimodpy

# Install dependencies (using uv)
uv pip install -e .
```

## Quick Start

```python
import pandas as pd
from aquimodpy import Model, FAO, Weibull, Q3K3S1, Observations, EvaluationRunner

# 1. Initialize the model
model = Model(
    model_name="MySimulation",
    executable_path="~/Documents/AquiMod2/AquiMod2.exe",
    working_directory="./simulation_results",
    exec_prefix=["wine"]  # Use ["wine"] for Linux or [] for native Windows
)

# 2. Add components using named arguments
# Units and special characters are handled automatically!
FAO(
    model, 
    theta_fc=0.4, 
    theta_wp=0.1, 
    Z_r=1000, 
    p=0.5, 
    BFI=0.8
)

Weibull(
    model, 
    k=2.0, 
    lambda_=5.0 # Use lambda_ as 'lambda' is a Python keyword
)

Q3K3S1(
    model, 
    dx=1000, 
    K3=10, 
    K2=5, 
    K1=1, 
    S=0.01, 
    z3=50, 
    z2=40, 
    z1=30, 
    alpha=1
)

# 3. Add observations and map column names
df = pd.read_csv("my_data.csv")
Observations(model, df, {
    "DATE": "date_col",
    "RAIN": "rainfall_mm",
    "PET": "pet_mm",
    "GWL": "gw_level_m"
})

# 4. Configure and run
model.set_runner(EvaluationRunner(model))
model.setup()
model.run()

# 5. Analyze results
results = model.get_results()
print(results['Sat'].head())
```

## Calibration and Optimization

### Monte Carlo Calibration
Provide `[min, max]` lists for parameters you wish to calibrate.
```python
from aquimodpy import CalibrationRunner
model.set_runner(CalibrationRunner(model))
model.set_simulation_mode('m', n_runs=10000, threshold=0.5, variable='g')

# Calibrate Z_r and BFI, keep others fixed
FAO(
    model, 
    theta_fc=0.35, 
    theta_wp=0.1, 
    Z_r=[500, 3000], 
    p=0.5, 
    BFI=[0.1, 0.99]
)
```

### SCE-UA Optimization
```python
model.set_simulation_mode('s', n_loops=100, n_complexes=50, variable='g')
```

## License and Attribution

This library is licensed under the **MIT License**.

This project provides a wrapper for **AquiMod 2**, which is owned by the British Geological Survey (BGS) and is licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). 

Please note that this library does not include the AquiMod 2 binary. You can download the AquiMod 2 software from the [official BGS website](https://www.bgs.ac.uk/technologies/software/aquimod/). Users are responsible for obtaining the binary independently and complying with the terms of the Open Government Licence as specified by the BGS.

