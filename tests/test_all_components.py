import pytest
from aquimodpy.Model import Model
from aquimodpy.Components import (
    FAO,
    NSSS,
    SMAP,
    Weibull,
    Q3K3S1,
    Q2K2S1,
    Q1K1S1,
    Q1T1S1,
    VKD,
    Q3K3S3,
    Q2K2S2,
    SA1D,
)


def test_soil_components():
    model = Model("Test", "exe", "dir")

    # FAO
    fao = FAO(model, theta_fc=0.4, theta_wp=0.1, Z_r=1000, p=0.5, BFI=0.8)
    assert fao.REQUIRED_PARAMETERS == [
        "theta_fc(-)",
        "theta_wp(-)",
        "Z_r(mm)",
        "p(-)",
        "BFI(-)",
    ]

    # NSSS
    with pytest.warns(UserWarning, match="Replacing existing SoilZone component"):
        nsss = NSSS(
            model, theta_fc=0.4, theta_wp=0.1, Z_r=1000, fracstor=0.5, p=0.5, BFI=0.8
        )
    assert nsss.REQUIRED_PARAMETERS == [
        "theta_fc(-)",
        "theta_wp(-)",
        "Z_r(mm)",
        "FRACSTOR(-)",
        "p(-)",
        "BFI(-)",
    ]

    # SMAP
    with pytest.warns(UserWarning, match="Replacing existing SoilZone component"):
        smap = SMAP(
            model,
            theta_fc=0.4,
            theta_wp=0.1,
            Z_r=1000,
            q_ic=50,
            K_s=1.0,
            eta=1.0,
            gamma=2.0,
            beta=1000,
            psi_a=-1,
        )
    assert smap.REQUIRED_PARAMETERS == [
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


def test_unsat_components():
    model = Model("Test", "exe", "dir")
    wb = Weibull(model, k=2.0, lambda_=5.0)
    assert wb.REQUIRED_PARAMETERS == ["k(-)", "lambda(-)"]


def test_sat_components_ordering():
    model = Model("Test", "exe", "dir")

    # Q3K3S1
    q3k3s1 = Q3K3S1(
        model, dx=3000, K3=10, K2=5, K1=1, S=0.01, z3=50, z2=40, z1=30, alpha=1
    )
    assert q3k3s1.REQUIRED_PARAMETERS[1] == "S(-)"

    # Q2K2S1
    with pytest.warns(UserWarning, match="Replacing existing SatZone component"):
        q2k2s1 = Q2K2S1(model, dx=3000, K2=5, K1=1, S=0.01, z2=40, z1=30, alpha=1)
    assert q2k2s1.REQUIRED_PARAMETERS[1] == "S(-)"

    # Q1K1S1
    with pytest.warns(UserWarning, match="Replacing existing SatZone component"):
        q1k1s1 = Q1K1S1(model, dx=3000, K1=1, S=0.01, z1=30, alpha=1)
    assert q1k1s1.REQUIRED_PARAMETERS[1] == "S(-)"

    # Q1T1S1
    with pytest.warns(UserWarning, match="Replacing existing SatZone component"):
        q1t1s1 = Q1T1S1(model, dx=3000, T1=100, S=0.01, z1=30)
    assert q1t1s1.REQUIRED_PARAMETERS[1] == "S(-)"

    # VKD
    with pytest.warns(UserWarning, match="Replacing existing SatZone component"):
        vkd = VKD(model, dx=3000, K1=1, m=0.1, S=0.01, z1=30, zp=40)
    assert vkd.REQUIRED_PARAMETERS[1] == "S(-)"

    # Q3K3S3
    with pytest.warns(UserWarning, match="Replacing existing SatZone component"):
        q3k3s3 = Q3K3S3(
            model,
            dx=3000,
            K3=10,
            K2=5,
            K1=1,
            S3=0.01,
            S2=0.01,
            S1=0.01,
            z3=50,
            z2=40,
            z1=30,
            alpha=1,
        )
    assert q3k3s3.REQUIRED_PARAMETERS[1:4] == ["S_3(-)", "S_2(-)", "S_1(-)"]

    # Q2K2S2
    with pytest.warns(UserWarning, match="Replacing existing SatZone component"):
        q2k2s2 = Q2K2S2(
            model, dx=3000, K2=5, K1=1, S2=0.01, S1=0.01, z2=40, z1=30, alpha=1
        )
    assert q2k2s2.REQUIRED_PARAMETERS[1:3] == ["S_2(-)", "S_1(-)"]

    # SA1D
    with pytest.warns(UserWarning, match="Replacing existing SatZone component"):
        sa1d = SA1D(model, A=1000000, k=0.1, z1=10, S=0.01)
    assert sa1d.REQUIRED_PARAMETERS[1] == "S(-)"
