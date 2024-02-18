# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 15:13:53 2023

@author: mathi
"""

""""
This script calculates the emissions from cement production (calcination only, not fuel
combustion!), based on the 2019 Refinement to the 2006 IPCC Guidelines for National
Greenhouse Gas Inventories, volume 3, chapter 2.
The equations in this script are coming only from the IPCC guidelines.
"""


def caco3_supply(f_cao_on_clinker, f_molec_weight_ocao_on_caco3):
    """
    This function calculates the CaCO3 (Calcium carbonate) needed to produce 1 tonne of
    clinker. This value is dependent on the mass fraction of CaO (calcium oxide or lime)
    on clinker: f_CaO_on_clinker (can vary but a default value is 0.65) and on the
    relative molecular weight of CaO on CaCO3.
    IPCC guidelines (Volume 3, Chapter 2) do not provide a particular equation, they
    describe the calculations with default value just before Equation 2.4 (Equation
    2.1.1 in the Technical documentation for cement).

    Parameters
    ----------
    f_CaO_on_clinker : float
        Mass fraction of CaO on clinker (that can be defined by design).
        The default value from IPCC is 0.65.
    f_molec_weight_CaO_on_CaCO3 : float
        Molecular weight fraction of CaO on CaCO3.

    Returns
    -------
    CaCO3_supply : float
        Mass of CaCO3 needed to produce 1 tonne of clinker with the particular fraction
        of CaO, in tonne.

    """

    caco3_supply = f_cao_on_clinker / f_molec_weight_ocao_on_caco3
    return caco3_supply


def calcination_factor_co2(caco3_supply, f_molec_weight_co2_on_caco3):
    """
    This function calculates the CO2 emissions stemming from the calcination of CaCO3
    needed to produce 1 tonne of clinker.
    IPCC guidelines (Volume 3, Chapter 2) do not provide a particular equation, they
    describe the calculations with default value just before Equation 2.4 (Equation
    2.1.2 in the Technical documentation for cement).

    Parameters
    ----------
    CaCO3_supply : float
        Mass value of CaCO3 that is calcinated to produce 1 tonne of clinker, in
        tonnes CaCO3/tonne clinker.
    f_molec_weight_CO2_on_CaCO3 : float
        Molecular weight fraction of CO2 on CaCO3.

    Returns
    -------
    CO2_release_calcination_CaCO3 : float
        Mass of CO2 released from the CaCO3 calcination, in tonnes CO2/tonne of clinker.

    """

    co2_release_calcination_caco3 = caco3_supply * f_molec_weight_co2_on_caco3
    return co2_release_calcination_caco3


def ef_clc(cao_in_clinker, ckd_correc_fact):
    """
    Equation 2.4 (tier 1)

    This function calculates the corrected emission factor for clinker production, in
    tonnes CO2/tonne of clinker.

    Parameters
    ----------
    cao_on_clinker (t/t): float
        Mass of CO2 released from the CaCO3 calcination, in tonnes CO2/tonne of clinker.
    ckd_correc_fact : float
        Correction factor due to Cement Kiln Dust (limiting the efficiency of
        calcination). A default assumption from IPCC would be an additional 2% (1.02)
        but can be adjusted.
        The default value from IPCC is 1.02.

    Returns
    -------
    ef_clc (t/t): float
    Corrected emission factor for clinker producion (in tonnes CO2/tonne of clinker).

    """
    X = cao_in_clinker / 0.5603
    ef_clc = X * 0.43971 * ckd_correc_fact
    return ef_clc


def ef_cl(cao_in_clinker, cao_non_carbo_frac):
    """
    Equation 2.4 (tier 2)

    This function calculates the corrected emission factor for clinker production, in
    tonnes CO2/tonne of clinker.

    Parameters
    ----------
    cao_on_clinker (t/t): float
        Mass of CO2 released from the CaCO3 calcination, in tonnes CO2/tonne of clinker.
    cao_non_carbo_frac (kg/kg): float
        fraction of CaO that is from non-carbonate sources (e.g. steel, slag of fly ash).


    Returns
    -------
    ef_cl (t/t): float
    Corrected emission factor for clinker producion (in tonnes CO2/tonne of clinker).

    """
    X = (cao_in_clinker - cao_non_carbo_frac) / 0.5603
    ef_cl = X * 0.43971
    return ef_cl


def co2_emissions_tier1_(m_c, c_cl, im_cl, ex_cl, ef_clc):
    """
    Equation 2.1 (tier 1).

    CO2 emissions stemming from the calcination for a certain amount of cement produced.
    Adoptions of parameters are done to make cement type explicit.

    Argument
    --------
    m_c (t): float
        Total mass of cement type produced.
    c_cl (dimensionless): float
        Fraction of clinker on cement type.
    im_cl (t): float
        import of clinker per cement type.
    ex_cl (t): float
        Export of clinker per cement type.
    ef_clc (t/t): float
        Emission factor of clinker in particular cement.

    Returns
    -------
    co2_emissions: float
        Total CO2 emissions generated from cement production per type of cement (in tonnes CO2).

    """
    co2_emissions = (m_c * c_cl - im_cl + ex_cl) * ef_clc
    return co2_emissions


def co2_emissions_tier2_(m_cl, ef_cl, cf_ckd):
    """
    Equation 2.2 (tier 2).

    This function calculates the CO2 emissions based on clinker production data.

    Argument
    --------
    m_cl (t/year): float
        Total mass of clinker produced.
    ef_cl (t/t): float
        Emission factor for clinker.
    cf_ckd (dimensionless): float
        Emissions correction factor for CKD.

    Returns
    -------
    co2_emissions (t/year): float
        Total CO2 emissions generated from cement production (in tonnes CO2).

    """
    co2_emissions = m_cl * ef_cl * cf_ckd
    return co2_emissions


def co2_per_cement_type_tier2(co2_emissions, cement_frac_region):
    """
    Equation 2.x (tier 2)

    Not in the guidelines. Is added to provide CO2 emissions per cement type.

    Argument
    --------
    co2_emissions (t/year): float
        total co2 emissions
    cement_frac_region (kg/kg): float
        fraction of cement type in the region (sum over cement types must equal 1)

    Returns
    -------
    co2_per_cement_type (t/year): float
        co2 emissions per cement type
    """
    co2_per_cement_type = co2_emissions * cement_frac_region
    return co2_per_cement_type


def cf_ckd(m_d, m_cl, c_d, f_d, ef_c, ef_cl):
    """
    Equation 2.5 (tier 2)

    CORRECTION FACTOR FOR CKD NOT RECYCLED TO THE KILN.

    Argument
    --------


    Returns
    -------

    """
    cf_ckd = 1 + (m_d / m_cl) * c_d * f_d * ef_c / ef_cl
    return cf_ckd


def co2_emissions_tier3_(ef_i, m_i, f_i, m_d, c_d, f_d, ef_d, m_k, x_k, ef_k):
    """
    Equation 2.3 (tier 3).

    This function calculates the CO2 emissions based on carbonate raw material inputs to the kiln.

    Argument
    --------
    ef_i,
    m_i
    f_i,
    m_d,
    c_d,
    f_d,
    ef_d,
    m_k,
    x_k,
    ef_k,

    Returns
    -------
    co2_emissions (t): float
        Total CO2 emissions generated from cement production (in tonnes CO2).

    """
    co2_emissions = (
        (ef_i * m_i * f_i) - (m_d * c_d * (1 - f_d) * ef_d) + (m_k * x_k * ef_k)
    )
    return co2_emissions
