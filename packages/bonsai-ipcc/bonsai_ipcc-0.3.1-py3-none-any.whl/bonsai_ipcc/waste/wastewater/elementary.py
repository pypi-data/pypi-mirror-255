import numpy as np

from ..biological.elementary import ch4_emissions as ch4_sludge
from ..waste_generation.elementary import ww_domestic, ww_industrial


def ch4_emissions_system(tow, s, ef, r):
    """
    Equation 6.1 (tier 1)

    Calculates the CH4 emissions from domestic wastewater treatment per system.

    Argument
    --------
    tow (kg/year) : float
        organics in wastewater of the treatment/discharge system (kg bod/yr)
    s (kg/year) : float
        organic component removed from the wastewater of the system (kg bod/yr)
    ef (kg/kg) : float
        emission factor for the system (kg ch4 / kg bod)
    r (kg/year) : float
        amount of CH4 recovered from the system (kg CH4 /yr)

    Returns
    -------
    VALUE: float
        CH4 emissions for treatment/discharge system (kg/year)
    """
    ch4_emissions_system = (tow - s) * ef - r
    return ch4_emissions_system


def ch4_emissions(*ch4):
    """
    Equation 6.1a (tier 1)

    Total CH4 emissions from domestic wastewater treatment and discharge.

    Argument
    --------
    ch4 (kg/year) : float, list of floats
        CH4 emissions of systems

    Returns
    -------
    VALUE: float
        total CH4 emissions for treatment and discharge system (Gg/year)
    """
    ch4_emissions = 0
    for c in ch4:
        ch4_emissions += c
    return ch4_emissions * 0.00001


def ef_ch4(b0, mcf):
    """
    Equation 6.2 (tier 1)

    Calculates the CH4 emission factor per treatment/discharge system.

    Argument
    --------
    b0 (kg/kg) : float
        maximum ch4 producing capacity (kg ch4/ kg bod)
    mcf (kg/kg) : float
        methane correction factor (fraction)

    Returns
    -------
    VALUE: float
        CH4 emission factor (kg/kg)
    """
    ef_ch4 = b0 * mcf
    return ef_ch4


def tow_system(tow, u, t, i):
    """
    Equation 6.3a (tier 1)

    Calculates total organics in domestic wastewater (TOW) per treatment/discharge system.
    Contrary to the guidelines the two dimensionless factors U and T are merged to one (UT),
    indicating the total share of system j in a country.

    Argument
    --------
    tow (kg/year) : float
        total organics in wasterwater
    u (cap/cap) float
        fraction of population per income group
    t (kg/kg) : float
        degree of utilisation of treatment/discharge system j per income group i
    i (kg/kg) : float
        correction factor for additional industrial BOD discharged into the system j

    Returns
    -------
    VALUE: float
        TOW per system j (kg/year)
    """
    tow_system = tow * u * t * i
    return tow_system


# def UT_ratio(U, T):
#    """
#    Helper Equation 6.x (not explicitly in the guidelines)
#
#    Calculates the degree of utilisation of treatment/discharge system j in a country.
#
#    Argument
#    --------
#    U (cap/cap) : np.array
#        fraction of population per income group i
#    T (kg/kg) : np.array
#        degree of utilisation of treatment/discharge system j per income group i
#
#    Returns
#    -------
#    UT (kg/kg) : float
#        degree of utilisation of treatment/discharge system j in a country
#    """
#    UT = np.multiply(U, T).sum()
#    return UT


def return_category(wwatertreat_type):
    """
    Helper function (not in the guidelines)
    This is required, since treatment types in table 6.3 does not match with treatment categories in table 6.5.

    Argument
    --------
        wwatertreat_type : str
            wastewater treatment type

    Returns
    -------
    str
        wastewater treatment category
    """

    mapping = {
        "coll_treat_aerob_centralised_primary": "sewer",
        "coll_treat_aerob_centralised_primary-and-digest": "sewer",
        "coll_treat_aerob_centralised_wo-primary": "sewer",
        "coll_treat_aerob_centralised_primary_secondary": "sewer",
        "coll_treat_aerob_centralised_primary-and-digest_secondary": "sewer",
        "coll_treat_aerob_centralised_primary_secondary-tertiary": "sewer",
        "coll_treat_aerob_centralised_primary-and-digest_secondary-tertiary": "sewer",
        "coll_treat_aerob_shallow": "sewer",
        "coll_treat_anaerob_a-lagoons": "other",
        "coll_treat_anaerob_f-lagoons": "other",
        "coll_treat_anaerob_c-wetlands": "other",
        "coll_treat_anaerob_a-reactors": "other",
        # "coll_treat_onsite_sludge": "other",
        # "coll_treat_onsite_composting": "other",
        # "coll_treat_onsite_incineration": "other",
        # "coll_untreat_sewers-flowing_closed": "sewer",
        # "coll_untreat_sewers-flowing_open": "sewer",
        # "coll_untreat_sewer-stagnant": "sewer",
        "uncoll_septic-tanks": "septic-tank",
        "uncoll_septic-system": "septic-tank",
        "uncoll_latrines_small": "latrine",
        "uncoll_latrines_communal": "latrine",
        "uncoll_latrines_wet": "latrine",
        "uncoll_untreated": "none",
    }

    return_category = mapping[wwatertreat_type]

    return return_category


def tow_eff_treat_system(tow, t, tow_rem):
    """
    Equation 6.3d (tier 1)

    Calculates total the amount of TOW in effluent.
    Contrary to the guidelines no summation over treatment systems is done.

    Argument
    --------
    tow (kg/year) : float
        total organics in wasterwater
    t (kg/kg) : float
        degree of utilisation of treatment/discharge system
    tow_rem (kg/kg) : float
        fraction of total wastewater organicas removed during wastewater treatment

    Returns
    -------
    VALUE: float
        TOW_EFFFtreat per system (kg/year)
    """
    tow_eff_treat_system = tow * t * (1 - tow_rem)
    return tow_eff_treat_system


def s_aerobic(s_mass, k_rem):
    """
    Equation 6.3b (tier 1)

    Organic component removed as sludge from aerobic treatment plants.

    Argument
    --------
    s_mass (t/year) : float
        amount of raw sludge removed from wastewater treatment as dry mass
    k_rem (kg/kg) : float
        sludge factor, kg BOD/ kg sludge

    Returns
    -------
    VALUE: float
        organic component removed from wastewater (kg/year)
    """
    s_aerobic = s_mass * k_rem * 1000
    return s_aerobic


def s_septic(tow_septic, f):
    """
    Equation 6.3c (tier 1)

    Organic component removed as sludge from septic systems.

    Argument
    --------
    tow_septic (kg/year) : float
        total organics in wastewater in septic systems, kg bod/ yr
    f (kg/kg) : float
        fraction of the population managing their septic tank in compliance with instruction

    Returns
    -------
    VALUE: float
        organic component removed from wastewater (kg/year)
    """
    s_septic = tow_septic * f * 0.5
    return s_septic


def ef_ch4_ind(B0, MCF):
    """
    Equation 6.5 (tier 1)

    Industrial wastewater
    Calculates the CH4 emission factor per treatment/discharge system.

    Argument
    --------
    B0 (kg/kg) : float
        maximum CH4 producing capacity (kg CH4/ kg COD)
    MCF (kg/kg) : float
        methane correction factor (fraction)

    Returns
    -------
    VALUE: float
        CH4 emission factor (kg/kg)
    """
    ef_ch4_ind = B0 * MCF
    return ef_ch4_ind


def ch4_emissions_system_ind(tow, s, ef, r):
    """
    Equation 6.4 (tier 1)

    Industrial wastewater
    Calculates the CH4 emissions from industrial wastewater treatment per system.

    Argument
    --------
    tow (kg/year) : float
        organics in wastewater of the treatment/discharge system (kg cod/yr)
    s (kg/year) : float
        organic component removed from the wastewater of the system (kg cod/yr)
    ef (kg/kg) : float
        emission factor for the system (kg ch4 / kg cod)
    r (kg/year) : float
        amount of CH4 recovered from the system (kg CH4 /yr)

    Returns
    -------
    VALUE: float
        CH4 emissions for treatment/discharge system (kg/year)
    """
    ch4_emissions_system_ind = (tow - s) * ef - r
    return ch4_emissions_system_ind


def tn_domestic(p_treatment, protein, f_npr, n_hh, f_non_con, f_ind_com):
    """
    Equation 6.10

    Total nitrogen in domesetic wastewater by treatment pathway.

    Argument
    --------
    p_treatment (cap/year) : float
        population who are served by the treatment pathway
    protein (kg/cap/year) : float
        annual per capita protein consumption
    f_npr (kg/kg) : float
        fraction of nitrogen in protein, default 0.16
    n_hh (kg/kg) : float
        factor that adds nitrogen from household products to the wastewater, default 1.1
    f_non_con (kg/kg) : float
        factor for nitrogen in non-consumed protein disposed in sewer system
    f_ind_com (kg/kg) : float
        factor for indsutriyl and commercial co-discharged protein into the sewer system

    Returns
    -------
    VALUE: float
        TN_DOM (kg/year)
        total annual amount of nitrogen in domestic wastewater
    """
    tn_domestic = p_treatment * protein * f_npr * n_hh * f_non_con * f_ind_com
    return tn_domestic


def protein(protein_supply, fpc):
    """
    Equation 6.10a

    Protein consumptions based on Protein supply (e.g. FAOSTAT data)

    Argument
    --------
    protein_supply (kg/cap/yr) : float
        annual per capita protein supply
    fpc (kg/kg) float
        fraction of protein consumed

    Returns
    -------
    VALUE : float
        protein (kg/cap/yr)
        Protein consumption
    """
    protein = protein_supply * fpc
    return protein


def n_effluent_dom_system(tn_dom, t, n_rem):
    """
    Equation 6.8 (updated)

    Total nitrogen in domestic wastewater effluent.

    Argument
    --------
    tn_dom (kg/year) : float
        total nitrogen in domestic wastewater in inventory year
    t (kg/kg) : float
        degree of utilisation of treatment system
    n_rem (kg/kg) : float
        fraction of total wastewater nitrogen removed during treatment

    Returns
    -------
    VALUE: float
        N_EFFLUENT (kg/year)
        total nitrogen in the wastewater effluent discharged to aquatic environments
    """
    n_effluent_dom_system = (tn_dom * t) * (1 - n_rem)
    return n_effluent_dom_system


def n2o_plants(u, t, ef, tn_dom):
    """
    Equation 6.9 (updated)

    N2O emissions from domestic wastewater treatment plants.
    Contrary to guidelines, no summation over treatments and income groups.

    Argument
    --------
    u (cap/cap) : float
        fraction of population in income group i in inventory year
    t (kg/kg) : float
        degree of utilization of treatment/discharge system for each income group
    ef kg/kg) : float
        emission factor for treatment/discharge system, kg n2o / kg n
    tn_dom (kg/yr) : float
        total nitrogen in domestic wastewater in inventory year

    Returns
    -------
    VALUE : float
        N2O_PLANTS (kg/yr)
        total N2O emissions from plants in inventory year
    """
    n2o_plants = u * t * ef * tn_dom * 44 / 28
    return n2o_plants


def n2o_effluent(n_effluent, ef_effluent):
    """
    Equation 6.7 (updated)

    N2O emissions from domestic wastewater effluent

    Argument
    --------
    n_effluent (kg/yr) : float
        nitrogen in the effluent discharged to aquatic environments, kg n / yr
    ef_effluent (kg/kg) : float
        emssion factor for N2O emissions from wastewater discharged to aquatic systems, kg N2O / kg N

    Returns
    -------
    VALUE : float
        N2O_EFFLUENT (kg/yr)
        N2O emissions from domestic wastewater effluent
    """
    n2o_effluent = n_effluent * ef_effluent
    return n2o_effluent


def tn_industry(p, w, tn):
    """
    Equation 6.13

    Total nitrogen in wastewater entering treatment for industry.

    Argument
    --------
    p (t/year) : float
        total industry product
    w (m3/t) : float
        wastewater generated for industrial sector product
    tn (kg/kg) : float
        total nitrogen in untreated wastewater for industrial sector

    Returns
    -------
    VALUE: float
        TN_IND (kg/year)
        total annual amount of nitrogen in industrial wastewater
    """
    tn_industry = p * w * tn
    return tn_industry


def n_effluent_ind(tn_ind, t_ind, n_rem):
    """
    Equation 6.14

    Total nitrogen in domestic wastewater effluent.
    Contrary to giudelines no summation over treatment type.

    Argument
    --------
    tn_ind (kg/year) : float
        total nitrogen in industrial wastewater in inventory year
    t (kg/kg) : float
        degree of utilisation of treatment system in industry
    n_rem (kg/kg) : float
        fraction of total wastewater nitrogen removed during treatment

    Returns
    -------
    VALUE: float
        N_EFFLUENT (kg/year)
        total nitrogen in the industrial wastewater effluent discharged to aquatic environments
    """
    n_effluent_ind = (tn_ind * t_ind) * (1 - n_rem)
    return n_effluent_ind


def n2o_effluent_ind(n_effluent_ind, ef_effluent):
    """
    Equation 6.12

    N2O emissions from industrial wastewater effluent

    Argument
    --------
    n_effluent_ind (kg/yr) : float
        nitrogen in industrial wastewater effluent discharged to aquatic environments, kg n / yr
    ef_effluent (kg/kg) : float
        emssion factor for N2O emissions from wastewater discharged to aquatic systems, kg N2O / kg N

    Returns
    -------
    VALUE : float
        N2O_EFFLUENT (kg/yr)
        N2O emissions from industrial wastewater effluent
    """
    n2o_effluent_ind = n_effluent_ind * ef_effluent
    return n2o_effluent_ind


def n2o_plants_ind(t_ind, ef, tn_ind):
    """
    Equation 6.11

    N2O emissions from industrial wastewater treatment plants.
    Contrary to guidelines, no summation over treatments and income groups.

    Argument
    --------
    t_ind (kg/kg) : float
        degree of utilization of treatment/discharge system for each industry
    ef kg/kg) : float
        emission factor for treatment/discharge system, kg n2o / kg n
    tn_ind (kg/yr) : float
        total nitrogen in indsutrial wastewater in inventory year

    Returns
    -------
    VALUE : float
        N2O_PLANTS (kg/yr)
        total N2O emissions from plants in inventory year
    """
    n2o_plants_ind = t_ind * ef * tn_ind * 44 / 28
    return n2o_plants_ind
