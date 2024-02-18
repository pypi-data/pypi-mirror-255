def soc(soc_ref, f_lu, f_mg, f_i, a):
    """
    Equation 2.25
    ANNUAL CHANGE IN ORGANIC CARBON STOCKS IN MINERAL SOILS

    Argument
    --------


    Returns
    -------
    VALUE: float
        soc (t)
    """
    soc = soc_ref * f_lu * f_mg * f_i * a
    return soc


def delta_c_mineral(soc_0, soc_t, d):
    """
    Equation 2.25
    ANNUAL CHANGE IN ORGANIC CARBON STOCKS IN MINERAL SOILS

    Argument
    --------
    soc_0 (t) : float
        soil organic carbon stock in the last year of an inventory time period
    soc_t (t) : float
        soil organic carbon stock at the beginning of an inventory time period
    d (yr): integer
        Time dependence of stock change factors which is the default time period for transition between equilibrium SOC values, yr. Commonly 20 years.
        If T exceeds D, use the value for T to obtain an annual rate of change over the inventory time period (0-T years).

    Returns
    -------
    VALUE: float
        delta_c (t/yr)
    """
    delta_c_mineral = (soc_0 - soc_t) / d
    return delta_c_mineral


def n2o(n2o_n):
    """
    Equation 11.x
    Convert to N2O emissions for reporting purposes.

    Argument
    --------
    n2o_n (kg/yr) : float
        nitrogen in n2o

    Returns
    -------
    VALUE: float
        n2o (kg/yr)
    """
    n2o = n2o_n * 44 / 28
    return n2o
