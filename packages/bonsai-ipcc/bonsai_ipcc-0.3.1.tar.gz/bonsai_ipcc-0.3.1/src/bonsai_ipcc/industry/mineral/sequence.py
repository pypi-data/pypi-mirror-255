"""
Sequences to determine GHG emission"s from mineral industry.
"""

"""
As the PPF model for cement includes some additional equations not covered by the IPCC
guidelines, the "Sequence.py" file is located in the PPF repository and is calling the
IPCC equations from "elementary.py" in the IPCC repository when needed. Therefore this
file remains empty.
"""

import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def tier1_co2_cement(year=2010, region="BG", cement_type="portland", uncertainty="def"):
    """Template calculation sequence for tier 1 method.

    CO2 Emissions for cement production.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    cement_type : str
        type of cement
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Mineral sequence started --->")
    seq.store_signature(locals())

    #'cao_in_clinker, ckd_correc_fact'
    seq.read_parameter(
        name="cao_in_clinker", table="cao_in_clinker", coords=[year, region]
    )

    seq.read_parameter(
        name="ckd_correc_fact", table="ckd_correc_fact", coords=[year, region]
    )

    value = seq.elementary.ef_clc(
        cao_in_clinker=seq.step.cao_in_clinker.value,
        ckd_correc_fact=seq.step.ckd_correc_fact.value,
    )

    seq.store_result(name="ef_clc", value=value, unit="t/t", year=year)

    seq.read_parameter(name="m_c", table="m_c", coords=[year, region, cement_type])

    seq.read_parameter(name="c_cl", table="c_cl", coords=[year, region, cement_type])

    seq.read_parameter(name="im_cl", table="im_cl", coords=[year, region, cement_type])

    seq.read_parameter(name="ex_cl", table="ex_cl", coords=[year, region, cement_type])

    value = seq.elementary.co2_emissions_tier1_(
        m_c=seq.step.m_c.value,
        c_cl=seq.step.c_cl.value,
        im_cl=seq.step.im_cl.value,
        ex_cl=seq.step.ex_cl.value,
        ef_clc=seq.step.ef_clc.value,
    )

    seq.store_result(name="co2_emissions", value=value, unit="t/yr", year=year)

    logger.info("---> Mineral sequence finalized.")
    return seq.step


def tier2_co2_cement_simple(
    year=2010, region="BG", cement_type="portland", uncertainty="def"
):
    """Template calculation sequence for tier 2 method.

    CO2 Emissions for cement production.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    cement_type : str
        type of cement
    carbonate_type : str
        type of the origin carbonate
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Mineral sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(
        name="cao_in_clinker", table="cao_in_clinker", coords=[year, region]
    )

    seq.read_parameter(
        name="cao_non_carbo_frac",
        table="cao_non_carbo_frac",
        coords=[year, region, cement_type],
    )

    value = seq.elementary.ef_cl(
        cao_in_clinker=seq.step.cao_in_clinker.value,
        cao_non_carbo_frac=seq.step.cao_non_carbo_frac.value,
    )

    seq.store_result(name="ef_cl", value=value, unit="t/t", year=year)

    seq.read_parameter(  # also equation 2.5 possible, but more data required
        name="cf_ckd", table="ckd_correc_fact", coords=[year, region]
    )

    seq.read_parameter(name="m_cl", table="m_cl", coords=[year, region, cement_type])

    value = seq.elementary.co2_emissions_tier2_(
        m_cl=seq.step.m_cl.value,
        ef_cl=seq.step.ef_cl.value,
        cf_ckd=seq.step.cf_ckd.value,
    )

    seq.store_result(name="co2_emissions", value=value, unit="t/yr", year=year)

    # co2_per_cement_type_tier2(co2_emissions, cement_frac_region)
    seq.read_parameter(
        name="cement_frac_region",
        table="cement_frac_region",
        coords=[year, region, cement_type],
    )

    value = seq.elementary.co2_per_cement_type_tier2(
        co2_emissions=seq.step.co2_emissions.value,
        cement_frac_region=seq.step.cement_frac_region.value,
    )

    seq.store_result(
        name="co2_emissions_per_cement_type", value=value, unit="t/yr", year=year
    )

    logger.info("---> Mineral sequence finalized.")
    return seq.step


def tier2_co2_cement_extended(
    year=2010, region="BG", cement_type="portland", uncertainty="def"
):
    """Template calculation sequence for tier 2 method.

    CO2 Emissions for cement production.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    cement_type : str
        type of cement
    carbonate_type : str
        type of the origin carbonate
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Mineral sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(
        name="cao_in_clinker", table="cao_in_clinker", coords=[year, region]
    )

    seq.read_parameter(
        name="cao_non_carbo_frac",
        table="cao_non_carbo_frac",
        coords=[year, region, cement_type],
    )

    value = seq.elementary.ef_cl(
        cao_in_clinker=seq.step.cao_in_clinker.value,
        cao_non_carbo_frac=seq.step.cao_non_carbo_frac.value,
    )

    seq.store_result(name="ef_cl", value=value, unit="t/t", year=year)

    seq.read_parameter(name="m_cl", table="m_cl", coords=[year, region, cement_type])

    # loop (sum over all carbonate types)
    d = seq.get_inventory_levels(table="c_d", year=year, region=region)
    value = 0.0
    for i in range(len(list(d.values())[0])):
        carbonate_type = d["carbonate_type"][i]

        seq.read_parameter(
            name="m_d", table="m_d", coords=[year, region, cement_type, carbonate_type]
        )

        seq.read_parameter(
            name="c_d",
            table="c_d",
            coords=[year, region, cement_type, carbonate_type],
        )
        seq.read_parameter(
            name="f_d",
            table="f_d",
            coords=[year, region, cement_type, carbonate_type],
        )
        seq.read_parameter(
            name="ef_c",
            table="ef_c",
            coords=[year, region, carbonate_type],
        )
        value += seq.elementary.cf_ckd(
            m_d=seq.step.m_d.value,
            m_cl=seq.step.m_cl.value,
            c_d=seq.step.c_d.value,
            f_d=seq.step.f_d.value,
            ef_c=seq.step.ef_c.value,
            ef_cl=seq.step.ef_cl.value,
        )

    seq.store_result(name="cf_ckd", value=value, unit="t/t", year=year)

    seq.read_parameter(name="m_cl", table="m_cl", coords=[year, region, cement_type])

    value = seq.elementary.co2_emissions_tier2_(
        m_cl=seq.step.m_cl.value,
        ef_cl=seq.step.ef_cl.value,
        cf_ckd=seq.step.cf_ckd.value,
    )

    seq.store_result(name="co2_emissions", value=value, unit="t/yr", year=year)

    # co2_per_cement_type_tier2(co2_emissions, cement_frac_region)
    seq.read_parameter(
        name="cement_frac_region",
        table="cement_frac_region",
        coords=[year, region, cement_type],
    )

    value = seq.elementary.co2_per_cement_type_tier2(
        co2_emissions=seq.step.co2_emissions.value,
        cement_frac_region=seq.step.cement_frac_region.value,
    )

    seq.store_result(
        name="co2_emissions_per_cement_type", value=value, unit="t/yr", year=year
    )

    logger.info("---> Mineral sequence finalized.")
    return seq.step


def tier3_co2_cement(year=2010, region="BG", cement_type="portland", uncertainty="def"):
    """Template calculation sequence for tier 3 method.

    CO2 Emissions for cement production.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    cement_type : str
        type of cement
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Mineral sequence started --->")
    seq.store_signature(locals())

    # loop sum over all carbonates i and all other materials k
    carb = seq.get_inventory_levels(table="m_i", year=year, region=region)
    other = seq.get_inventory_levels(table="m_k", year=year, region=region)
    value = 0.0
    for i in range(len(list(carb.values())[0])):
        for k in range(len(list(other.values())[0])):
            carbonate_type = carb["carbonate_type"][i]
            other_material_type = other["other_material_type"][k]

            seq.read_parameter(
                name="m_d",
                table="m_d",
                coords=[year, region, cement_type, carbonate_type],
            )

            seq.read_parameter(
                name="ef_i", table="ef_c", coords=[year, region, carbonate_type]
            )

            seq.read_parameter(
                name="m_i",
                table="m_i",
                coords=[year, region, cement_type, carbonate_type],
            )

            seq.read_parameter(
                name="f_i",
                table="f_i",
                coords=[year, region, cement_type, carbonate_type],
            )

            seq.read_parameter(
                name="c_d",
                table="c_d",
                coords=[year, region, cement_type, carbonate_type],
            )

            seq.read_parameter(
                name="f_d",
                table="f_d",
                coords=[year, region, cement_type, carbonate_type],
            )

            seq.read_parameter(
                name="ef_d",
                table="ef_d",
                coords=[year, region, cement_type, carbonate_type],
            )

            seq.read_parameter(
                name="m_k",
                table="m_k",
                coords=[year, region, cement_type, other_material_type],
            )

            seq.read_parameter(
                name="x_k",
                table="x_k",
                coords=[year, region, cement_type, other_material_type],
            )

            seq.read_parameter(
                name="ef_k",
                table="ef_k",
                coords=[year, region, cement_type, other_material_type],
            )

            value += seq.elementary.co2_emissions_tier3_(
                ef_i=seq.step.ef_i.value,
                m_i=seq.step.m_i.value,
                f_i=seq.step.f_i.value,
                m_d=seq.step.m_d.value,
                c_d=seq.step.c_d.value,
                f_d=seq.step.f_d.value,
                ef_d=seq.step.ef_d.value,
                m_k=seq.step.m_k.value,
                x_k=seq.step.x_k.value,
                ef_k=seq.step.ef_k.value,
            )

    seq.store_result(name="co2_emissions", value=value, unit="t/yr", year=year)

    logger.info("---> Mineral sequence finalized.")
    return seq.step
