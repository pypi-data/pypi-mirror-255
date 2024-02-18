import math

import numpy as np
from uncertainties.umath import exp as uexp

from ..waste_generation.elementary import (
    isw_total,
    msw_to_swds,
    waste_to_technology,
    waste_to_treatment,
)


def ddoc_from_wd_data(waste, doc, doc_f, mcf):
    """
    Equation 3.2 (tier 1)

    Calculates the decomposable DOC (DDOCm) from waste disposal data.

    Argument
    --------
    waste (Gg) : float
        Amount of waste
        (either wet or dry-matter, but attention to DOC!)
    doc (kg/kg) : float
        fraction of degradable organic carbon in waste.
    doc_f (kg/kg) : float
        fraction of doc that can decompose.
    mcf (kg/kg) : float
        CH4 correction factor for aerobic decomposition in the year of decompostion.

    Returns
    -------
    VALUE: float
        Decomposable DOC (Gg/year)
    """
    ddoc_from_wd_data = waste * doc * doc_f * mcf
    return ddoc_from_wd_data


def ch4_generated(ddocm, f):
    """
    Equation 3.6 (tier 1)

    Calculates the generated amount of CH4 from delayed DDOCm.
    The assumption in tier 1 is that all decomposable DOC is decomposed in the year of dumping.

    Argument
    --------
    ddocm (Gg/year) : float
       Decomposed DDOCm in a given year.
    f (m3/m3) : float
       Fraction of CH4 in landfill gas (volume).

    Returns
    -------
    VALUE: float
        CH4 generated (Gg/year)
    """
    # F = 0.5 # fraction of CH4 by volume, in generated landfill gas
    ch4_generated = ddocm * f * 16 / 12
    return ch4_generated


def ch4_emissions(ch4_gen, ox, r):
    """
    Equation 3.1 (tier 1)

    Calculates the CH4 emissions based on the amount of CH4 that is generated in swdS.

    Argument
    --------
    ch4_gen (Gg/year) : float
       Generated amount of CH4 for a given year.
    ox (kg/kg) : float
       oxidation factor.
    r (kg/kg) : float
       Methane recovery rate. (in guidelines R is a absolut value, instead of a fraction)
       Assumed to be zero. When providing values, consider uncertainties:
       +- 10% of def, if meetering in place,
       +- 50% of def, if no meetering in place.

    Returns
    -------
    VALUE: float
        CH emissions (Gg/year)
    """
    # R = 0.0 # fraction of CH4 that is recovered
    ch4_emissions = (ch4_gen - (ch4_gen * r)) * (1 - ox)
    return ch4_emissions


def co2_emissions_direct(ddocm, f):
    """
    Equation 3.x (not explicit in the guidelines, tier 1)

    Calculates the direct CO2 emissions from delayed DDOCm.
    The assumption in tier 1 is that all decomposable DOC is decomposed in the year of dumping.

    Argument
    --------
    ddocm (Gg/year) : float
       Decomposed DDOCm in a given year.
    f (m3/m3) : float
       Fraction of CH4 in landfill gas (volume).
       Assumption that rest is CO2

    Returns
    -------
    VALUE: float
        CO2 (Gg/year)
    """
    # F = 0.5 # fraction of CH4 by volume, in generated landfill gas
    co2_emissions_direct = ddocm * (1 - f) * 44 / 12
    return co2_emissions_direct


def co2_emissions_from_ch4(ddocm, f, ox):
    """
    Equation 3.x (not explicit in the guidelines, tier 1)

    Calculates the indirect CO2 emissions from generated CH4.
    The assumption in tier 1 is that all decomposable DOC is decomposed in the year of dumping.

    Argument
    --------
    ddocm (Gg/year) : float
       Decomposed DDOCm in a given year.
    f (m3/m3) : float
       fraction of ch4 in landfill gas (volume).
       assumption that rest is co2
    ox (kg/kg) : float
       oxidation factor.
    r (kg/kg) : float
       Methane recovery rate. (in guidelines R is a absolut value, instead of a fraction)
       Assumed to be zero. When providing values, consider uncertainties:
       +- 10% of def, if meetering in place,
       +- 50% of def, if no meetering in place.

    Returns
    -------
    VALUE: float
        CO2 (Gg/year)
    """
    # F = 0.5 # fraction of CH4 by volume, in generated landfill gas
    ch4_gen = ddocm * f * 16 / 12
    co2_emissions_from_ch4 = ch4_gen * ox * 12 / 16 * 44 / 12
    return co2_emissions_from_ch4


def ddoc_m_decomp_t(ddoc_ma_t_1, k):
    """
    Equation 3.5
    Calculates DDOCm DECOMPOSED AT THE END OF YEAR T.


    Argument
    --------
    ddoc_ma_t_1 (Gg) : float
        DDOCm accumulated in the swdS at the end of year (T-1)
    k (1/yr) : float
        reaction constant k, k=ln(2)/t_1/2
        t_1/2 = half-life time

    Returns
    -------
    VALUE: float
        DDOCm decomposed (Gg/yr)
    """
    try:
        # equation for type(k) = float
        ddoc_m_decomp_t = ddoc_ma_t_1 * (1 - math.exp(-k))
    except TypeError:
        try:
            # for type(k) = ufloat
            ddoc_m_decomp_t = ddoc_ma_t_1 * (1 - uexp(-k))
        except TypeError:
            # for type(k) = np.array
            ddoc_m_decomp_t = ddoc_ma_t_1 * (1 - np.exp(-k))
    return ddoc_m_decomp_t


def ddoc_ma_t(ddoc_md_t, ddoc_ma_t_1, k):
    """
    Equation 3.4
    Calculates DDOCm accumulated in the swdS at the end of year T.


    Argument
    --------
    ddoc_md_t (Gg) : float
        DDOCm deposited into the swdS in year T.
    ddoc_ma_t_1 (Gg) : float
        DDOCm accumulated in the swdS at the end of year (T-1)
    k (1/yr) : float
        reaction constant k, k=ln(2)/t_1/2
        t_1/2 = half-life time

    Returns
    -------
    VALUE: float
        DDOCm accumulated (Gg(yr))
    """
    try:
        # equation for type(k) = float
        ddoc_ma_t = ddoc_md_t + (ddoc_ma_t_1 * math.exp(-k))
    except TypeError:
        try:
            # for type(k) = ufloat
            ddoc_ma_t = ddoc_md_t + (ddoc_ma_t_1 * uexp(-k))
        except TypeError:
            # for type(k) = np.array
            ddoc_ma_t = ddoc_md_t + (ddoc_ma_t_1 * np.exp(-k))
    return ddoc_ma_t
