from typing import Any, Dict, List, TYPE_CHECKING
import pandas as pd
import os

if TYPE_CHECKING:
    from .Model import Model


class Component:
    """Base class for all model components.

    Attributes:
        model (Model): The Model instance.
        component_id (int): Unique identifier for the component.
        parameters (Dict[str, Any]): Dictionary of component parameters.
    """

    MAP: Dict[str, str] = {}
    REQUIRED_PARAMETERS: List[str] = []

    def __init__(self, model: "Model", component_id: int, **kwargs: Any) -> None:
        """Initializes a new component and registers it with the model.

        Args:
            model (Model): The Model instance.
            component_id (int): Unique identifier for the component.
            **kwargs: Component parameters as named arguments.
        """
        self.model: "Model" = model
        self.component_id: int = component_id
        self.parameters: Dict[str, Any] = {}

        # Map clean names to Aquimod names
        for clean_name, value in kwargs.items():
            if clean_name in self.MAP:
                self.parameters[self.MAP[clean_name]] = value
            else:
                # Allow passing the "unfriendly" name directly too
                self.parameters[clean_name] = value

        # Basic validation
        missing = [
            req for req in self.REQUIRED_PARAMETERS if req not in self.parameters
        ]
        if missing:
            raise ValueError(
                f"Missing required parameters for {self.__class__.__name__}: {missing}"
            )

        self.model.add_component(self)


class SoilZone(Component):
    """Base class for soil zone components."""

    pass


class FAO(SoilZone):
    """Soil FAO component."""

    REQUIRED_PARAMETERS = ["theta_fc(-)", "theta_wp(-)", "Z_r(mm)", "p(-)", "BFI(-)"]
    MAP = {
        "theta_fc": "theta_fc(-)",
        "theta_wp": "theta_wp(-)",
        "Z_r": "Z_r(mm)",
        "p": "p(-)",
        "BFI": "BFI(-)",
    }

    def __init__(
        self,
        model: "Model",
        theta_fc: float,
        theta_wp: float,
        Z_r: float,
        p: float,
        BFI: float,
    ) -> None:
        """Initializes the FAO soil component.

        Args:
            model (Model): The Model instance.
            theta_fc: Field capacity moisture content (-).
            theta_wp: Wilting point moisture content (-).
            Z_r: Rooting depth (mm).
            p: Fraction of available soil water (-).
            BFI: Baseflow index (-).
        """
        super().__init__(
            model, 1, theta_fc=theta_fc, theta_wp=theta_wp, Z_r=Z_r, p=p, BFI=BFI
        )


class NSSS(SoilZone):
    """NSSS soil component."""

    REQUIRED_PARAMETERS = [
        "theta_fc(-)",
        "theta_wp(-)",
        "Z_r(mm)",
        "FRACSTOR(-)",
        "p(-)",
        "BFI(-)",
    ]
    MAP = {
        "theta_fc": "theta_fc(-)",
        "theta_wp": "theta_wp(-)",
        "Z_r": "Z_r(mm)",
        "fracstor": "FRACSTOR(-)",
        "p": "p(-)",
        "BFI": "BFI(-)",
    }

    def __init__(
        self,
        model: "Model",
        theta_fc: float,
        theta_wp: float,
        Z_r: float,
        fracstor: float,
        p: float,
        BFI: float,
    ) -> None:
        """Initializes the NSSS soil component.

        Args:
            model: The Model instance.
            theta_fc: Field capacity moisture content (-).
            theta_wp: Wilting point moisture content (-).
            Z_r: Rooting depth (mm).
            fracstor: Fraction of soil moisture that can be stored (-).
            p: Fraction of available soil water (-).
            BFI: Baseflow index (-).
        """
        super().__init__(
            model,
            2,
            theta_fc=theta_fc,
            theta_wp=theta_wp,
            Z_r=Z_r,
            fracstor=fracstor,
            p=p,
            BFI=BFI,
        )


class SMAP(SoilZone):
    """SMAP soil component."""

    REQUIRED_PARAMETERS = [
        "theta_fc(-)",
        "theta_wp(-)",
        "Z_r(mm)",
        "q_ic(mm d-1)",
        "K_s(m d-1)",
        "eta(-)",
        "gamma(-)",
        "beta(mm-1)",
        "psi_a(mm)",
    ]
    MAP = {
        "theta_fc": "theta_fc(-)",
        "theta_wp": "theta_wp(-)",
        "Z_r": "Z_r(mm)",
        "q_ic": "q_ic(mm d-1)",
        "K_s": "K_s(m d-1)",
        "eta": "eta(-)",
        "gamma": "gamma(-)",
        "beta": "beta(mm-1)",
        "psi_a": "psi_a(mm)",
    }

    def __init__(
        self,
        model: "Model",
        theta_fc: float,
        theta_wp: float,
        Z_r: float,
        q_ic: float,
        K_s: float,
        eta: float,
        gamma: float,
        beta: float,
        psi_a: float,
    ) -> None:
        """Initializes the SMAP soil component.

        Args:
            model: The Model instance.
            theta_fc: Field capacity moisture content (-).
            theta_wp: Wilting point moisture content (-).
            Z_r: Rooting depth (mm).
            q_ic: Constant infiltration rate (mm/day).
            K_s: Saturated hydraulic conductivity (m/day).
            eta: Infiltration parameter (-).
            gamma: Infiltration parameter (-).
            beta: Infiltration parameter (mm^-1).
            psi_a: Air entry suction (mm).
        """
        super().__init__(
            model,
            3,
            theta_fc=theta_fc,
            theta_wp=theta_wp,
            Z_r=Z_r,
            q_ic=q_ic,
            K_s=K_s,
            eta=eta,
            gamma=gamma,
            beta=beta,
            psi_a=psi_a,
        )


class UnsatZone(Component):
    """Base class for unsaturated zone components."""

    pass


class Weibull(UnsatZone):
    """Weibull unsaturated zone component."""

    REQUIRED_PARAMETERS = ["k(-)", "lambda(-)"]
    MAP = {"k": "k(-)", "lambda_": "lambda(-)"}  # lambda is a keyword in Python

    def __init__(self, model: "Model", k: float, lambda_: float) -> None:
        """Initializes the Weibull unsaturated zone component.

        Args:
            model: The Model instance.
            k: Weibull shape parameter (-).
            lambda_: Weibull scale parameter (-).
        """
        super().__init__(model, 1, k=k, lambda_=lambda_)


class SatZone(Component):
    """Base class for saturated zone components."""

    pass


class Q3K3S1(SatZone):
    """Q3K3S1 saturated zone component."""

    REQUIRED_PARAMETERS = [
        "deltaX(m)",
        "S(-)",
        "K_3(m/d)",
        "K_2(m/d)",
        "K_1(m/d)",
        "z_3(m)",
        "z_2(m)",
        "z_1(m)",
        "alpha(-)",
    ]
    MAP = {
        "dx": "deltaX(m)",
        "K3": "K_3(m/d)",
        "K2": "K_2(m/d)",
        "K1": "K_1(m/d)",
        "S": "S(-)",
        "z3": "z_3(m)",
        "z2": "z_2(m)",
        "z1": "z_1(m)",
        "alpha": "alpha(-)",
    }

    def __init__(
        self,
        model: "Model",
        dx: float,
        K3: float,
        K2: float,
        K1: float,
        S: float,
        z3: float,
        z2: float,
        z1: float,
        alpha: float,
    ) -> None:
        """Initializes the Q3K3S1 saturated zone component.

        Args:
            model: The Model instance.
            dx: Grid spacing (m).
            K3: Hydraulic conductivity of layer 3 (m/day).
            K2: Hydraulic conductivity of layer 2 (m/day).
            K1: Hydraulic conductivity of layer 1 (m/day).
            S: Storage coefficient (-).
            z3: Bottom depth of layer 3 (m).
            z2: Bottom depth of layer 2 (m).
            z1: Bottom depth of layer 1 (m).
            alpha: Saturated zone parameter (-).
        """
        super().__init__(
            model, 1, dx=dx, K3=K3, K2=K2, K1=K1, S=S, z3=z3, z2=z2, z1=z1, alpha=alpha
        )


class Q2K2S1(SatZone):
    """Q2K2S1 saturated zone component."""

    REQUIRED_PARAMETERS = [
        "deltaX(m)",
        "S(-)",
        "K_2(m/d)",
        "K_1(m/d)",
        "z_2(m)",
        "z_1(m)",
        "alpha(-)",
    ]
    MAP = {
        "dx": "deltaX(m)",
        "K2": "K_2(m/d)",
        "K1": "K_1(m/d)",
        "S": "S(-)",
        "z2": "z_2(m)",
        "z1": "z_1(m)",
        "alpha": "alpha(-)",
    }

    def __init__(
        self,
        model: "Model",
        dx: float,
        K2: float,
        K1: float,
        S: float,
        z2: float,
        z1: float,
        alpha: float,
    ) -> None:
        """Initializes the Q2K2S1 saturated zone component.

        Args:
            model: The Model instance.
            dx: Grid spacing (m).
            K2: Hydraulic conductivity of layer 2 (m/day).
            K1: Hydraulic conductivity of layer 1 (m/day).
            S: Storage coefficient (-).
            z2: Bottom depth of layer 2 (m).
            z1: Bottom depth of layer 1 (m).
            alpha: Saturated zone parameter (-).
        """
        super().__init__(model, 2, dx=dx, K2=K2, K1=K1, S=S, z2=z2, z1=z1, alpha=alpha)


class Q1K1S1(SatZone):
    """Q1K1S1 saturated zone component."""

    REQUIRED_PARAMETERS = ["deltaX(m)", "S(-)", "K_1(m/d)", "z_1(m)", "alpha(-)"]
    MAP = {
        "dx": "deltaX(m)",
        "K1": "K_1(m/d)",
        "S": "S(-)",
        "z1": "z_1(m)",
        "alpha": "alpha(-)",
    }

    def __init__(
        self, model: "Model", dx: float, K1: float, S: float, z1: float, alpha: float
    ) -> None:
        """Initializes the Q1K1S1 saturated zone component.

        Args:
            model: The Model instance.
            dx: Grid spacing (m).
            K1: Hydraulic conductivity of layer 1 (m/day).
            S: Storage coefficient (-).
            z1: Bottom depth of layer 1 (m).
            alpha: Saturated zone parameter (-).
        """
        super().__init__(model, 3, dx=dx, K1=K1, S=S, z1=z1, alpha=alpha)


class Q1T1S1(SatZone):
    """Q1T1S1 saturated zone component."""

    REQUIRED_PARAMETERS = ["deltaX(m)", "S(-)", "T_1(m2/d)", "z_1(m)"]
    MAP = {"dx": "deltaX(m)", "T1": "T_1(m2/d)", "S": "S(-)", "z1": "z_1(m)"}

    def __init__(
        self, model: "Model", dx: float, T1: float, S: float, z1: float
    ) -> None:
        """Initializes the Q1T1S1 saturated zone component.

        Args:
            model: The Model instance.
            dx: Grid spacing (m).
            T1: Transmissivity of layer 1 (m2/day).
            S: Storage coefficient (-).
            z1: Bottom depth of layer 1 (m).
        """
        super().__init__(model, 4, dx=dx, T1=T1, S=S, z1=z1)


class VKD(SatZone):
    """VKD saturated zone component."""

    REQUIRED_PARAMETERS = [
        "deltaX(m)",
        "S(-)",
        "K_1(m/d)",
        "m(d-1)",
        "z_1(m)",
        "z_p(m)",
    ]
    MAP = {
        "dx": "deltaX(m)",
        "K1": "K_1(m/d)",
        "m": "m(d-1)",
        "S": "S(-)",
        "z1": "z_1(m)",
        "zp": "z_p(m)",
    }

    def __init__(
        self,
        model: "Model",
        dx: float,
        K1: float,
        m: float,
        S: float,
        z1: float,
        zp: float,
    ) -> None:
        """Initializes the VKD saturated zone component.

        Args:
            model: The Model instance.
            dx: Grid spacing (m).
            K1: Hydraulic conductivity (m/day).
            m: Drainage parameter (day^-1).
            S: Storage coefficient (-).
            z1: Bottom depth of layer 1 (m).
            zp: Depth to base (m).
        """
        super().__init__(model, 5, dx=dx, K1=K1, m=m, S=S, z1=z1, zp=zp)


class Q3K3S3(SatZone):
    """Q3K3S3 saturated zone component."""

    REQUIRED_PARAMETERS = [
        "deltaX(m)",
        "S_3(-)",
        "S_2(-)",
        "S_1(-)",
        "K_3(m/d)",
        "K_2(m/d)",
        "K_1(m/d)",
        "z_3(m)",
        "z_2(m)",
        "z_1(m)",
        "alpha(-)",
    ]
    MAP = {
        "dx": "deltaX(m)",
        "K3": "K_3(m/d)",
        "K2": "K_2(m/d)",
        "K1": "K_1(m/d)",
        "S3": "S_3(-)",
        "S2": "S_2(-)",
        "S1": "S_1(-)",
        "z3": "z_3(m)",
        "z2": "z_2(m)",
        "z1": "z_1(m)",
        "alpha": "alpha(-)",
    }

    def __init__(
        self,
        model: "Model",
        dx: float,
        K3: float,
        K2: float,
        K1: float,
        S3: float,
        S2: float,
        S1: float,
        z3: float,
        z2: float,
        z1: float,
        alpha: float,
    ) -> None:
        """Initializes the Q3K3S3 saturated zone component.

        Args:
            model: The Model instance.
            dx: Grid spacing (m).
            K3: Hydraulic conductivity of layer 3 (m/day).
            K2: Hydraulic conductivity of layer 2 (m/day).
            K1: Hydraulic conductivity of layer 1 (m/day).
            S3: Storage coefficient of layer 3 (-).
            S2: Storage coefficient of layer 2 (-).
            S1: Storage coefficient of layer 1 (-).
            z3: Bottom depth of layer 3 (m).
            z2: Bottom depth of layer 2 (m).
            z1: Bottom depth of layer 1 (m).
            alpha: Saturated zone parameter (-).
        """
        super().__init__(
            model,
            6,
            dx=dx,
            K3=K3,
            K2=K2,
            K1=K1,
            S3=S3,
            S2=S2,
            S1=S1,
            z3=z3,
            z2=z2,
            z1=z1,
            alpha=alpha,
        )


class Q2K2S2(SatZone):
    """Q2K2S2 saturated zone component."""

    REQUIRED_PARAMETERS = [
        "deltaX(m)",
        "S_2(-)",
        "S_1(-)",
        "K_2(m/d)",
        "K_1(m/d)",
        "z_2(m)",
        "z_1(m)",
        "alpha(-)",
    ]
    MAP = {
        "dx": "deltaX(m)",
        "K2": "K_2(m/d)",
        "K1": "K_1(m/d)",
        "S2": "S_2(-)",
        "S1": "S_1(-)",
        "z2": "z_2(m)",
        "z1": "z_1(m)",
        "alpha": "alpha(-)",
    }

    def __init__(
        self,
        model: "Model",
        dx: float,
        K2: float,
        K1: float,
        S2: float,
        S1: float,
        z2: float,
        z1: float,
        alpha: float,
    ) -> None:
        """Initializes the Q2K2S2 saturated zone component.

        Args:
            model: The Model instance.
            dx: Grid spacing (m).
            K2: Hydraulic conductivity of layer 2 (m/day).
            K1: Hydraulic conductivity of layer 1 (m/day).
            S2: Storage coefficient of layer 2 (-).
            S1: Storage coefficient of layer 1 (-).
            z2: Bottom depth of layer 2 (m).
            z1: Bottom depth of layer 1 (m).
            alpha: Saturated zone parameter (-).
        """
        super().__init__(
            model, 7, dx=dx, K2=K2, K1=K1, S2=S2, S1=S1, z2=z2, z1=z1, alpha=alpha
        )


class SA1D(SatZone):
    """SA1D saturated zone component."""

    REQUIRED_PARAMETERS = ["A(m2)", "S(-)", "k(d-1)", "z1(m)"]
    MAP = {"A": "A(m2)", "k": "k(d-1)", "z1": "z1(m)", "S": "S(-)"}

    def __init__(self, model: "Model", A: float, k: float, z1: float, S: float) -> None:
        """Initializes the SA1D saturated zone component.

        Args:
            model: The Model instance.
            A: Area (m2).
            k: Drainage coefficient (day^-1).
            z1: Bottom depth of layer 1 (m).
            S: Storage coefficient (-).
        """
        super().__init__(model, 8, A=A, k=k, z1=z1, S=S)


class Observations:
    """Handles model observations and generates the required input file."""

    def __init__(
        self, model: "Model", obs_df: pd.DataFrame, columns: Dict[str, str]
    ) -> None:
        """Initializes Observations component.

        Args:
            model: The Model instance.
            obs_df: Pandas DataFrame containing observations.
            columns: Dictionary mapping required model columns to user DataFrame columns.
                     Required keys: DATE, RAIN, PET.
                     Optional keys: SOIL_VWC, GWL, ABS.
        """
        self.model: "Model" = model
        self.obs_df: pd.DataFrame = obs_df.copy()
        self.columns: Dict[str, str] = columns

        # Ensure required columns are present in mapping
        for req in ["DATE", "RAIN", "PET"]:
            if req not in columns:
                raise KeyError(
                    f"Required key '{req}' missing from columns mapping dictionary."
                )

            # Ensure mapped column exists in DataFrame
            if columns[req] not in obs_df.columns:
                raise KeyError(
                    f"Mapped {req} column '{columns[req]}' missing from DataFrame."
                )

        self.model.observations = self

    def write_obs_file(self) -> None:
        """Processes observations and writes them to 'Observations.txt' in the working directory."""
        # Create a working copy for processing
        df = self.obs_df.copy()

        # Map user columns to standard names used by the model
        rename_map = {v: k for k, v in self.columns.items()}
        df = df.rename(columns=rename_map)

        # Required columns for the output file
        headings = ["DAY", "MONTH", "YEAR", "RAIN", "PET", "SOIL_VWC", "GWL", "ABS"]

        # Validate numeric types and check for NaNs in required continuous columns
        for col in ["RAIN", "PET", "SOIL_VWC", "GWL", "ABS"]:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    raise TypeError(f"Column '{col}' must be numeric.")

                if col in ["RAIN", "PET"] and df[col].isnull().any():
                    raise ValueError(
                        f"Column '{col}' contains missing values (NaNs). "
                        "Continuous values are required for RAIN and PET."
                    )

        df["DATE"] = pd.to_datetime(df["DATE"])

        # Create date component columns
        df["DAY"] = df["DATE"].dt.day
        df["MONTH"] = df["DATE"].dt.month
        df["YEAR"] = df["DATE"].dt.year

        # Define default fill values for missing columns or NaNs
        fill_values = {"SOIL_VWC": -9999, "GWL": -9999, "ABS": 0}

        # Ensure all required headings are present and fill missing values
        for col in headings:
            if col in ["DAY", "MONTH", "YEAR", "RAIN", "PET"]:
                continue
            if col not in df.columns:
                df[col] = fill_values[col]
            else:
                df[col] = df[col].fillna(fill_values[col])

        # Define output file path
        out_file = os.path.join(self.model.working_directory, "Observations.txt")

        # Write to file with CRLF for Windows/Wine compatibility
        with open(out_file, "w", newline="") as f:
            f.write("NUMBER OF OBSERVATIONS\r\n")
            f.write(f"{len(df)}\r\n")
            # Aquimod 2 expects tab-separated values in Observations.txt
            df[headings].to_csv(
                f, sep="\t", index=False, header=True, lineterminator="\r\n"
            )
