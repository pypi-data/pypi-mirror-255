def co2_coke_tier1a_(ck, ef_co2):
    """
    Equation 4.1 (tier 1a).

    This function calculates the CO2 emissions from coke production.

    Argument
    --------
    ck (t/year): float
        Quantity of coke produced.
    ef_co2 (t/t): float
        Emission factor CO2.

    Returns
    -------
    co2_coke_tier1a_ (t/year): float
        Total CO2 emissions generated from coke production (in tonnes CO2).

    """
    co2_coke_tier1a_ = ck * ef_co2
    return co2_coke_tier1a_


def ch4_coke_tier1a_(ck, ef_ch4):
    """
    Equation 4.1a (tier 1a).

    This function calculates the CH4 emissions from coke production.

    Argument
    --------
    ck (t/year): float
        Quantity of coke produced.
    ef_ch4 (t/t): float
        Emission factor CO2.

    Returns
    -------
    ch4_coke_tier1a_ (t/year): float
        Total CH4 emissions generated from coke production (in tonnes CH4).

    """
    ch4_coke_tier1a_ = ck * ef_ch4
    return ch4_coke_tier1a_


def co2_coke_tier1b_(cc, ck, c_cc, c_ck):
    """
    Equation 4.1b (tier 1b).

    This function calculates the CO2 emissions from coke production.

    Argument
    --------
    ck (t/year): float
        Quantity of coke produced.
    cc (t/year): float
        Quantity of coking coal produced.
    c_ck (t/t): float
        default carbon content of metallurgical coke.
    c_cc (t/t): float
        default carbon content of coking coal.

    Returns
    -------
    co2_coke_tier1b_ (t/year): float
        Total CO2 emissions generated from coke production (in tonnes CO2).

    """
    co2_coke_tier1b_ = (cc * c_cc - ck * c_ck) * 44 / 12
    return co2_coke_tier1b_


def co2_coke_tier2_(
    cc, c_cc, pm_a, c_a, bg, c_bg, co, c_co, cog, c_cog, cob_b, c_b, e_flaring
):
    """
    Equation 4.2 (tier 2).

    This function calculates the CO2 emissions from coke production.

    Argument
    --------
    cc (t/year): float
        Quantity of coking coal produced.
    c_cc (t/t): float
        country-specific carbon content of coking coal.
    pm_a (t/yr): float
        quantity of process materials consumed for metallurgical coke production
    c_a (t/t): float
        country-specific carbon content of material input
    bg (t/yr): float
        quantity of blast furnace gas consumed in coke oven
    c_bg (t/t): float
        country-specific carbon content of blast furnace gas
    co (t/yr): float
        quantity of metallurgical coke produced
    c_co (t/t): float
        country-specific carbon content of metallurgical coke
    cog (t/yr): float
        quantity of coke oven gas produced but not recirculated and therefore not consumed for metallurgical coke production
    c_cog (t/t): float
        country-specific carbon content of coke oven gas
    cob_b (t/yr): float
        quantity of coke oven by-product
    c_b (t/t): float
        country-specific carbon content of by-product
    e_flaring (t/yr): float
        co2 emissions from flaring, deducted from the carbon mass balance, as the corresponding emissions are estimated as fugitive emissions using the methodology described in Section 4.3.2.2 Chapter 4 Volume 2 of the 2019 Refinement


    Returns
    -------
    co2_coke_tier2_ (t/year): float
        Total CO2 emissions generated from coke production (in tonnes CO2).

    """
    co2_coke_tier2_ = (
        (
            cc * c_cc
            + pm_a * c_a
            + bg * c_bg
            - co * c_co
            - cog * c_cog
            - cob_b * c_b
            - e_flaring
        )
        * 44
        / 12
    )
    return co2_coke_tier2_
