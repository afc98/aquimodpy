import pytest
import pandas as pd
import os
from aquimodpy.Model import Model
from aquimodpy.Components import Observations


def test_observations_mapping(tmp_path):
    model = Model("Test", "exe", str(tmp_path))

    dates = pd.date_range("2020-01-01", periods=3)
    df = pd.DataFrame(
        {
            "my_date": dates,
            "precip": [1, 2, 3],
            "evap": [0.1, 0.2, 0.3],
            "level": [10, 11, 12],
        }
    )

    obs = Observations(
        model, df, {"DATE": "my_date", "RAIN": "precip", "PET": "evap", "GWL": "level"}
    )

    obs.write_obs_file()

    obs_file = tmp_path / "Observations.txt"
    assert os.path.exists(obs_file)

    # Skip the first two comment/count lines
    with open(obs_file, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    assert "NUMBER OF OBSERVATIONS" in lines[0]
    assert "3" == lines[1]

    # Parse the data section
    # The columns are on line 2 (0-indexed)
    from io import StringIO

    data_str = "\n".join(lines[2:])
    read_df = pd.read_csv(StringIO(data_str), sep=r"\s+")

    assert "ABS" in read_df.columns
    assert "SOIL_VWC" in read_df.columns
    assert read_df["ABS"].iloc[0] == 0
    assert read_df["RAIN"].iloc[0] == 1


def test_observations_missing_required_columns():
    model = Model("Test", "exe", "dir")
    df = pd.DataFrame(
        {
            "DATE": pd.date_range("2020-01-01", periods=2),
            "RAIN": [1, 2],
            "PET": [0.1, 0.2],
        }
    )

    # Missing RAIN in mapping
    with pytest.raises(KeyError, match="Required key 'RAIN' missing"):
        Observations(model, df, {"DATE": "DATE", "PET": "PET"})

    # Missing PET in mapping
    with pytest.raises(KeyError, match="Required key 'PET' missing"):
        Observations(model, df, {"DATE": "DATE", "RAIN": "RAIN"})


def test_observations_nans_in_required_columns(tmp_path):
    model = Model("Test", "exe", str(tmp_path))
    df = pd.DataFrame(
        {
            "DATE": pd.date_range("2020-01-01", periods=2),
            "RAIN": [1, None],
            "PET": [0.1, 0.2],
        }
    )

    obs = Observations(model, df, {"DATE": "DATE", "RAIN": "RAIN", "PET": "PET"})
    with pytest.raises(ValueError, match="Column 'RAIN' contains missing values"):
        obs.write_obs_file()


def test_observations_missing_date():
    model = Model("Test", "exe", "dir")
    df = pd.DataFrame({"RAIN": [1, 2]})
    # Now it should raise at __init__
    with pytest.raises(KeyError, match="Required key 'DATE' missing"):
        Observations(model, df, {"RAIN": "RAIN"})

    with pytest.raises(KeyError, match="Mapped DATE column 'DATE' missing"):
        Observations(model, df, {"DATE": "DATE"})


def test_observations_invalid_date_type(tmp_path):
    model = Model("Test", "exe", str(tmp_path))
    df = pd.DataFrame(
        {"DATE": ["not-a-date", "2020-01-01"], "RAIN": [1, 2], "PET": [0.1, 0.2]}
    )
    obs = Observations(model, df, {"DATE": "DATE", "RAIN": "RAIN", "PET": "PET"})
    with pytest.raises((ValueError, TypeError)):
        obs.write_obs_file()


def test_observations_invalid_numeric_type(tmp_path):
    model = Model("Test", "exe", str(tmp_path))
    # RAIN is string
    df = pd.DataFrame(
        {
            "DATE": pd.date_range("2020-01-01", periods=2),
            "RAIN": ["high", 2],
            "PET": [0.1, 0.2],
        }
    )
    obs = Observations(model, df, {"DATE": "DATE", "RAIN": "RAIN", "PET": "PET"})
    with pytest.raises(TypeError, match="Column 'RAIN' must be numeric"):
        obs.write_obs_file()

    # Optional column GWL is string
    df2 = pd.DataFrame(
        {
            "DATE": pd.date_range("2020-01-01", periods=2),
            "RAIN": [1, 2],
            "PET": [0.1, 0.2],
            "GWL": ["A", "B"],
        }
    )
    obs2 = Observations(
        model, df2, {"DATE": "DATE", "RAIN": "RAIN", "PET": "PET", "GWL": "GWL"}
    )
    with pytest.raises(TypeError, match="Column 'GWL' must be numeric"):
        obs2.write_obs_file()
