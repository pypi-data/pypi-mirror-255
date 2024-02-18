"""
Sequences to determine GHG emissions from biogenic treatment.

Decision tree for CH4 and N2O:
    - tier 1: estimate total amount of wastes biogenic treated and use default emission factors
              (requirement: incineration or open burning is not a key category)
    - tier 2: country-specific emission factors
    - tier 3: plant- or site-specific emission factors
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
    wastetype="msw_metal",
    wastemoisture="wet",
    biotreattype="compost",
    uncertainty="def",
):
    """Tier 1 method CH4 Emissions.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    wastetype : str
        Fraction of solid waste.
    wastemoisture : str
        'dry' for dry-matter, 'wet' for wet-matter.
    biotreattype : str
        biological treatment technology
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Biogenic-treat sequence started --->")
    seq.store_signature(locals())
    # 1: read parameters first function

    if wastetype.startswith("msw_"):
        # 1: read parameters first function
        seq.read_parameter(
            name="urb_population", table="urb_population", coords=[year, region]
        )

        seq.read_parameter(
            name="msw_gen_rate", table="msw_gen_rate", coords=[year, region]
        )

        seq.read_parameter(
            name="msw_frac_to_biotreat",
            table="msw_frac_to_biotreat",
            coords=[year, region, biotreattype],
        )

        seq.read_parameter(
            name="msw_type_frac_bio",
            table="msw_type_frac_bio",
            coords=[year, region, wastetype],
        )

        value = (
            seq.elementary.msw_to_biotreat(
                urb_population=seq.step.urb_population.value,
                msw_gen_rate=seq.step.msw_gen_rate.value,
                msw_frac_to_biotreat=seq.step.msw_frac_to_biotreat.value,
                msw_type_frac_bio=seq.step.msw_type_frac_bio.value,
            )
            / 1000
        )  # conversion from tonnes to Gg

        seq.store_result(
            name="sw_per_tech",
            value=value,
            unit="Gg/year",
            year=year,
        )

    else:
        #    seq.read_parameter(name="SW", table="SW", coords=[year, region, wastetype]) # for tier 2a!
        seq.read_parameter(name="gdp", table="gdp", coords=[year, region])

        seq.read_parameter(
            name="isw_gen_rate", table="isw_gen_rate", coords=[year, region]
        )

        value = seq.elementary.isw_total(
            gdp=seq.step.gdp.value, waste_gen_rate=seq.step.isw_gen_rate.value
        )
        seq.store_result(name="sw", value=value, unit="gg/year", year=year)

        seq.read_parameter(
            name="isw_frac_to_biotreat",
            table="isw_frac_to_biotreat",
            coords=[year, region, biotreattype],
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.sw.value, treatmentrate=seq.step.isw_frac_to_biotreat.value
        )
        seq.store_result(name="sw_per_tech", value=value, unit="Gg/year", year=year)

    seq.read_parameter(
        name="ef_ch4_biotreat",
        table="ef_ch4_biotreat",
        coords=[year, region, biotreattype, wastemoisture],
    )

    seq.read_parameter(name="r_bt", table="r_bt", coords=[year, region, biotreattype])

    value = seq.elementary.ch4_emissions(
        m=seq.step.sw_per_tech.value,
        ef_ch4_biotr=seq.step.ef_ch4_biotreat.value,
        r_bt=seq.step.r_bt.value,
    )

    seq.store_result(
        name="ch4_emissions",
        value=value,
        unit="Gg/year",
        year=year,
    )
    logger.info("---> Biogenic-treat sequence finalized.")
    return seq.step


def tier1_n2o(
    year=2010,
    region="BG",
    wastetype="msw_metal",
    wastemoisture="wet",
    biotreattype="compost",
    uncertainty="def",
):
    """Tier 1 method N2O Emissions.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    wastetype : str
        Fraction of solid waste.
    wastemoisture : str
        'dry' for dry-matter, 'wet' for wet-matter.
    biotreattype : str
        biological treatment technology
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Biogenic-treat sequence started --->")
    seq.store_signature(locals())
    # 1: read parameters first function

    if wastetype.startswith("msw_"):
        # 1: read parameters first function
        seq.read_parameter(
            name="urb_population", table="urb_population", coords=[year, region]
        )

        seq.read_parameter(
            name="msw_gen_rate", table="msw_gen_rate", coords=[year, region]
        )

        seq.read_parameter(
            name="msw_frac_to_biotreat",
            table="msw_frac_to_biotreat",
            coords=[year, region, biotreattype],
        )

        seq.read_parameter(
            name="msw_type_frac_bio",
            table="msw_type_frac_bio",
            coords=[year, region, wastetype],
        )

        value = (
            seq.elementary.msw_to_biotreat(
                urb_population=seq.step.urb_population.value,
                msw_gen_rate=seq.step.msw_gen_rate.value,
                msw_frac_to_biotreat=seq.step.msw_frac_to_biotreat.value,
                msw_type_frac_bio=seq.step.msw_type_frac_bio.value,
            )
            / 1000
        )  # conversion from tonnes to gg

        seq.store_result(
            name="sw_per_tech",
            value=value,
            unit="Gg/year",
            year=year,
        )

    else:
        #    seq.read_parameter(name="sw", table="sw", coords=[year, region, wastetype]) # for tier 2a!
        seq.read_parameter(name="gdp", table="gdp", coords=[year, region])

        seq.read_parameter(
            name="isw_gen_rate", table="isw_gen_rate", coords=[year, region]
        )

        value = seq.elementary.isw_total(
            gdp=seq.step.gdp.value, waste_gen_rate=seq.step.isw_gen_rate.value
        )
        seq.store_result(name="sw", value=value, unit="Gg/year", year=year)

        seq.read_parameter(
            name="isw_frac_to_biotreat",
            table="isw_frac_to_biotreat",
            coords=[year, region, biotreattype],
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.sw.value, treatmentrate=seq.step.isw_frac_to_biotreat.value
        )
        seq.store_result(name="sw_per_tech", value=value, unit="Gg/year", year=year)

    seq.read_parameter(
        name="ef_n2o_biotreat",
        table="ef_n2o_biotreat",
        coords=[year, region, biotreattype, wastemoisture],
    )

    value = seq.elementary.n2o_emissions(
        m=seq.step.sw_per_tech.value,
        ef_n2o_biotr=seq.step.ef_n2o_biotreat.value,
    )

    seq.store_result(
        name="n2o_emissions",
        value=value,
        unit="Gg/year",
        year=year,
    )
    logger.info("---> Biogenic-treat sequence finalized.")
    return seq.step


def tier2_ch4(
    year=2010,
    region="BG",
    wastetype="msw_metal",
    wastemoisture="wet",
    biotreattype="compost",
    uncertainty="def",
):
    """Tier 2 method CH4 Emissions.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    wastetype : str
        Fraction of solid waste.
    wastemoisture : str
        'dry' for dry-matter, 'wet' for wet-matter.
    biotreattype : str
        biological treatment technology
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Biogenic-treat sequence started --->")
    seq.store_signature(locals())
    # 1: read parameters first function

    seq.read_parameter(
        name="sw_per_tech",
        table="sw_per_tech_bio",
        coords=[year, region, wastetype, biotreattype],
    )

    logger.info(
        "for tier 2, emission factor ef_ch4 requieres country-specific information representative for each technology."
    )
    seq.read_parameter(
        name="ef_ch4_biotreat",
        table="ef_ch4_biotreat",
        coords=[year, region, biotreattype, wastemoisture],
    )

    seq.read_parameter(name="r_bt", table="r_bt", coords=[year, region, biotreattype])

    value = seq.elementary.ch4_emissions(
        m=seq.step.sw_per_tech.value,
        ef_ch4_biotr=seq.step.ef_ch4_biotreat.value,
        r_bt=seq.step.r_bt.value,
    )

    seq.store_result(
        name="ch4_emissions",
        value=value,
        unit="Gg/year",
        year=year,
    )
    logger.info("---> Biogenic-treat sequence finalized.")
    return seq.step


def tier2_n2o(
    year=2010,
    region="BG",
    wastetype="msw_metal",
    wastemoisture="wet",
    biotreattype="compost",
    uncertainty="def",
):
    """Tier 2 method N2O Emissions.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    wastetype : str
        Fraction of solid waste.
    wastemoisture : str
        'dry' for dry-matter, 'wet' for wet-matter.
    biotreattype : str
        biological treatment technology
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Biogenic-treat sequence started --->")
    seq.store_signature(locals())
    # 1: read parameters first function

    seq.read_parameter(
        name="sw_per_tech",
        table="sw_per_tech_bio",
        coords=[year, region, wastetype, biotreattype],
    )

    logger.info(
        "for tier 2, emission factor ef_n2o requieres country-specific information representative for each technology."
    )
    seq.read_parameter(
        name="ef_n2o_biotreat",
        table="ef_n2o_biotreat",
        coords=[year, region, biotreattype, wastemoisture],
    )

    value = seq.elementary.n2o_emissions(
        m=seq.step.sw_per_tech.value,
        ef_n2o_biotr=seq.step.ef_n2o_biotreat.value,
    )

    seq.store_result(
        name="n2o_emissions",
        value=value,
        unit="Gg/year",
        year=year,
    )
    logger.info("---> Biogenic-treat sequence finalized.")
    return seq.step


def tier3_ch4(
    year=2010,
    region="BG",
    wastetype="msw_metal",
    wastemoisture="wet",
    biotreattype="compost",
    uncertainty="def",
):
    """Tier 3 method CH4 Emissions.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    wastetype : str
        Fraction of solid waste.
    wastemoisture : str
        'dry' for dry-matter, 'wet' for wet-matter.
    biotreattype : str
        biological treatment technology
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Biogenic-treat sequence started --->")
    seq.store_signature(locals())
    # 1: read parameters first function

    logger.info("For tier 3, waste data requieres plant-specific information.")
    seq.read_parameter(
        name="sw_per_tech",
        table="sw_per_tech_bio",
        coords=[year, region, wastetype, biotreattype],
    )

    logger.info(
        "for tier 3, emission factor ef_ch4 requieres plant-specific information."
    )
    seq.read_parameter(
        name="ef_ch4_biotreat",
        table="ef_ch4_biotreat",
        coords=[year, region, biotreattype, wastemoisture],
    )

    seq.read_parameter(name="r_bt", table="r_bt", coords=[year, region, biotreattype])

    value = seq.elementary.ch4_emissions(
        m=seq.step.sw_per_tech.value,
        ef_ch4_biotr=seq.step.ef_ch4_biotreat.value,
        r_bt=seq.step.r_bt.value,
    )

    seq.store_result(
        name="ch4_emissions",
        value=value,
        unit="Gg/year",
        year=year,
    )
    logger.info("---> Biogenic-treat sequence finalized.")
    return seq.step


def tier3_n2o(
    year=2010,
    region="BG",
    wastetype="msw_metal",
    wastemoisture="wet",
    biotreattype="compost",
    uncertainty="def",
):
    """Tier 3 method N2O Emissions.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    wastetype : str
        Fraction of solid waste.
    wastemoisture : str
        'dry' for dry-matter, 'wet' for wet-matter.
    biotreattype : str
        biological treatment technology
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Biogenic-treat sequence started --->")
    seq.store_signature(locals())
    # 1: read parameters first function

    logger.info("For tier 3, waste data requieres plant-specific information.")
    seq.read_parameter(
        name="sw_per_tech",
        table="sw_per_tech_bio",
        coords=[year, region, wastetype, biotreattype],
    )

    logger.info(
        "for tier 3, emission factor ef_n2o requieres plant-specific information."
    )
    seq.read_parameter(
        name="ef_n2o_biotreat",
        table="ef_n2o_biotreat",
        coords=[year, region, biotreattype, wastemoisture],
    )

    value = seq.elementary.n2o_emissions(
        m=seq.step.sw_per_tech.value,
        ef_n2o_biotr=seq.step.ef_n2o_biotreat.value,
    )

    seq.store_result(
        name="n2o_emissions",
        value=value,
        unit="Gg/year",
        year=year,
    )
    logger.info("---> Biogenic-treat sequence finalized.")
    return seq.step
