"""
Sequences to determine GHG emissions from solid waste disposal (swd).

Decision tree for CH4:
    - tier 1: FOD method using mainly default activity data and default parameters.
              (requirement: swd is not a key category)
    - tier 2: FOD method and some default parameters,
              but good quality country-specific data on current and historical waste disposal at swds.
              Historical waste disposal data for 10 years or more should be based on country-specific statistics.
    - tier 3: good quality country-specific activity data (see Tier 2) and the use of either the FOD method with
              (1) nationally developed key parameters, or (2) measurement derived country-specific parameter.

Comments on CH4 and N2O:
    - equations for quantifying C2O emissions are not explicitly provided by IPCC guidelines, since
      those are of biogenic origin. However, CO2 emissions occur and can be quantified by additionaly provided
      elementary equations.
    - methodolgy for N2O emissions is not provided by IPCC guidelines, since those are "not significant"
"""

import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def tier1_ch4(
    year=2010,
    region="BG",
    wastetype="msw_food",
    wastemoisture="wet",
    past_years=0,
    landfilltype="uncharacterised",
    uncertainty="def",
):
    """Template calculation sequence for tier 1 method.

    CH4 Emissions in year y, due to waste deposed in past year y-n.
    Defines a sequence of steps.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    wastetype : str
        Fraction of solid waste.
    wastemoisture : str
        'wet' or 'dry'. Specifies if waste amount is measured as dry-matter or wet.
    past_years : int
        number of past years to be considered for waste generation. good practice is 60 years.
    landfilltype : str
        Management of solid waste disposal side.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    logger.info("swd sequence started --->")
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    seq.store_signature(locals())

    value_list = []
    year_list = []

    for y in range(year - past_years, year + 1):

        if wastetype.startswith("msw_"):

            # 1: read parameters first function
            seq.read_parameter(
                name="urb_population", table="urb_population", coords=[y, region]
            )

            seq.read_parameter(
                name="msw_gen_rate", table="msw_gen_rate", coords=[y, region]
            )

            seq.read_parameter(
                name="msw_frac_to_swds",
                table="msw_frac_to_swds",
                coords=[y, region],
            )

            seq.read_parameter(
                name="msw_type_frac",
                table="msw_type_frac",
                coords=[y, region, wastetype],
            )

            value = (
                seq.elementary.msw_to_swds(
                    urb_population=seq.step.urb_population.value,
                    msw_gen_rate=seq.step.msw_gen_rate.value,
                    msw_frac_to_swds=seq.step.msw_frac_to_swds.value,
                    msw_type_frac=seq.step.msw_type_frac.value,
                )
                / 1000
            )  # from tonnes to Gg

            value_list.append(value)
            year_list.append(y)

        else:
            seq.read_parameter(name="gdp", table="gdp", coords=[y, region])

            seq.read_parameter(
                name="isw_gen_rate", table="isw_gen_rate", coords=[y, region]
            )

            value = seq.elementary.isw_total(
                gdp=seq.step.gdp.value, waste_gen_rate=seq.step.isw_gen_rate.value
            )

            seq.read_parameter(
                name="isw_frac_to_swds", table="isw_frac_to_swds", coords=[y, region]
            )

            value = seq.elementary.waste_to_treatment(
                waste=value, treatmentrate=seq.step.isw_frac_to_swds.value
            )

            value_list.append(value)
            year_list.append(y)

    seq.store_result(
        name="w_per_treat", value=value_list, unit="Gg/year", year=year_list
    )

    value_list = []
    year_list = []

    for y in range(year - past_years, year + 1):
        seq.read_parameter(
            name="swdstype_frac",
            table="swdstype_frac",
            coords=[y, region, landfilltype],
        )

        value = seq.elementary.waste_to_technology(
            waste=seq.step.w_per_treat.value[year - y],
            technologyrate=seq.step.swdstype_frac.value,
        )
        value_list.append(value)
        year_list.append(y)

    seq.store_result(
        name="w_per_tech", value=value_list, unit="Gg/year", year=year_list
    )

    # 2: read parameters second function
    seq.read_parameter(
        name="doc", table="doc", coords=[region, wastetype, wastemoisture]
    )

    seq.read_parameter(name="doc_f", table="doc_f", coords=[region, wastetype])

    seq.read_parameter(name="mcf", table="mcf", coords=[landfilltype])

    value_list = []
    year_list = []
    for y in range(year - past_years, year + 1):
        value = seq.elementary.ddoc_from_wd_data(
            seq.step.w_per_tech.value[year - y],
            doc=seq.step.doc.value,
            doc_f=seq.step.doc_f.value,
            mcf=seq.step.mcf.value,
        )
        value_list.append(value)
        year_list.append(y)

    seq.store_result(
        name="ddoc_from_wd_data",
        value=value_list,
        unit="gg/year",
        year=year_list,
    )

    # 3: read parameters third function
    seq.read_parameter(name="climate_zone", table="climate_zone", coords=[region])

    seq.read_parameter(name="moisture_regime", table="moisture_regime", coords=[region])

    seq.read_parameter(
        name="k",
        table="k",
        coords=[wastetype, seq.step.moisture_regime.value, seq.step.climate_zone.value],
    )

    value = 0
    value_list = []
    year_list = []
    for y in range(year - past_years, year + 1):
        value = seq.elementary.ddoc_ma_t(
            seq.step.ddoc_from_wd_data.value[year - y],
            value,
            seq.step.k.value,
        )
        value_list.append(value)
        year_list.append(y)

    seq.store_result(
        name="ddoc_ma_t",
        value=value_list,
        unit="Gg/year",
        year=year_list,
    )

    value = seq.elementary.ddoc_m_decomp_t(
        seq.step.ddoc_ma_t.value[-2],
        seq.step.k.value,  # -2, beacause value dpends on the accumalation in year before
    )
    seq.store_result(
        name="ddoc_m_decomp_t",
        value=value,
        unit="Gg/year",
        year=year,
    )

    # 4: read parameters forth function
    seq.read_parameter(name="f", table="f", coords=[])

    value = seq.elementary.ch4_generated(
        seq.step.ddoc_m_decomp_t.value, seq.step.f.value
    )

    seq.store_result(
        name="ch4_generated",
        value=value,
        unit="Gg/year",
        year=year,
    )

    # 5: read parameter for fith equation
    seq.read_parameter(name="ox", table="ox", coords=[landfilltype])

    seq.read_parameter(name="r", table="r_swd", coords=[year, region, landfilltype])

    value = seq.elementary.ch4_emissions(
        seq.step.ch4_generated.value, ox=seq.step.ox.value, r=seq.step.r.value
    )

    seq.store_result(
        name="ch4",
        value=value,
        unit="Gg/year",
        year=year,
    )
    logger.info("---> swd sequence finalized.")
    return seq.step


def tier1_ch4_prospective(
    year=2010,
    region="BG",
    wastetype="msw_food",
    wastemoisture="wet",
    landfilltype="uncharacterised",
    prospective_years=20,
    uncertainty="def",
):
    """Template calculation sequence for tier 1 method.

    CH4 Emissions in prospective years y+n, due to waste deposed in year y.
    Defines a sequence of steps.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    wastetype : str
        Fraction of solid waste.
    wastemoisture : str
        'wet' or 'dry'
        Specifies if waste amount is measured as dry-matter or wet.
    landfilltype : str
        Management of solid waste disposal side.
    prospective_years : int
        prospective years under study
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    logger.info("swd sequence started --->")
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    seq.store_signature(locals())

    if wastetype.startswith("msw_"):
        # 1: read parameters first function
        seq.read_parameter(
            name="urb_population", table="urb_population", coords=[year, region]
        )

        seq.read_parameter(
            name="msw_gen_rate", table="msw_gen_rate", coords=[year, region]
        )

        seq.read_parameter(
            name="msw_frac_to_swds",
            table="msw_frac_to_swds",
            coords=[year, region],
        )

        seq.read_parameter(
            name="msw_type_frac",
            table="msw_type_frac",
            coords=[year, region, wastetype],
        )

        value = (
            seq.elementary.msw_to_swds(
                urb_population=seq.step.urb_population.value,
                msw_gen_rate=seq.step.msw_gen_rate.value,
                msw_frac_to_swds=seq.step.msw_frac_to_swds.value,
                msw_type_frac=seq.step.msw_type_frac.value,
            )
            / 1000
        )  # from tonnes to Gg

        seq.store_result(
            name="w_per_treat",
            value=value,
            unit="Gg/year",
            year=year,
        )
    else:
        seq.read_parameter(name="gdp", table="gdp", coords=[year, region])

        seq.read_parameter(
            name="isw_gen_rate", table="isw_gen_rate", coords=[year, region]
        )

        value = seq.elementary.isw_total(
            gdp=seq.step.gdp.value, waste_gen_rate=seq.step.isw_gen_rate.value
        )
        seq.store_result(name="w", value=value, unit="gg/year", year=year)

        seq.read_parameter(
            name="isw_frac_to_swds", table="isw_frac_to_swds", coords=[year, region]
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.w.value, treatmentrate=seq.step.isw_frac_to_swds.value
        )
        seq.store_result(name="w_per_treat", value=value, unit="Gg/year", year=year)

    seq.read_parameter(
        name="swdstype_frac", table="swdstype_frac", coords=[year, region, landfilltype]
    )

    value = seq.elementary.waste_to_technology(
        waste=seq.step.w_per_treat.value, technologyrate=seq.step.swdstype_frac.value
    )
    seq.store_result(name="w_per_tech", value=value, unit="Gg/year", year=year)

    # 2: read parameters second function
    seq.read_parameter(
        name="doc", table="doc", coords=[region, wastetype, wastemoisture]
    )

    seq.read_parameter(name="doc_f", table="doc_f", coords=[region, wastetype])

    seq.read_parameter(name="mcf", table="mcf", coords=[landfilltype])

    value = seq.elementary.ddoc_from_wd_data(
        seq.step.w_per_tech.value,
        doc=seq.step.doc.value,
        doc_f=seq.step.doc_f.value,
        mcf=seq.step.mcf.value,
    )
    seq.store_result(
        name="ddoc_from_wd_data",
        value=value,
        unit="Gg/year",
        year=year,
    )

    # 3: read parameters third and forth and fith function
    seq.read_parameter(name="climate_zone", table="climate_zone", coords=[region])

    seq.read_parameter(name="moisture_regime", table="moisture_regime", coords=[region])

    seq.read_parameter(
        name="k",
        table="k",
        coords=[wastetype, seq.step.moisture_regime.value, seq.step.climate_zone.value],
    )

    seq.read_parameter(name="f", table="f", coords=[])

    seq.read_parameter(name="ox", table="ox", coords=[landfilltype])

    seq.read_parameter(name="r", table="r_swd", coords=[year, region, landfilltype])

    # loop
    ddoc_ma_t_1 = seq.step.ddoc_from_wd_data.value

    ch4_per_years = []
    year_list = []
    for y in list(range(prospective_years)):
        ddoc_m_decomp_t = seq.elementary.ddoc_m_decomp_t(ddoc_ma_t_1, seq.step.k.value)
        # 5: execute third equation and store results
        ch4_generated = seq.elementary.ch4_generated(ddoc_m_decomp_t, seq.step.f.value)
        # 7: execute forth equation and store results
        ch4_per_year = seq.elementary.ch4_emissions(
            ch4_generated, ox=seq.step.ox.value, r=seq.step.r.value
        )
        ch4_per_years.append(ch4_per_year)
        year_list.append(y + 1)
        ddoc_ma_t_1 -= ddoc_m_decomp_t

    year_list = [y + year for y in year_list]

    seq.store_result(
        name="ch4_prospective",
        value=ch4_per_years,
        unit="Gg/year",
        year=year_list,
    )
    logger.info("---> swd sequence finalized.")
    return seq.step


def tier2_ch4(
    year=2010,
    region="BG",
    wastetype="msw_food",
    wastemoisture="wet",
    past_years=0,
    landfilltype="uncharacterised",
    uncertainty="def",
):
    """Template calculation sequence for tier 2 method.

    CH4 Emissions in year y, due to waste deposed in past year y-n.
    Defines a sequence of steps.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    wastetype : str
        Fraction of solid waste.
    wastemoisture : str
        'wet' or 'dry'
        Specifies if waste amount is measured as dry-matter or wet.
    past_years : int
        number of past years to be considered for waste generation.
        good practice is 60 years.
    landfilltype : str
        Management of solid waste disposal side.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    logger.info("swd sequence started --->")
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    seq.store_signature(locals())

    value_list = []
    year_list = []

    for y in range(year - past_years, year + 1):
        if wastetype.startswith("msw_"):
            seq.read_parameter(name="sw", table="sw", coords=[year, region, wastetype])

            seq.read_parameter(
                name="msw_frac_to_swds", table="msw_frac_to_swds", coords=[year, region]
            )

            value = seq.elementary.waste_to_treatment(
                waste=seq.step.sw.value, treatmentrate=seq.step.msw_frac_to_swds.value
            )
            value_list.append(value)
            year_list.append(y)

        elif wastetype.startswith("isw_"):
            seq.read_parameter(name="sw", table="sw", coords=[year, region, wastetype])

            seq.read_parameter(
                name="isw_frac_to_swds", table="isw_frac_to_swds", coords=[year, region]
            )

            value = seq.elementary.waste_to_treatment(
                waste=seq.step.sw.value, treatmentrate=seq.step.isw_frac_to_swds.value
            )
            value_list.append(value)
            year_list.append(y)

    seq.store_result(
        name="w_per_treat", value=value_list, unit="Gg/year", year=year_list
    )

    value_list = []
    year_list = []

    for y in range(year - past_years, year + 1):
        seq.read_parameter(
            name="swdstype_frac",
            table="swdstype_frac",
            coords=[y, region, landfilltype],
        )

        value = seq.elementary.waste_to_technology(
            waste=seq.step.w_per_treat.value[year - y],
            technologyrate=seq.step.swdstype_frac.value,
        )
        value_list.append(value)
        year_list.append(y)

    seq.store_result(
        name="w_per_tech", value=value_list, unit="gg/year", year=year_list
    )

    # 2: read parameters second function
    seq.read_parameter(
        name="doc", table="doc", coords=[region, wastetype, wastemoisture]
    )

    seq.read_parameter(name="doc_f", table="doc_f", coords=[region, wastetype])

    seq.read_parameter(name="mcf", table="mcf", coords=[landfilltype])

    value_list = []
    year_list = []
    for y in range(year - past_years, year + 1):
        value = seq.elementary.ddoc_from_wd_data(
            seq.step.w_per_tech.value[year - y],
            doc=seq.step.doc.value,
            doc_f=seq.step.doc_f.value,
            mcf=seq.step.mcf.value,
        )
        value_list.append(value)
        year_list.append(y)

    seq.store_result(
        name="ddoc_from_wd_data",
        value=value_list,
        unit="Gg/year",
        year=year_list,
    )

    # 3: read parameters third function
    seq.read_parameter(name="climate_zone", table="climate_zone", coords=[region])

    seq.read_parameter(name="moisture_regime", table="moisture_regime", coords=[region])

    seq.read_parameter(
        name="k",
        table="k",
        coords=[wastetype, seq.step.moisture_regime.value, seq.step.climate_zone.value],
    )

    value = 0
    value_list = []
    year_list = []
    for y in range(year - past_years, year + 1):
        value = seq.elementary.ddoc_ma_t(
            seq.step.ddoc_from_wd_data.value[year - y],
            value,
            seq.step.k.value,
        )
        value_list.append(value)
        year_list.append(y)

    seq.store_result(
        name="ddoc_ma_t",
        value=value_list,
        unit="Gg/year",
        year=year_list,
    )

    value = seq.elementary.ddoc_m_decomp_t(
        seq.step.ddoc_ma_t.value[-2],
        seq.step.k.value,  # -2, beacause value dpends on the accumalation in year before
    )
    seq.store_result(
        name="ddoc_m_decomp_t",
        value=value,
        unit="Gg/year",
        year=year,
    )

    # 4: read parameters forth function
    seq.read_parameter(name="f", table="f", coords=[])

    value = seq.elementary.ch4_generated(
        seq.step.ddoc_m_decomp_t.value, seq.step.f.value
    )

    seq.store_result(
        name="ch4_generated",
        value=value,
        unit="Gg/year",
        year=year,
    )

    # 5: read parameter for fith equation
    seq.read_parameter(name="ox", table="ox", coords=[landfilltype])

    seq.read_parameter(name="r", table="r_swd", coords=[year, region, landfilltype])

    value = seq.elementary.ch4_emissions(
        seq.step.ch4_generated.value, ox=seq.step.ox.value, r=seq.step.r.value
    )

    seq.store_result(
        name="ch4",
        value=value,
        unit="Gg/year",
        year=year,
    )
    logger.info("---> swd sequence finalized.")
    return seq.step


def tier2_ch4_prospective(
    year=2010,
    region="BG",
    wastetype="msw_food",
    wastemoisture="wet",
    landfilltype="uncharacterised",
    prospective_years=20,
    uncertainty="def",
):
    """Template calculation sequence for tier 2 method.

    CH4 Emissions in prospective years y+n, due to waste deposed in year y.
    Defines a sequence of steps.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    wastetype : str
        Fraction of solid waste.
    wastemoisture : str
        'wet' or 'dry'
        Specifies if waste amount is measured as dry-matter or wet.
    landfilltype : str
        Management of solid waste disposal side.
    prospective_years : int
        prospective years under study
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    logger.info("swd sequence started --->")
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    seq.store_signature(locals())

    if wastetype.startswith("msw_"):
        seq.read_parameter(name="sw", table="sw", coords=[year, region, wastetype])

        seq.read_parameter(
            name="msw_frac_to_swds", table="msw_frac_to_swds", coords=[year, region]
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.sw.value, treatmentrate=seq.step.msw_frac_to_swds.value
        )
        seq.store_result(name="w_per_treat", value=value, unit="Gg/year", year=year)

    elif wastetype.startswith("isw_"):
        seq.read_parameter(name="sw", table="sw", coords=[year, region, wastetype])

        seq.read_parameter(
            name="isw_frac_to_swds", table="isw_frac_to_swds", coords=[year, region]
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.sw.value, treatmentrate=seq.step.isw_frac_to_swds.value
        )
        seq.store_result(name="w_per_treat", value=value, unit="Gg/year", year=year)

    seq.read_parameter(
        name="swdstype_frac", table="swdstype_frac", coords=[year, region, landfilltype]
    )

    value = seq.elementary.waste_to_technology(
        waste=seq.step.w_per_treat.value, technologyrate=seq.step.swdstype_frac.value
    )
    seq.store_result(name="w_per_tech", value=value, unit="Gg/year", year=year)

    # 2: read parameters second function
    seq.read_parameter(
        name="doc", table="doc", coords=[region, wastetype, wastemoisture]
    )

    seq.read_parameter(name="doc_f", table="doc_f", coords=[region, wastetype])

    seq.read_parameter(name="mcf", table="mcf", coords=[landfilltype])

    value = seq.elementary.ddoc_from_wd_data(
        seq.step.w_per_tech.value,
        doc=seq.step.doc.value,
        doc_f=seq.step.doc_f.value,
        mcf=seq.step.mcf.value,
    )
    seq.store_result(
        name="ddoc_from_wd_data",
        value=value,
        unit="Gg/year",
        year=year,
    )

    # 3: read parameters third and forth and fith function
    seq.read_parameter(name="climate_zone", table="climate_zone", coords=[region])

    seq.read_parameter(name="moisture_regime", table="moisture_regime", coords=[region])

    seq.read_parameter(
        name="k",
        table="k",
        coords=[wastetype, seq.step.moisture_regime.value, seq.step.climate_zone.value],
    )

    seq.read_parameter(name="f", table="f", coords=[])

    seq.read_parameter(name="ox", table="ox", coords=[landfilltype])

    seq.read_parameter(name="r", table="r_swd", coords=[year, region, landfilltype])

    # loop
    ddoc_ma_t_1 = seq.step.ddoc_from_wd_data.value

    ch4_per_years = []
    year_list = []
    for y in list(range(prospective_years)):
        ddoc_m_decomp_t = seq.elementary.ddoc_m_decomp_t(ddoc_ma_t_1, seq.step.k.value)
        # 5: execute third equation and store results
        ch4_generated = seq.elementary.ch4_generated(ddoc_m_decomp_t, seq.step.f.value)
        # 7: execute forth equation and store results
        ch4_per_year = seq.elementary.ch4_emissions(
            ch4_generated, ox=seq.step.ox.value, r=seq.step.r.value
        )
        ch4_per_years.append(ch4_per_year)
        year_list.append(y + 1)
        ddoc_ma_t_1 -= ddoc_m_decomp_t

    year_list = [y + year for y in year_list]

    seq.store_result(
        name="ch4_prospective",
        value=ch4_per_years,
        unit="Gg/year",
        year=year_list,
    )
    logger.info("---> swd sequence finalized.")
    return seq.step


def tier3_ch4(
    year=2010,
    region="BG",
    wastetype="msw_food",
    wastemoisture="wet",
    past_years=0,
    landfilltype="uncharacterised",
    uncertainty="def",
):
    """Template calculation sequence for tier 3 method.

    CH4 Emissions in year y, due to waste deposed in past year y-n.
    Defines a sequence of steps.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    wastetype : str
        Fraction of solid waste.
    wastemoisture : str
        'wet' or 'dry'
        Specifies if waste amount is measured as dry-matter or wet.
    past_years : int
        number of past years to be considered for waste generation.
        good practice is 60 years.
    landfilltype : str
        Management of solid waste disposal side.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    logger.info("swd sequence started --->")
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    seq.store_signature(locals())

    value_list = []
    year_list = []

    for y in range(year - past_years, year + 1):
        seq.read_parameter(
            name="sw_per_tech",
            table="sw_per_tech_swd",
            coords=[year, region, wastetype, landfilltype],
        )

        value = seq.step.sw_per_tech.value

        value_list.append(value)
        year_list.append(y)

    seq.store_result(
        name="w_per_tech", value=value_list, unit="Gg/year", year=year_list
    )

    # 2: read parameters second function
    logger.info("for tier 3, parameter 'doc' requires country-specific data.")
    seq.read_parameter(
        name="doc", table="doc", coords=[region, wastetype, wastemoisture]
    )

    logger.info("for tier 3, parameter 'doc_f' requires country-specific data.")
    seq.read_parameter(name="doc_f", table="doc_f", coords=[region, wastetype])

    seq.read_parameter(name="mcf", table="mcf", coords=[landfilltype])

    value_list = []
    year_list = []
    for y in range(year - past_years, year + 1):
        value = seq.elementary.ddoc_from_wd_data(
            seq.step.w_per_tech.value[year - y],
            doc=seq.step.doc.value,
            doc_f=seq.step.doc_f.value,
            mcf=seq.step.mcf.value,
        )
        value_list.append(value)
        year_list.append(y)

    seq.store_result(
        name="ddoc_from_wd_data",
        value=value_list,
        unit="Gg/year",
        year=year_list,
    )

    # 3: read parameters third function
    seq.read_parameter(name="climate_zone", table="climate_zone", coords=[region])

    seq.read_parameter(name="moisture_regime", table="moisture_regime", coords=[region])

    seq.read_parameter(
        name="k",
        table="k",
        coords=[wastetype, seq.step.moisture_regime.value, seq.step.climate_zone.value],
    )

    value = 0
    value_list = []
    year_list = []
    for y in range(year - past_years, year + 1):
        value = seq.elementary.ddoc_ma_t(
            seq.step.ddoc_from_wd_data.value[year - y],
            value,
            seq.step.k.value,
        )
        value_list.append(value)
        year_list.append(y)

    seq.store_result(
        name="ddoc_ma_t",
        value=value_list,
        unit="Gg/year",
        year=year_list,
    )

    value = seq.elementary.ddoc_m_decomp_t(
        seq.step.ddoc_ma_t.value[-2],
        seq.step.k.value,  # -2, beacause value dpends on the accumalation in year before
    )
    seq.store_result(
        name="ddoc_m_decomp_t",
        value=value,
        unit="Gg/year",
        year=year,
    )

    # 4: read parameters forth function
    seq.read_parameter(name="f", table="f", coords=[])

    value = seq.elementary.ch4_generated(
        seq.step.ddoc_m_decomp_t.value, seq.step.f.value
    )

    seq.store_result(
        name="ch4_generated",
        value=value,
        unit="Gg/year",
        year=year,
    )

    # 5: read parameter for fith equation
    seq.read_parameter(name="ox", table="ox", coords=[landfilltype])

    seq.read_parameter(name="r", table="r_swd", coords=[year, region, landfilltype])

    value = seq.elementary.ch4_emissions(
        seq.step.ch4_generated.value, ox=seq.step.ox.value, r=seq.step.r.value
    )

    seq.store_result(
        name="ch4",
        value=value,
        unit="Gg/year",
        year=year,
    )
    logger.info("---> swd sequence finalized.")
    return seq.step


def tier3_ch4_prospective(
    year=2010,
    region="BG",
    wastetype="msw_food",
    wastemoisture="wet",
    landfilltype="uncharacterised",
    prospective_years=20,
    uncertainty="def",
):
    """Template calculation sequence for tier 3 method.

    CH4 Emissions in prospective years y+n, due to waste deposed in year y.
    Defines a sequence of steps.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    wastetype : str
        Fraction of solid waste.
    wastemoisture : str
        'wet' or 'dry'
        Specifies if waste amount is measured as dry-matter or wet.
    landfilltype : str
        Management of solid waste disposal side.
    prospective_years : int
        prospective years under study
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    logger.info("swd sequence started --->")
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    seq.store_signature(locals())

    seq.read_parameter(
        name="w_per_tech", table="sw_per_tech_swd", coords=[year, region, wastetype]
    )

    # 2: read parameters second function
    logger.info("for tier 3, parameter 'doc' requires country-specific data.")
    seq.read_parameter(
        name="doc", table="doc", coords=[region, wastetype, wastemoisture]
    )

    logger.info("for tier 3, parameter 'doc_f' requires country-specific data.")
    seq.read_parameter(name="doc_f", table="doc_f", coords=[region, wastetype])

    seq.read_parameter(name="mcf", table="mcf", coords=[landfilltype])

    value = seq.elementary.ddoc_from_wd_data(
        seq.step.w_per_tech.value,
        doc=seq.step.doc.value,
        doc_f=seq.step.doc_f.value,
        mcf=seq.step.mcf.value,
    )
    seq.store_result(
        name="ddoc_from_wd_data",
        value=value,
        unit="Gg/year",
        year=year,
    )

    # 3: read parameters third and forth and fith function
    seq.read_parameter(name="climate_zone", table="climate_zone", coords=[region])

    seq.read_parameter(name="moisture_regime", table="moisture_regime", coords=[region])

    seq.read_parameter(
        name="k",
        table="k",
        coords=[wastetype, seq.step.moisture_regime.value, seq.step.climate_zone.value],
    )

    seq.read_parameter(name="f", table="f", coords=[])

    seq.read_parameter(name="ox", table="ox", coords=[landfilltype])

    seq.read_parameter(name="r", table="r_swd", coords=[year, region, landfilltype])

    # loop
    ddoc_ma_t_1 = seq.step.ddoc_from_wd_data.value

    ch4_per_years = []
    year_list = []
    for y in list(range(prospective_years)):
        ddoc_m_decomp_t = seq.elementary.ddoc_m_decomp_t(ddoc_ma_t_1, seq.step.k.value)
        # 5: execute third equation and store results
        ch4_generated = seq.elementary.ch4_generated(ddoc_m_decomp_t, seq.step.f.value)
        # 7: execute forth equation and store results
        ch4_per_year = seq.elementary.ch4_emissions(
            ch4_generated, ox=seq.step.ox.value, r=seq.step.r.value
        )
        ch4_per_years.append(ch4_per_year)
        year_list.append(y + 1)
        ddoc_ma_t_1 -= ddoc_m_decomp_t

    year_list = [y + year for y in year_list]

    seq.store_result(
        name="ch4_prospective",
        value=ch4_per_years,
        unit="Gg/year",
        year=year_list,
    )
    logger.info("---> swd sequence finalized.")
    return seq.step
