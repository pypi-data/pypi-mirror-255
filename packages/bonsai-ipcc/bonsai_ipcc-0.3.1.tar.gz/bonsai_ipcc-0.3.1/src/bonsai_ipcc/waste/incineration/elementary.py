from ..waste_generation.elementary import (
    isw_total,
    msw_open_burned,
    msw_to_incin,
    waste_to_technology,
    waste_to_treatment,
)


def co2_emissions(waste, dm, cf, fcf, of):
    """
    Equation 5.x (in accordance to 5.1 and 5.2, tier 1)

    Calculates the CO2 emissions from incineration/open-burning for a waste type.
    Contrary to equations 5.1 and 5.2, no summation over waste types.

    Argument
    --------
    waste (Gg/year) : float
        Amount of waste type that is incinerated/open-burned.
        (wet weight)
    dm (kg/kg) : float
        Dry matter content in the waste type.
    fcf (kg/kg) : float
        Fraction of fossil carbon in the waste type.
    of (kg/kg) :float
        Oxidation factor.

    Returns
    -------
    VALUE: float
        CO2 emissions for waste type (Gg/year)
    """
    co2_emissions = waste * dm * cf * fcf * of * 44 / 12
    return co2_emissions


def ch4_emissions(waste, ef_ch4):
    """
    Equation 5.y (in accordance to 5.4, tier 1)

    Calculates CH4 emissions from incineration/open-burning for a waste type.
    Contrary to equations 5.4, no summation over waste types.

    Argument
    --------
    waste (Gg/year) : float
        Amount of waste type that is incinerated/open-burned.
        (wet weight)
    EF_CH4 (kg/Gg) float
        CH4 emission factor of wet waste.

    Returns
    -------
    VALUE: float
        CH4 emissions for waste type (Gg/year)
    """
    ch4_emissions = waste * ef_ch4 * 0.000001
    return ch4_emissions


def n2o_emissions(waste, ef_n2o):
    """
    Equation 5.5z (in accordance to 5.5, tier 1)

    Calculates N2o emissions from incineration/open-burning for a waste type.
    Contrary to equations 5.5, no summation over waste types.

    Argument
    --------
    waste (Gg/year) : float
        Amount of waste type that is incinerated/open-burned.
        (wet weight)
    ef_n2o (kg/Gg) float
        N2O emission factor of wet waste.

    Returns
    -------
    VALUE: float
        N2O emissions for waste type (Gg/year)
    """
    n2o_emissions = waste * ef_n2o * 0.000001
    return n2o_emissions


def n2o_emissions_tier3(iw, ec, fgv):
    """
    Equation 5.6z (in accordance to 5.6, tier 3)

    Calculates N2o emissions based on influencing factors.
    Contrary to equations 5.6, no summation over waste types.

    Argument
    --------
    iw (Gg/year) : float
        Amount of waste type that is incinerated per treatment type.
        (wet weight)
    ec (mg/m3) : float
        N2O emission concentration in flue gas from the incineration of waste type.
    fgv (m3/Mg) : float
        Flue gas volume by amount of incinerated waste type.

    Returns
    -------
    VALUE: float
        N2O emissions for waste type and treatment type (Gg/year)
    """
    n2o_emissions_tier3 = iw * ec * fgv * 0.000000001
    return n2o_emissions_tier3
