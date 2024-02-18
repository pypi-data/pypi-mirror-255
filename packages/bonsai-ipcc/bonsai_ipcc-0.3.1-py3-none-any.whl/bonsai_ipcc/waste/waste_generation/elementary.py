def msw_to_swds(urb_population, msw_gen_rate, msw_frac_to_swds, msw_type_frac):
    """
    Equation 2.x (not explicit in guidelines, tier 1)

    Calculates the amount of municipal solid waste (MSW) disposed to solid waste disposal sites (swdS),
    by using default data from chapter 2 (Waste Generation, Composition amd Management).

    Argument
    --------
    urb_population (cap/year) : float
        Urban population of a region in a given year.
    msw_gen_rate (t/cap) : float
        rate of municipal solid waste per capita.
    msw_frac_to_swds (kg/kg) : float
        fraction of waste disposed to swds in municipal solid waste.
    msw_frac (kg/kg) : float
        Fraction of waste type in municipal solid waste.

    Returns
    -------
    VALUE: float
        amount of certain MSW type sent to swdS (tonnes/year)
    """

    msw_to_swds = urb_population * msw_gen_rate * msw_frac_to_swds * msw_type_frac
    return msw_to_swds


def msw_to_incin(urb_population, msw_gen_rate, msw_frac_to_incin, msw_type_frac):
    """
    Equation 2.y (not explicit in guidelines, tier 1)

    Calculates the amount of municipal solid waste (MSW) disposed to incineration sites,
    by using default data from chapter 2 (Waste Generation, Composition amd Management).

    Argument
    --------
    urb_population (cap/year) : float
        Urban population of a region in a given year.
    msw_gen_rate (t/cap) : float
        rate of municipal solid waste per capita.
    msw_frac_to_incin (kg/kg) : float
        Fraction of waste disposed to incineration in municipal solid waste.

    Returns
    -------
    VALUE: float
        amount of certain MSW type which is incinerated (tonnes/year)
    """

    msw_to_incin = urb_population * msw_gen_rate * msw_frac_to_incin * msw_type_frac
    return msw_to_incin


def msw_open_burned(total_population, p_frac, msw_gen_rate, b_frac, msw_type_frac):
    """
    Equation 5.7 (has been removed from chapter 5)

    Calculates the amount of MSW that is open-burned.
    Slightly modified compared to original equation.

    Argument
    --------
    population (cap/year) : float
        total poulation in a region
    p_frac (cap/cap) : float
        Fraction of capita that burnes waste.
    msw_gen_rate (t/cap) : float
        msw generation per capita.
    b_frac (kg/kg) : float
        fraction of waste that is burned relative to total amount of waste.
    msw_type_frac (kg/kg) : float
        Fraction of waste type in MSW.

    Returns
    -------
    VALUE: float
        amount of certain MSW type which is open burned (Gg/year)
    """

    msw_open_burned = (
        total_population * p_frac * msw_gen_rate * b_frac * msw_type_frac * 0.001
    )
    return msw_open_burned


def msw_to_biotreat(
    urb_population, msw_gen_rate, msw_frac_to_biotreat, msw_type_frac_bio
):
    """
    Equation 2.z (not explicit in guidelines, tier 1)

    Calculates the amount of municipal solid waste (MSW) that is composted,
    by using default data from chapter 2 (Waste Generation, Composition amd Management).

    Argument
    --------
    urb_population (cap/year) : float
        Urban population of a region in a given year.
    msw_gen_rate (t/cap) : float
        rate of municipal solid waste per capita.
    msw_frac_to_compost (kg/kg) : float
        fraction of waste in municipal solid waste which is composted.
    msw_type_frac_bio (kg/kg) : float
        Fraction of biodegradable waste type.
        (e.g. food, garden, wood and paper fractions)

    Returns
    -------
    VALUE: float
        amount of certain MSW type which is composted (tonnes/year)
    """

    msw_to_biotreat = (
        urb_population * msw_gen_rate * msw_frac_to_biotreat * msw_type_frac_bio
    )
    return msw_to_biotreat


def ww_domestic(p, bod):
    """
    Equation 6.3 (has been removed from chapter 6)

    Calculates domestic wastewater amount,
    expressd as total organically degradable material in domestic wastewater (TOW).

    Argument
    --------
    p (cap) : float
        country population in inventory year (person)
    bod (g/cap/day) : float
        country-specific per capita BOD in inventory year

    Returns
    -------
    VALUE: float
        total organics in wastewater TOW (kg/year)
    """
    ww_domestic = p * bod * 0.001 * 365
    return ww_domestic


def ww_industrial(p, w, cod):
    """
    Equation 6.6 (has been removed from chapter 6)

    Calculates industrial wastewater amount,
    expressed as total organically degradable material in domestic wastewater (TOW).

    Argument
    --------
    p (t/yr) : float
        total industrial product output of the sector
    w (m3/t) : float
        wastewater generated m3/t
    cod (kg/m3) : float
        chemical oxygen demand (industrial degradable organic component in wastewater)

    Returns
    -------
    VALUE: float
        total organics in wastewater TOW (kg/year)
    """
    ww_industrial = p * w * cod
    return ww_industrial


def waste_to_treatment(waste, treatmentrate):
    """
    Equation 2.x (not explicit in the guidelines).

    Allocates the total generated amount of waste to a treatment technology.

    Argument
    --------
    waste (Gg/year) : float
        total amount of waste type
    treatmentrate (kg/kg) : float
        ratio of a certain treatment route (e.g 'incineration', 'swd', 'biological')

    Returns
    -------
    VALUE : float
        amount of waste that is treated in a treatment route (Gg/year)
    """
    waste_to_treatment = waste * treatmentrate
    return waste_to_treatment


def waste_to_technology(waste, technologyrate):
    """
    Equation 2.x (not explicit in the guidelines).

    Allocates the total generated amount of waste to a treatment technology.

    Argument
    --------
    waste (Gg/year) : float
        total amount of waste type
    technologyrate (kg/kg) : float
        ratio of a certain technology within a treatment route (e.g 'continous' in incineration)

    Returns
    -------
    VALUE : float
        amount of waste that is treated by a technology (Gg/year)
    """
    waste_to_technology = waste * technologyrate
    return waste_to_technology


def isw_total(gdp, waste_gen_rate):
    """
    Equation 2.x (not explicit in the guidelines, tier 1).

    Estimates total indsutrial solid waste based on GDP.

    Argument
    --------
    gdp (MUSD/year) : float
        Gross domestic product of a region in Million US Dollar
    waste_gen_rate (Gg/MUSD) : float
        waste generation rate

    Returns
    -------
    VALUE : float
        amount of solid industrial waste (Gg/year)
    """
    isw_total = gdp * waste_gen_rate
    return isw_total


def biogenic_frac(fossil_C, total_C):
    """
    Equation 2.x (not explicit in the guidelines, tier 1).

    Estimates biogenic waste fraction based Carbon content.

    Argument
    --------
    total_C (kg/kg) : float
        total Carbon per waste type
    fossil carbon (kg/kg) : float
        fossil Carbon per waste type

    Returns
    -------
    VALUE : float
        biogenic fraction of waste (kg/kg)
    """
    biogenic_frac = (total_C - fossil_C) / total_C
    return biogenic_frac
