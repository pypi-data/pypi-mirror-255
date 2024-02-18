from ..waste_generation.elementary import isw_total, msw_to_biotreat, waste_to_treatment


def ch4_emissions(m, ef_ch4_biotr, r_bt):
    """
    Equation 4.1 (tier 1)

    Calculates the CH4 emissions from biological treatment for MSW.
    Contrary to equations 4.1 in guidelines, no summation over treatment types.

    Argument
    --------
    m (Gg/year) : float
        Amount of organic waste that is treated.
        (wet weight)
    ef_ch4_biotr (g/kg) : float
        CH4 emissions factor
    r (Gg/year) : float
        total amount of CH4 that is recovered

    Returns
    -------
    VALUE: float
        CH4 emissions for biological treated MSW(Gg/year)
    """
    ch4_emissions = m * ef_ch4_biotr * 0.01 - r_bt
    return ch4_emissions


def n2o_emissions(m, ef_n2o_biotr):
    """
    Equation 4.2 (tier 1)

    Calculates the N2O emissions from biological treatment for MSW.
    Contrary to equations 4.2 in guidelines, no summation over treatment types.

    Argument
    --------
    m (Gg/year) : float
        Amount of organic waste that is treated.
        (wet weight)
    ef_n2o_biotr (g/kg) : float
        N2O emissions factor

    Returns
    -------
    VALUE: float
        N2O emissions for biological treated MSW(Gg/year)
    """
    n2o_emissions = m * ef_n2o_biotr * 0.01
    return n2o_emissions
