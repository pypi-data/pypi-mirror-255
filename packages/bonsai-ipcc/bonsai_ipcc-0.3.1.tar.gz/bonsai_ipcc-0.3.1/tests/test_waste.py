import os
from pathlib import Path

import pandas as pd
import pytest

TEST_DATA_PATH = Path(os.path.dirname(__file__)).parent / "tests/data/"

from bonsai_ipcc import IPCC
from bonsai_ipcc.waste.swd import elementary as elem


def test_msw_to_swds():
    obs = elem.msw_to_swds(
        urb_population=200, msw_gen_rate=0.5, msw_frac_to_swds=0.5, msw_type_frac=0.5
    )
    assert obs == 200 * 0.5 * 0.5 * 0.5


def test_C_balance():
    DDOCm = 100
    F = 0.5
    R = 0.1
    OX = 0.1

    CH4_gen = elem.ch4_generated(ddocm=DDOCm, f=F)
    CH4 = elem.ch4_emissions(ch4_gen=CH4_gen, ox=OX, r=R)
    CO2_d = elem.co2_emissions_direct(ddocm=DDOCm, f=F)
    CO2_i = elem.co2_emissions_from_ch4(ddocm=DDOCm, f=F, ox=OX)

    obs = (
        CH4 * (12 / 16)  # Carbon in CH4 emissions
        + (CO2_d + CO2_i) * (12 / 44)  # Carbon in CO2 emissions
        + (CH4_gen * R) * (1 - OX) * 12 / 16  # Carbon in recovered CH4
    )
    expected = DDOCm

    assert obs == expected


def test_tier2_CH4_swd():
    test = IPCC()

    # same data as in the IPCC waste model example
    d = {
        "year": [1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959],
        "region": ["DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE"],
        "waste_type": [
            "msw_food",
            "msw_food",
            "msw_food",
            "msw_food",
            "msw_food",
            "msw_food",
            "msw_food",
            "msw_food",
            "msw_food",
            "msw_food",
        ],
        "property": [
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
        ],
        "value": [
            2300.322,
            2300.322,
            2300.322,
            2300.322,
            2300.322,
            2300.322,
            2300.322,
            2300.322,
            2300.322,
            2300.322,
        ],
        "unit": [
            "Gg/year",
            "Gg/year",
            "Gg/year",
            "Gg/year",
            "Gg/year",
            "Gg/year",
            "Gg/year",
            "Gg/year",
            "Gg/year",
            "Gg/year",
        ],
    }
    df = pd.DataFrame(d).set_index(["year", "region", "waste_type", "property"])
    test.waste.swd.parameter.sw = df

    d = {
        "year": [1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959],
        "region": ["DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE"],
        "property": [
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
        ],
        "value": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "unit": [
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
        ],
    }
    df = pd.DataFrame(d).set_index(["year", "region", "property"])
    test.waste.swd.parameter.msw_frac_to_swds = df

    d = {
        "year": [1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959],
        "region": ["DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE"],
        "swds_type": [
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
        ],
        "property": [
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
        ],
        "value": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "unit": [
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
        ],
    }
    df = pd.DataFrame(d).set_index(["year", "region", "swds_type", "property"])
    test.waste.swd.parameter.swdstype_frac = df

    d = {
        "year": [1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959],
        "region": ["DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE"],
        "swds_type": [
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
            "uncharacterised",
        ],
        "property": [
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
            "def",
        ],
        "value": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "unit": [
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
            "kg/kg",
        ],
    }
    df = pd.DataFrame(d).set_index(["year", "region", "swds_type", "property"])
    test.waste.swd.parameter.r_swd = df

    test.waste.swd.parameter.mcf.loc[("uncharacterised", "def"), "value"] = 0.705

    sequence = test.waste.swd.sequence.tier2_ch4(
        year=1959,
        region="DE",
        wastetype="msw_food",
        wastemoisture="wet",
        past_years=9,
        landfilltype="uncharacterised",
        uncertainty="def",
    )

    # read the expected result
    TEST_DF = pd.read_excel(
        TEST_DATA_PATH / "test_waste_CH4_food_waste.xlsx",
        sheet_name="Food",
        header=[13],
    ).drop(index=[0, 1, 2])

    assert (
        sequence.ch4.value
        == TEST_DF.loc[TEST_DF["Year"] == 1959]["CH4 generated "].item()
    )
