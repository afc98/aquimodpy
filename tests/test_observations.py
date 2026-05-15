import pandas as pd
import os
import pytest
from aquimodpy import Model, Observations

def test_observations_modifies_df_in_place(tmp_path):
    # Setup
    working_dir = tmp_path / "working"
    working_dir.mkdir()
    
    model = Model("TestModel", "fake_path", str(working_dir))
    
    data = {
        "date": ["2020-01-01", "2020-01-02"],
        "rain": [1.0, 2.0],
        "pet": [0.5, 0.6],
        "soil": [0.1, 0.2],
        "gwl": [10.0, 11.0],
        "abs": [0.0, 0.0]
    }
    df = pd.DataFrame(data)
    df_original = df.copy()
    
    columns = {
        "DATE": "date",
        "RAIN": "rain",
        "PET": "pet",
        "SOIL_VWC": "soil",
        "GWL": "gwl",
        "ABS": "abs"
    }
    
    obs = Observations(model, df, columns)
    obs.write_obs_file()
    
    # Check if original df was NOT modified
    # 1. Date column should still be object/string if it was originally
    assert not pd.api.types.is_datetime64_any_dtype(df["date"])
    # 2. New columns should NOT be added
    assert "DAY" not in df.columns
    assert "MONTH" not in df.columns
    assert "YEAR" not in df.columns
    
    # This confirms in-place modification, which is usually undesirable in a library
    # unless explicitly documented.

def test_observations_write_file_content(tmp_path):
    working_dir = tmp_path / "working"
    working_dir.mkdir()
    
    model = Model("TestModel", "fake_path", str(working_dir))
    
    data = {
        "date": ["2020-01-01", "2020-01-02"],
        "rain": [1.0, None], # Testing fillna
        "pet": [0.5, 0.6],
        "soil": [0.1, 0.2],
        "gwl": [10.0, 11.0],
        "abs": [0.0, 0.0]
    }
    df = pd.DataFrame(data)
    
    columns = {
        "DATE": "date",
        "RAIN": "rain",
        "PET": "pet",
        "SOIL_VWC": "soil",
        "GWL": "gwl",
        "ABS": "abs"
    }
    
    obs = Observations(model, df, columns)
    obs.write_obs_file()
    
    out_file = working_dir / "Observations.txt"
    assert out_file.exists()
    
    with open(out_file, "r") as f:
        lines = f.readlines()
        
    assert lines[0].strip() == "NUMBER OF OBSERVATIONS"
    assert lines[1].strip() == "2"
    assert "DAY\tMONTH\tYEAR\tRAIN\tPET\tSOIL_VWC\tGWL\tABS" in lines[2]
    # Check fillna
    assert "-9999" in lines[4]
