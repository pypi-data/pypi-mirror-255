import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def tier1a_co2_coke(
    year=2019, region="DE", cokeprocess_type="by-product_recovery", uncertainty="def"
):
    """Template calculation sequence for tier 1a method.

    CO2 Emissions for coke production.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    cokeprocess_type : str
        type of coke production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")
    seq.store_signature(locals())

    #'cao_in_clinker, ckd_correc_fact'
    seq.read_parameter(name="ck", table="ck", coords=[year, region, cokeprocess_type])

    seq.read_parameter(
        name="ef_co2", table="ef_co2_v3c4", coords=[year, region, cokeprocess_type]
    )

    value = seq.elementary.co2_coke_tier1a_(
        ck=seq.step.ck.value, ef_co2=seq.step.ef_co2.value
    )

    seq.store_result(name="co2_emission", value=value, unit="t/yr", year=year)

    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1a_ch4_coke(
    year=2019, region="DE", cokeprocess_type="by-product_recovery", uncertainty="def"
):
    """Template calculation sequence for tier 1a method.

    CH4 Emissions for coke production.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    cokeprocess_type : str
        type of coke production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(name="ck", table="ck", coords=[year, region, cokeprocess_type])

    seq.read_parameter(
        name="ef_ch4", table="ef_ch4_v3c4", coords=[year, region, cokeprocess_type]
    )

    value = seq.elementary.ch4_coke_tier1a_(
        ck=seq.step.ck.value, ef_ch4=seq.step.ef_ch4.value
    )

    seq.store_result(name="ch4_emission", value=value, unit="t/yr", year=year)

    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1b_co2_coke(
    year=2019, region="DE", cokeprocess_type="by-product_recovery", uncertainty="def"
):
    """Template calculation sequence for tier 1b method.

    CO2 Emissions for coke production.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    cokeprocess_type : str
        type of coke production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")
    seq.store_signature(locals())

    #'cao_in_clinker, ckd_correc_fact'
    seq.read_parameter(name="ck", table="ck", coords=[year, region, cokeprocess_type])

    seq.read_parameter(name="c_ck", table="c_ck", coords=[year, region])

    seq.read_parameter(name="cc", table="cc", coords=[year, region, cokeprocess_type])

    seq.read_parameter(name="c_cc", table="c_cc", coords=[year, region])

    value = seq.elementary.co2_coke_tier1b_(
        ck=seq.step.ck.value,
        cc=seq.step.cc.value,
        c_ck=seq.step.ck.value,
        c_cc=seq.step.cc.value,
    )

    seq.store_result(name="co2_emission", value=value, unit="t/yr", year=year)

    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier2_co2_coke(
    year=2019, region="DE", cokeprocess_type="by-product_recovery", uncertainty="def"
):
    """Template calculation sequence for tier 2 method.

    CO2 Emissions for coke production.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    cokeprocess_type : str
        type of coke production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(name="cc", table="cc", coords=[year, region, cokeprocess_type])
    seq.read_parameter(
        name="c_cc",
        table="c_cc",
        coords=[year, region],
    )
    seq.read_parameter(name="bg", table="bg", coords=[year, region, cokeprocess_type])
    seq.read_parameter(
        name="c_bg",
        table="c_bg",
        coords=[year, region],
    )

    seq.read_parameter(name="co", table="co", coords=[year, region, cokeprocess_type])
    seq.read_parameter(
        name="c_co",
        table="c_co",
        coords=[year, region],
    )
    seq.read_parameter(name="cog", table="cog", coords=[year, region, cokeprocess_type])
    seq.read_parameter(
        name="c_cog",
        table="c_cog",
        coords=[year, region],
    )
    seq.read_parameter(
        name="e_flaring", table="e_flaring", coords=[year, region, cokeprocess_type]
    )

    # loop (sum over all process materials)
    d = seq.get_inventory_levels(table="pm_a", year=year, region=region)
    d1 = seq.get_inventory_levels(table="cob_b", year=year, region=region)
    value = 0.0
    for a in range(len(list(d.values())[0])):
        for b in range(len(list(d.values())[0])):
            material_type = d["material_type"][a]
            byproduct_type = d1["byproduct_type"][b]

            seq.read_parameter(
                name="pm_a",
                table="pm_a",
                coords=[year, region, cokeprocess_type, material_type],
            )

            seq.read_parameter(
                name="c_a",
                table="c_a",
                coords=[year, region, material_type],
            )

            seq.read_parameter(
                name="cob_b",
                table="cob_b",
                coords=[year, region, cokeprocess_type, byproduct_type],
            )

            seq.read_parameter(
                name="c_b",
                table="c_b",
                coords=[year, region, byproduct_type],
            )

            value += seq.elementary.co2_coke_tier2_(
                cc=seq.step.cc.value,
                c_cc=seq.step.c_cc.value,
                pm_a=seq.step.pm_a.value,
                c_a=seq.step.c_a.value,
                bg=seq.step.bg.value,
                c_bg=seq.step.c_bg.value,
                co=seq.step.co.value,
                c_co=seq.step.c_co.value,
                cog=seq.step.cog.value,
                c_cog=seq.step.c_cog.value,
                cob_b=seq.step.cob_b.value,
                c_b=seq.step.c_b.value,
                e_flaring=seq.step.e_flaring.value,
            )

    seq.store_result(name="co2_emission", value=value, unit="t/yr", year=year)
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier3_co2_coke(
    year=2019,
    region="a specific plant",
    cokeprocess_type="by-product_recovery",
    uncertainty="def",
):
    """Template calculation sequence for tier 3 method. Plant-specific carbon content for materials and by-products required.

    CO2 Emissions for coke production.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    cokeprocess_type : str
        type of coke production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(name="cc", table="cc", coords=[year, region, cokeprocess_type])
    seq.read_parameter(
        name="c_cc",
        table="c_cc",
        coords=[year, region],
    )
    seq.read_parameter(name="bg", table="bg", coords=[year, region, cokeprocess_type])
    seq.read_parameter(
        name="c_bg",
        table="c_bg",
        coords=[year, region],
    )

    seq.read_parameter(name="co", table="co", coords=[year, region, cokeprocess_type])
    seq.read_parameter(
        name="c_co",
        table="c_co",
        coords=[year, region],
    )
    seq.read_parameter(name="cog", table="cog", coords=[year, region, cokeprocess_type])
    seq.read_parameter(
        name="c_cog",
        table="c_cog",
        coords=[year, region],
    )
    seq.read_parameter(
        name="e_flaring", table="e_flaring", coords=[year, region, cokeprocess_type]
    )

    # loop (sum over all process materials)
    d = seq.get_inventory_levels(table="pm_a", year=year, region=region)
    d1 = seq.get_inventory_levels(table="cob_b", year=year, region=region)
    value = 0.0
    for a in range(len(list(d.values())[0])):
        for b in range(len(list(d.values())[0])):
            material_type = d["material_type"][a]
            byproduct_type = d1["byproduct_type"][b]

            seq.read_parameter(
                name="pm_a",
                table="pm_a",
                coords=[year, region, cokeprocess_type, material_type],
            )

            seq.read_parameter(
                name="c_a",
                table="c_a",
                coords=[year, region, material_type],
            )

            seq.read_parameter(
                name="cob_b",
                table="cob_b",
                coords=[year, region, cokeprocess_type, byproduct_type],
            )

            seq.read_parameter(
                name="c_b",
                table="c_b",
                coords=[year, region, byproduct_type],
            )

            value += seq.elementary.co2_coke_tier2_(
                cc=seq.step.cc.value,
                c_cc=seq.step.c_cc.value,
                pm_a=seq.step.pm_a.value,
                c_a=seq.step.c_a.value,
                bg=seq.step.bg.value,
                c_bg=seq.step.c_bg.value,
                co=seq.step.co.value,
                c_co=seq.step.c_co.value,
                cog=seq.step.cog.value,
                c_cog=seq.step.c_cog.value,
                cob_b=seq.step.cob_b.value,
                c_b=seq.step.c_b.value,
                e_flaring=seq.step.e_flaring.value,
            )

    seq.store_result(name="co2_emission", value=value, unit="t/yr", year=year)
    logger.info("---> Metal sequence finalized.")
    return seq.step
