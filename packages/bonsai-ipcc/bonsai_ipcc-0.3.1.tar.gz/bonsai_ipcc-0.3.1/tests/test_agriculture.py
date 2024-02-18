import os
from pathlib import Path

import pandas as pd
import pytest

TEST_DATA_PATH = Path(os.path.dirname(__file__)) / "data/"

from bonsai_ipcc import IPCC


def test_livestock_nex():
    YEAR = 2019
    REGION = "DE"
    SPECIES_TYPE = "cattle-dairy"
    UNCERTAINTY = "def"

    test = IPCC()

    df_n = pd.DataFrame(
        {
            "year": [2019, 2019, 2019, 2019, 2019],
            "region": ["DE", "DE", "DE", "DE", "DE"],
            "species_type": [
                "cattle-dairy",
                "cattle-dairy",
                "cattle-dairy",
                "cattle-dairy",
                "cattle-dairy",
            ],
            "property": ["def", "min", "max", "abs_min", "abs_max"],
            "value": [1.0, 1.0, 1.0, 0.0, "inf"],
            "unit": ["piece", "piece", "piece", "piece", "piece"],
        }
    ).set_index(["year", "region", "species_type", "property"])

    test.agriculture.livestock_manure.parameter.n = df_n

    s1 = test.agriculture.livestock_manure.sequence.tier1_n2o(
        year=YEAR,
        region=REGION,
        species_type=SPECIES_TYPE,
        manuretreat_type="lagoon",
        uncertainty=UNCERTAINTY,
    )

    s2 = test.agriculture.livestock_manure.sequence.tier2_n2o(
        year=YEAR,
        region=REGION,
        species_type=SPECIES_TYPE,
        feeding_situation="stall",
        diet_type="forage-high",
        manuretreat_type="solid-storage",
        uncertainty=UNCERTAINTY,
    )

    # test data is taken from table 10a.1 (tier 1 data)
    TEST_DF = pd.read_csv(
        TEST_DATA_PATH / "test_agriculture_nex.csv", delimiter=","
    ).set_index(["year", "region", "species_type", "property"])

    weight = s2.weight.value  # kg
    nex_expected = TEST_DF.loc[(YEAR, "Western Europe", SPECIES_TYPE, UNCERTAINTY)][
        "value"
    ]

    # two tests
    # tier 1 test (needs to be equal the provided tier 1 values)
    nex_test1 = (
        s1.nex.value / 365 * (1000 / weight)
    )  # transformation of unit kg/animal/year => kg/1000kg/day

    # tier 2 test (tolerance is allowed compared to tier 1 values)
    nex_test2 = s2.nex.value / 365 * (1000 / weight)
    TOLERANCE = 0.3

    assert nex_test1 == nex_expected
    assert abs((nex_expected - nex_test2) / nex_expected) <= TOLERANCE


def test_soils_delta_c():
    """Example in volume: 4, chpater: 5 page: 5.22, year: 2006."""

    EXPECTED_C = 264000  # t C per year
    TOLERANCE = 0.001  # due to rounding

    YEAR = 2019
    REGION = "DE"
    CROPTYPE = "wheat_spring"
    LANDUSETYPE = "CL-ANNUAL"
    CULTIVATIONTYPE = "N_unspec"
    CLIMATEZONE = "temperate-warm"
    MOISTUREREGIME = "wet"
    LANDUSECHANGE = {"year_ref": 2009, "landusechange_type": "CL_CL"}
    UNCERTAINTY = "def"

    PAR_A = pd.read_excel(
        TEST_DATA_PATH / "test_agriculture_delta_c.xlsx", sheet_name="par_a"
    ).set_index(
        [
            "year",
            "region",
            "climate_zone",
            "moisture_regime",
            "soil_type",
            "landuse_type",
            "management_practice",
            "amendment_level",
            "property",
        ]
    )

    PAR_YIELD_FRESH = pd.read_excel(
        TEST_DATA_PATH / "test_agriculture_delta_c.xlsx", sheet_name="par_yield_fresh"
    ).set_index(["year", "region", "landuse_type", "crop_type", "property"])

    df_area = pd.DataFrame(
        {
            "year": [YEAR, YEAR, YEAR, YEAR, YEAR],
            "region": [REGION, REGION, REGION, REGION, REGION],
            "crop_type": [
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
            ],
            "property": ["def", "min", "max", "abs_min", "abs_max"],
            "value": [1.0, 1.0, 1.0, 0.0, "inf"],
            "unit": ["ha/year", "ha/year", "ha/year", "ha/year", "ha/year"],
        }
    ).set_index(["year", "region", "crop_type", "property"])

    df_frac_burnt = pd.DataFrame(
        {
            "year": [YEAR, YEAR, YEAR, YEAR, YEAR],
            "region": [REGION, REGION, REGION, REGION, REGION],
            "crop_type": [
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
            ],
            "property": ["def", "min", "max", "abs_min", "abs_max"],
            "value": [1.0, 1.0, 1.0, 0.0, "inf"],
            "unit": ["kg/kg", "kg/kg", "kg/kg", "kg/kg", "kg/kg"],
        }
    ).set_index(["year", "region", "crop_type", "property"])

    df_n_mms = pd.DataFrame(
        {
            "year": [YEAR, YEAR, YEAR, YEAR, YEAR],
            "region": [REGION, REGION, REGION, REGION, REGION],
            "landuse_type": [
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
            ],
            "crop_type": [
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
            ],
            "property": ["def", "min", "max", "abs_min", "abs_max"],
            "value": [1.0, 1.0, 1.0, 0.0, "inf"],
            "unit": ["kg/year", "kg/year", "kg/year", "kg/year", "kg/year"],
        }
    ).set_index(["year", "region", "landuse_type", "crop_type", "property"])

    df_f_comp = pd.DataFrame(
        {
            "year": [YEAR, YEAR, YEAR, YEAR, YEAR],
            "region": [REGION, REGION, REGION, REGION, REGION],
            "landuse_type": [
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
            ],
            "crop_type": [
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
            ],
            "property": ["def", "min", "max", "abs_min", "abs_max"],
            "value": [1.0, 1.0, 1.0, 0.0, "inf"],
            "unit": ["kg/year", "kg/year", "kg/year", "kg/year", "kg/year"],
        }
    ).set_index(["year", "region", "landuse_type", "crop_type", "property"])

    df_f_sew = pd.DataFrame(
        {
            "year": [YEAR, YEAR, YEAR, YEAR, YEAR],
            "region": [REGION, REGION, REGION, REGION, REGION],
            "landuse_type": [
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
            ],
            "crop_type": [
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
            ],
            "property": ["def", "min", "max", "abs_min", "abs_max"],
            "value": [1.0, 1.0, 1.0, 0.0, "inf"],
            "unit": ["kg/year", "kg/year", "kg/year", "kg/year", "kg/year"],
        }
    ).set_index(["year", "region", "landuse_type", "crop_type", "property"])

    df_f_ooa = pd.DataFrame(
        {
            "year": [YEAR, YEAR, YEAR, YEAR, YEAR],
            "region": [REGION, REGION, REGION, REGION, REGION],
            "landuse_type": [
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
            ],
            "crop_type": [
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
                CROPTYPE,
            ],
            "property": ["def", "min", "max", "abs_min", "abs_max"],
            "value": [1.0, 1.0, 1.0, 0.0, "inf"],
            "unit": ["kg/year", "kg/year", "kg/year", "kg/year", "kg/year"],
        }
    ).set_index(["year", "region", "landuse_type", "crop_type", "property"])

    # year,region,landuse_type,cultivation_type,property,value,unit
    df_f_sn = pd.DataFrame(
        {
            "year": [YEAR, YEAR, YEAR, YEAR, YEAR],
            "region": [REGION, REGION, REGION, REGION, REGION],
            "landuse_type": [
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
                LANDUSETYPE,
            ],
            "cultivation_type": [
                CULTIVATIONTYPE,
                CULTIVATIONTYPE,
                CULTIVATIONTYPE,
                CULTIVATIONTYPE,
                CULTIVATIONTYPE,
            ],
            "property": ["def", "min", "max", "abs_min", "abs_max"],
            "value": [1.0, 1.0, 1.0, 0.0, "inf"],
            "unit": ["kg/year", "kg/year", "kg/year", "kg/year", "kg/year"],
        }
    ).set_index(["year", "region", "landuse_type", "cultivation_type", "property"])

    test = IPCC()

    test.agriculture.soils.parameter.area = df_area
    test.agriculture.soils.parameter.frac_burnt = df_frac_burnt
    test.agriculture.soils.parameter.n_mms = df_n_mms
    test.agriculture.soils.parameter.f_comp = df_f_comp
    test.agriculture.soils.parameter.f_sew = df_f_sew
    test.agriculture.soils.parameter.f_ooa = df_f_ooa
    test.agriculture.soils.parameter.f_sn = df_f_sn

    test.agriculture.soils.parameter.a = PAR_A
    test.agriculture.soils.parameter.yield_fresh = PAR_YIELD_FRESH

    s = test.agriculture.soils.sequence.tier1_n2o_inputs(
        year=YEAR,
        region=REGION,
        crop_type=CROPTYPE,
        landuse_type=LANDUSETYPE,
        cultivation_type=CULTIVATIONTYPE,
        climate_zone=CLIMATEZONE,
        moisture_regime=MOISTUREREGIME,
        landusechange=LANDUSECHANGE,
        uncertainty=UNCERTAINTY,
    )

    result = s.delta_c_mineral.value

    assert abs((EXPECTED_C - result) / EXPECTED_C) <= TOLERANCE
