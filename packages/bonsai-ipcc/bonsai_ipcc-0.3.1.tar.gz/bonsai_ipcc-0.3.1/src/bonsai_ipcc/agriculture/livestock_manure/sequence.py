"""
Sequences to determine GHG emissions from manure treatment.


"""


import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def tier1_n2o(
    year=2010,
    region="NZ",
    species_type="cattle-dairy",
    manuretreat_type="lagoon",
    uncertainty="def",
):
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("livestock-manure-treat sequence started --->")
    seq.store_signature(locals())

    # nex:

    seq.read_parameter(
        name="tam",
        table="weight",
        coords=[year, region, species_type],
    )

    seq.read_parameter(
        name="n_rate",
        table="n_rate",
        coords=[year, region, species_type],
    )

    value = seq.elementary.nex_tier1_(
        n_rate=seq.step.n_rate.value,
        tam=seq.step.tam.value,
    )

    seq.store_result(
        name="nex",
        value=value,
        unit="kg/piece/year",
        year=year,
    )

    # n2o_direct_mm:

    seq.read_parameter(
        name="n",
        table="n",
        coords=[year, region, species_type],
    )

    seq.read_parameter(
        name="ms",
        table="ms",
        coords=[year, region, species_type, manuretreat_type],
    )

    seq.read_parameter(
        name="ef",
        table="ef3",
        coords=[manuretreat_type],
    )

    value = seq.elementary.n2o_direct_mm(
        n=seq.step.n.value,
        nex=seq.step.nex.value,
        ms=seq.step.ms.value,
        ef=seq.step.ef.value,
    )

    seq.store_result(
        name="n2o_direct",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="frac_gas",
        table="frac_gas",
        coords=[year, region, species_type, manuretreat_type],
    )
    value = seq.elementary.n_volatilization(
        n=seq.step.n.value,
        nex=seq.step.nex.value,
        awms=seq.step.ms.value,
        frac_gas=seq.step.frac_gas.value,
    )
    seq.store_result(
        name="n_volatilization",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="frac_leach",
        table="frac_leach",
        coords=[year, region, species_type, manuretreat_type],
    )
    value = seq.elementary.n_leaching(
        n=seq.step.n.value,
        nex=seq.step.nex.value,
        awms=seq.step.ms.value,
        frac_leach=seq.step.frac_leach.value,
    )
    seq.store_result(
        name="n_leaching",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(name="moisture_regime", table="moisture_regime", coords=[region])

    seq.read_parameter(
        name="ef4",
        table="ef4",
        coords=[seq.step.moisture_regime.value],
    )
    value = seq.elementary.n2o_g(
        n_volatilization=seq.step.n_volatilization.value,
        ef4=seq.step.ef4.value,
    )
    seq.store_result(
        name="n2o_volatilization",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="ef5",
        table="ef5",
        coords=[],
    )
    value = seq.elementary.n2o_l(
        n_leaching=seq.step.n_leaching.value,
        ef5=seq.step.ef5.value,
    )
    seq.store_result(
        name="n2o_leaching",
        value=value,
        unit="kg/year",
        year=year,
    )

    logger.info("---> livestock-manure-treat sequence finalized.")
    return seq.step


def tier2_n2o(
    year=2019,
    region="DE",
    species_type="cattle-dairy",
    feeding_situation="stall",
    diet_type="forage-high",
    manuretreat_type="solid-storage",
    uncertainty="def",
):
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("livestock-manure-treat sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(name="cf_i", table="cf_i", coords=[species_type])

    seq.read_parameter(
        name="weight", table="weight", coords=[year, region, species_type]
    )

    value = seq.elementary.ne_m(cf_i=seq.step.cf_i.value, weight=seq.step.weight.value)

    seq.store_result(
        name="ne_m",
        value=value,
        unit="MJ/piece/day",
        year=year,
    )

    if species_type.startswith(("cattle", "buffalo", "sheep", "goat")):
        if species_type.startswith(("cattle", "buffalo")):
            seq.read_parameter(
                name="c_a", table="c_a_cattle", coords=[feeding_situation]
            )

            value = seq.elementary.nea_cattle_(
                c_a=seq.step.c_a.value, ne_m=seq.step.ne_m.value
            )
            seq.store_result(
                name="ne_a",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="bw", table="weight", coords=[year, region, species_type]
            )

            seq.read_parameter(name="c", table="c", coords=[species_type])

            seq.read_parameter(
                name="mw", table="mw", coords=[year, region, species_type]
            )

            seq.read_parameter(
                name="wg", table="wg", coords=[year, region, species_type]
            )

            value = seq.elementary.neg_cattle_(
                bw=seq.step.bw.value,
                c=seq.step.c.value,
                mw=seq.step.mw.value,
                wg=seq.step.wg.value,
            )
            seq.store_result(
                name="ne_g",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="milk", table="milk", coords=[year, region, species_type]
            )

            seq.read_parameter(
                name="fat", table="fat", coords=[year, region, species_type]
            )

            value = seq.elementary.nel_cattle_(
                milk=seq.step.milk.value, fat=seq.step.fat.value
            )
            seq.store_result(
                name="ne_l",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="workhours", table="workhours", coords=[year, region, species_type]
            )

            value = seq.elementary.ne_work(
                ne_m=seq.step.ne_m.value, hours=seq.step.workhours.value
            )
            seq.store_result(
                name="ne_work",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="c_pregnancy", table="c_pregnancy", coords=[species_type]
            )

            seq.read_parameter(
                name="ratio_preg",
                table="ratio_preg",
                coords=[year, region, species_type],
            )

            value = seq.elementary.ne_p(
                ne_m=seq.step.ne_m.value,
                c_pregnancy=seq.step.c_pregnancy.value,
                ratio_preg=seq.step.ratio_preg.value,
            )
            seq.store_result(
                name="ne_p",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="de", table="de", coords=[year, region, species_type]
            )
            value = seq.elementary.rem(de=seq.step.de.value)
            seq.store_result(
                name="rem",
                value=value,
                unit="MJ/MJ",
                year=year,
            )

            value = seq.elementary.reg(de=seq.step.de.value)
            seq.store_result(
                name="reg",
                value=value,
                unit="MJ/MJ",
                year=year,
            )

            if "cattle" in species_type and "calve" in species_type:
                seq.read_parameter(
                    name="ne_mf", table="ne_mf", coords=[year, region, diet_type]
                )

                value = seq.elementary.dmi_calve_(
                    ne_mf=seq.step.ne_mf.value, bw=seq.step.bw.value
                )
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            elif "cattle" in species_type and "growing" in species_type:
                seq.read_parameter(
                    name="ne_mf", table="ne_mf", coords=[year, region, diet_type]
                )

                value = seq.elementary.dmi_growing_(
                    ne_mf=seq.step.ne_mf.value, bw=seq.step.bw.value
                )
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            elif "cattle" in species_type and "bull" in species_type:

                value = seq.elementary.dmi_steer_(bw=seq.step.bw.value)
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(name="ge", value=value, unit="mj/piece/day", year=year)
            elif "cattle" in species_type and "heifer" in species_type:
                value = seq.elementary.dmi_heifer_(bw=seq.step.bw.value)
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            elif "cattle" in species_type and "dairy" in species_type:
                value = seq.elementary.fcm(
                    milk=seq.step.milk.value, fat=seq.step.fat.value
                )
                seq.store_result(
                    name="fcm",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )

                value = seq.elementary.dmi_lactating_(
                    bw=seq.step.bw.value, fcm=seq.step.fcm.value
                )
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            else:
                value = seq.elementary.ge_cattletier2_(
                    ne_m=seq.step.ne_m.value,
                    ne_a=seq.step.ne_a.value,
                    ne_l=seq.step.ne_l.value,
                    ne_p=seq.step.ne_p.value,
                    ne_work=seq.step.ne_work.value,
                    ne_g=seq.step.ne_g.value,
                    reg=seq.step.reg.value,
                    rem=seq.step.rem.value,
                    de=seq.step.de.value,
                )
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )

        seq.read_parameter(name="cp", table="cp", coords=[year, region, species_type])

        value = seq.elementary.nintake_cattletier2_(
            ge=seq.step.ge.value, cp=seq.step.cp.value
        )
        seq.store_result(
            name="n_intake",
            value=value,
            unit="kg/piece/day",
            year=year,
        )

        # TODO: use equations n_retention instead of parameter n_retention_frac?
        seq.read_parameter(
            name="n_retention_frac",
            table="n_retention_frac",
            coords=[year, region, species_type],
        )

        value = seq.elementary.nex_atier2_(
            n_intake=seq.step.n_intake.value,
            n_retention_frac=seq.step.n_retention_frac.value,
        )
        seq.store_result(
            name="nex",
            value=value,
            unit="kg/piece/year",
            year=year,
        )

        seq.read_parameter(name="n", table="n", coords=[year, region, species_type])
        seq.read_parameter(
            name="ms", table="ms", coords=[year, region, species_type, manuretreat_type]
        )
        seq.read_parameter(name="ef", table="ef3", coords=[manuretreat_type])
        value = seq.elementary.n2o_direct_mm(
            n=seq.step.n.value,
            nex=seq.step.nex.value,
            ms=seq.step.ms.value,
            ef=seq.step.ef.value,
        )
        seq.store_result(
            name="n2o_direct",
            value=value,
            unit="kg/year",
            year=year,
        )

    elif species_type.startswith(("sheep", "goat")):
        seq.read_parameter(name="c_a", table="c_a_sheep")

        value = seq.elementary.nea_sheep_(
            c_a=seq.step.c_a.value, weight=seq.step.weight.value
        )
        seq.store_result(
            name="ne_a",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(
            name="bw_i", table="bw_i", coords=[year, region, species_type]
        )

        seq.read_parameter(
            name="bw_f", table="bw_f", coords=[year, region, species_type]
        )

        seq.read_parameter(name="a", table="a", coords=[species_type])

        seq.read_parameter(name="b", table="b", coords=[species_type])

        value = seq.elementary.neg_sheep_(
            bw_f=seq.step.bw_f.value,
            bw_i=seq.step.bw_i.value,
            a=seq.step.a.value,
            b=seq.step.b.value,
        )
        seq.store_result(
            name="ne_g",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        # eq 10.9 or 10.10
        seq.read_parameter(
            name="milk", table="milk", coords=[year, region, species_type]
        )

        seq.read_parameter(
            name="ev_milk", table="ev_milk", coords=[year, region, species_type]
        )

        value = seq.elementary.nel_asheep_(
            milk=seq.step.milk.value, ev_milk=seq.step.ev_milk.value
        )
        seq.store_result(
            name="ne_l",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )
        # 10.10
        # seq.read_parameter(
        #    name="WG_mean", table="WG_mean", coords=[year, region, species_type]
        # )
        # seq.read_parameter(
        #    name="EV_milk", table="EV_milk", coords=[year, region, species_type]
        # )
        # value = seq.elementary.nel_bsheep_(
        #    W=seq.step.MILK.value, EV_milk=seq.step.EV_milk.value
        # )
        # seq.store_result(
        #    name="NE_L",
        #    value=value,
        #    unit="MJ/piece/day",
        #    year=year,
        # )
        seq.read_parameter(
            name="ev_wool", table="ev_wool", coords=[year, region, species_type]
        )
        seq.read_parameter(
            name="pr_wool", table="pr_wool", coords=[year, region, species_type]
        )

        value = seq.elementary.ne_wool(
            ev_wool=seq.step.ev_wool.value, pr_wool=seq.step.pr_wool.value
        )
        seq.store_result(
            name="ne_wool",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(
            name="c_pregnancy", table="c_pregnancy", coords=[species_type]
        )

        seq.read_parameter(
            name="ratio_preg",
            table="ratio_preg",
            coords=[year, region, species_type],
        )
        value = seq.elementary.ne_p(
            ne_m=seq.step.ne_m.value,
            c_pregnancy=seq.step.c_pregnancy.value,
            ratio_preg=seq.step.ratio_preg.value,
        )
        seq.store_result(
            name="ne_p",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="de", table="de", coords=[year, region, species_type])
        value = seq.elementary.rem(de=seq.step.de.value)
        seq.store_result(
            name="rem",
            value=value,
            unit="MJ/MJ",
            year=year,
        )
        value = seq.elementary.reg(de=seq.step.de.value)
        seq.store_result(
            name="reg",
            value=value,
            unit="MJ/MJ",
            year=year,
        )

        value = seq.elementary.ge_sheeptier2_(
            ne_m=seq.step.ne_m.value,
            ne_a=seq.step.ne_a.value,
            ne_l=seq.step.ne_l.value,
            ne_p=seq.step.ne_p.value,
            ne_wool=seq.step.ne_wool.value,
            ne_g=seq.step.ne_g.value,
            reg=seq.step.reg.value,
            rem=seq.step.rem.value,
            de=seq.step.de.value,
        )
        seq.store_result(
            name="ge",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="cp", table="cp", coords=[year, region, species_type])

        value = seq.elementary.nintake_cattletier2_(
            ge=seq.step.ge.value, cp=seq.step.cp.value
        )
        seq.store_result(
            name="n_intake",
            value=value,
            unit="kg/piece/day",
            year=year,
        )

        seq.read_parameter(
            name="n_retention_frac",
            table="n_retention_frac",
            coords=[year, region, species_type],
        )

        value = seq.elementary.nex_atier2_(
            n_intake=seq.step.n_intake.value,
            n_retention_frac=seq.step.n_retention_frac.value,
        )
        seq.store_result(
            name="nex",
            value=value,
            unit="kg/piece/year",
            year=year,
        )

        seq.read_parameter(name="n", table="n", coords=[year, region, species_type])
        seq.read_parameter(
            name="ms", table="ms", coords=[year, region, species_type, manuretreat_type]
        )
        seq.read_parameter(name="ef", table="ef3", coords=[manuretreat_type])
        value = seq.elementary.n2o_direct_mm(
            n=seq.step.n.value,
            nex=seq.step.nex.value,
            ms=seq.step.ms.value,
            ef=seq.step.ef.value,
        )
        seq.store_result(
            name="n2o_direct",
            value=value,
            unit="kg/year",
            year=year,
        )

    seq.read_parameter(
        name="frac_gas",
        table="frac_gas",
        coords=[year, region, species_type, manuretreat_type],
    )
    value = seq.elementary.n_volatilization(
        n=seq.step.n.value,
        nex=seq.step.nex.value,
        awms=seq.step.ms.value,
        frac_gas=seq.step.frac_gas.value,
    )
    seq.store_result(
        name="n_volatilization",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="frac_leach",
        table="frac_leach",
        coords=[year, region, species_type, manuretreat_type],
    )
    value = seq.elementary.n_leaching(
        n=seq.step.n.value,
        nex=seq.step.nex.value,
        awms=seq.step.ms.value,
        frac_leach=seq.step.frac_leach.value,
    )
    seq.store_result(
        name="n_leaching",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(name="moisture_regime", table="moisture_regime", coords=[region])

    seq.read_parameter(
        name="ef4",
        table="ef4",
        coords=[seq.step.moisture_regime.value],
    )
    value = seq.elementary.n2o_g(
        n_volatilization=seq.step.n_volatilization.value,
        ef4=seq.step.ef4.value,
    )
    seq.store_result(
        name="n2o_volatilization",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="ef5",
        table="ef5",
        coords=[],
    )
    value = seq.elementary.n2o_l(
        n_leaching=seq.step.n_leaching.value,
        ef5=seq.step.ef5.value,
    )
    seq.store_result(
        name="n2o_leaching",
        value=value,
        unit="kg/year",
        year=year,
    )

    logger.info("---> livestock-manure-treat sequence finalized.")
    return seq.step


def tier1_ch4_enteric(
    year=2010,
    region="DE",
    species_type="cattle-dairy",
    uncertainty="def",
):
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("livestock-manure-treat sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(
        name="ef",
        table="ef",
        coords=[year, region, species_type],
    )
    seq.read_parameter(
        name="n",
        table="n",
        coords=[year, region, species_type],
    )
    value = seq.elementary.e(
        n=seq.step.n.value,
        ef=seq.step.ef.value,
    )
    seq.store_result(
        name="ch4",
        value=value,
        unit="Gg/year",
        year=year,
    )
    logger.info("---> livestock-manure-treat sequence finalized.")
    return seq.step


def tier2_ch4_enteric(
    year=2010,
    region="DE",
    species_type="cattle-dairy",
    feeding_situation="stall",
    diet_type="undefined",
    uncertainty="def",
):
    """
    diet_type : str
        optional, required for growing cattle and calve
    feeding_situation : str
        optional, required for cattle and buffalo
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("livestock-manure-treat sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(name="cf_i", table="cf_i", coords=[species_type])

    seq.read_parameter(
        name="weight", table="weight", coords=[year, region, species_type]
    )

    value = seq.elementary.ne_m(cf_i=seq.step.cf_i.value, weight=seq.step.weight.value)

    seq.store_result(
        name="ne_m",
        value=value,
        unit="MJ/piece/day",
        year=year,
    )

    if species_type.startswith(("cattle", "buffalo", "sheep", "goat")):
        if species_type.startswith(("cattle", "buffalo")):
            seq.read_parameter(
                name="c_a", table="c_a_cattle", coords=[feeding_situation]
            )

            value = seq.elementary.nea_cattle_(
                c_a=seq.step.c_a.value, ne_m=seq.step.ne_m.value
            )
            seq.store_result(
                name="ne_a",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="bw", table="weight", coords=[year, region, species_type]
            )

            seq.read_parameter(name="c", table="c", coords=[species_type])
            logger.info("mw")
            seq.read_parameter(
                name="mw", table="mw", coords=[year, region, species_type]
            )

            seq.read_parameter(
                name="wg", table="wg", coords=[year, region, species_type]
            )

            value = seq.elementary.neg_cattle_(
                bw=seq.step.bw.value,
                c=seq.step.c.value,
                mw=seq.step.mw.value,
                wg=seq.step.wg.value,
            )
            seq.store_result(
                name="ne_g",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="milk", table="milk", coords=[year, region, species_type]
            )

            seq.read_parameter(
                name="fat", table="fat", coords=[year, region, species_type]
            )

            value = seq.elementary.nel_cattle_(
                milk=seq.step.milk.value, fat=seq.step.fat.value
            )
            seq.store_result(
                name="ne_l",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="workhours", table="workhours", coords=[year, region, species_type]
            )

            value = seq.elementary.ne_work(
                ne_m=seq.step.ne_m.value, hours=seq.step.workhours.value
            )
            seq.store_result(
                name="ne_work",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="c_pregnancy", table="c_pregnancy", coords=[species_type]
            )

            seq.read_parameter(
                name="ratio_preg",
                table="ratio_preg",
                coords=[year, region, species_type],
            )

            value = seq.elementary.ne_p(
                ne_m=seq.step.ne_m.value,
                c_pregnancy=seq.step.c_pregnancy.value,
                ratio_preg=seq.step.ratio_preg.value,
            )
            seq.store_result(
                name="ne_p",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="de", table="de", coords=[year, region, species_type]
            )
            value = seq.elementary.rem(de=seq.step.de.value)
            seq.store_result(
                name="rem",
                value=value,
                unit="MJ/MJ",
                year=year,
            )

            value = seq.elementary.reg(de=seq.step.de.value)
            seq.store_result(
                name="reg",
                value=value,
                unit="MJ/MJ",
                year=year,
            )

            if "cattle" in species_type and "calve" in species_type:
                seq.read_parameter(
                    name="ne_mf", table="ne_mf", coords=[year, region, diet_type]
                )

                value = seq.elementary.dmi_calve_(
                    ne_mf=seq.step.ne_mf.value, bw=seq.step.bw.value
                )
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            elif "cattle" in species_type and "growing" in species_type:
                seq.read_parameter(
                    name="ne_mf", table="ne_mf", coords=[year, region, diet_type]
                )

                value = seq.elementary.dmi_growing_(
                    ne_mf=seq.step.ne_mf.value, bw=seq.step.bw.value
                )
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            elif "cattle" in species_type and "bull" in species_type:

                value = seq.elementary.dmi_steer_(bw=seq.step.bw.value)
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(name="ge", value=value, unit="MJ/piece/day", year=year)
            elif "cattle" in species_type and "heifer" in species_type:
                value = seq.elementary.dmi_heifer_(bw=seq.step.bw.value)
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            elif "cattle" in species_type and "dairy" in species_type:
                value = seq.elementary.fcm(
                    milk=seq.step.milk.value, fat=seq.step.fat.value
                )
                seq.store_result(
                    name="fcm",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )

                value = seq.elementary.dmi_lactating_(
                    bw=seq.step.bw.value, fcm=seq.step.fcm.value
                )
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            else:
                value = seq.elementary.ge_cattletier2_(
                    ne_m=seq.step.ne_m.value,
                    ne_a=seq.step.ne_a.value,
                    ne_l=seq.step.ne_l.value,
                    ne_p=seq.step.ne_p.value,
                    ne_work=seq.step.ne_work.value,
                    ne_g=seq.step.ne_g.value,
                    reg=seq.step.reg.value,
                    rem=seq.step.rem.value,
                    de=seq.step.de.value,
                )
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
    elif species_type.startswith(("sheep", "goat")):
        seq.read_parameter(name="c_a", table="c_a_sheep")

        value = seq.elementary.nea_sheep_(
            c_a=seq.step.c_a.value, weight=seq.step.weight.value
        )
        seq.store_result(
            name="ne_a",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(
            name="bw_i", table="bw_i", coords=[year, region, species_type]
        )

        seq.read_parameter(
            name="bw_f", table="bw_f", coords=[year, region, species_type]
        )

        seq.read_parameter(name="a", table="a", coords=[species_type])

        seq.read_parameter(name="b", table="b", coords=[species_type])

        value = seq.elementary.neg_sheep_(
            bw_f=seq.step.bw_f.value,
            bw_i=seq.step.bw_i.value,
            a=seq.step.a.value,
            b=seq.step.b.value,
        )
        seq.store_result(
            name="ne_g",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        # eq 10.9 or 10.10
        seq.read_parameter(
            name="milk", table="milk", coords=[year, region, species_type]
        )

        seq.read_parameter(
            name="ev_milk", table="ev_milk", coords=[year, region, species_type]
        )

        value = seq.elementary.nel_asheep_(
            milk=seq.step.milk.value, ev_milk=seq.step.ev_milk.value
        )
        seq.store_result(
            name="ne_l",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )
        # 10.10
        # seq.read_parameter(
        #    name="WG_mean", table="WG_mean", coords=[year, region, species_type]
        # )
        # seq.read_parameter(
        #    name="EV_milk", table="EV_milk", coords=[year, region, species_type]
        # )
        # value = seq.elementary.nel_bsheep_(
        #    W=seq.step.MILK.value, EV_milk=seq.step.EV_milk.value
        # )
        # seq.store_result(
        #    name="NE_L",
        #    value=value,
        #    unit="MJ/piece/day",
        #    year=year,
        # )
        seq.read_parameter(
            name="ev_wool", table="ev_wool", coords=[year, region, species_type]
        )
        seq.read_parameter(
            name="pr_wool", table="pr_wool", coords=[year, region, species_type]
        )

        value = seq.elementary.ne_wool(
            ev_wool=seq.step.ev_wool.value, pr_wool=seq.step.pr_wool.value
        )
        seq.store_result(
            name="ne_wool",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(
            name="c_pregnancy", table="c_pregnancy", coords=[species_type]
        )

        seq.read_parameter(
            name="ratio_preg",
            table="ratio_preg",
            coords=[year, region, species_type],
        )
        value = seq.elementary.ne_p(
            ne_m=seq.step.ne_m.value,
            c_pregnancy=seq.step.c_pregnancy.value,
            ratio_preg=seq.step.ratio_preg.value,
        )
        seq.store_result(
            name="ne_p",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="de", table="de", coords=[year, region, species_type])
        value = seq.elementary.rem(de=seq.step.de.value)
        seq.store_result(
            name="rem",
            value=value,
            unit="MJ/MJ",
            year=year,
        )
        value = seq.elementary.reg(de=seq.step.de.value)
        seq.store_result(
            name="reg",
            value=value,
            unit="MJ/MJ",
            year=year,
        )

        value = seq.elementary.ge_sheeptier2_(
            ne_m=seq.step.ne_m.value,
            ne_a=seq.step.ne_a.value,
            ne_l=seq.step.ne_l.value,
            ne_p=seq.step.ne_p.value,
            ne_wool=seq.step.ne_wool.value,
            ne_g=seq.step.ne_g.value,
            reg=seq.step.reg.value,
            rem=seq.step.rem.value,
            de=seq.step.de.value,
        )
        seq.store_result(
            name="ge",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

    seq.read_parameter(
        name="ym",
        table="ym",
        coords=[year, region, species_type, diet_type],
    )
    value = seq.elementary.ef_atier2_(
        ge=seq.step.ge.value,
        ym=seq.step.ym.value,
    )
    seq.store_result(
        name="ef",
        value=value,
        unit="kg/piece/year",
        year=year,
    )

    #####
    seq.read_parameter(
        name="n",
        table="n",
        coords=[year, region, species_type],
    )
    value = seq.elementary.e(
        n=seq.step.n.value,
        ef=seq.step.ef.value,
    )
    seq.store_result(
        name="ch4",
        value=value,
        unit="Gg/year",
        year=year,
    )
    logger.info("---> livestock-manure-treat sequence finalized.")
    return seq.step


def tier1_ch4_manure(
    year=2019,
    region="DE",
    species_type="cattle-dairy",
    manuretreat_type="drylot",
    climate_zone="temperate-cool",
    moisture_regime="moist",
    uncertainty="def",
):
    """
    diet_type : str
        optional, required for growing cattle and calve
    feeding_situation : str
        optional, required for cattle and buffalo
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("livestock-manure-treat sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(
        name="n",
        table="n",
        coords=[year, region, species_type],
    )

    if species_type in [
        "deer",
        "reindeer",
        "rabbit",
        "furbearing_mink",
        "furbearing_fox",
        "ostrich",
    ]:
        seq.read_parameter(
            name="ef",
            table="ef_ch4_v4c10_others",
            coords=[species_type],
        )
        value = seq.elementary.ch4_other_animals(
            n=seq.step.n.value,
            ef_others=seq.step.ef.value,
        )
        seq.store_result(
            name="ch4",
            value=value,
            unit="kg/year",
            year=year,
        )
    else:
        seq.read_parameter(
            name="vs_rate",
            table="vs_rate",
            coords=[year, region, species_type],
        )
        seq.read_parameter(
            name="tam",
            table="weight",
            coords=[year, region, species_type],
        )
        value = seq.elementary.vs_tier1_(
            vs_rate=seq.step.vs_rate.value,
            tam=seq.step.tam.value,
        )
        seq.store_result(
            name="vs",
            value=value,
            unit="kg/1000kg/year",
            year=year,
        )

        seq.read_parameter(
            name="ef",
            table="ef_ch4_v4c10",
            coords=[species_type, manuretreat_type, climate_zone, moisture_regime],
        )
        seq.read_parameter(
            name="awms",
            table="ms",
            coords=[year, region, species_type, manuretreat_type],
        )
        seq.read_parameter(
            name="n",
            table="n",
            coords=[year, region, species_type],
        )
        value = seq.elementary.ch4_mm(
            n=seq.step.n_rate.value,
            vs=seq.step.vs.value,
            awms=seq.step.awms.value,
            ef=seq.step.ef.value,
        )
        seq.store_result(
            name="ch4",
            value=value,
            unit="kg/year",
            year=year,
        )
    logger.info("---> livestock-manure-treat sequence finalized.")
    return seq.step


def tier2_ch4_manure(
    year=2019,
    region="DE",
    species_type="cattle-dairy",
    feeding_situation="stall",
    diet_type="forage-mod",
    manuretreat_type="drylot",
    climate_zone="temperate-cool",
    moisture_regime="moist",
    uncertainty="def",
):

    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("livestock-manure-treat sequence started --->")
    seq.store_signature(locals())

    #### activity
    seq.read_parameter(name="cf_i", table="cf_i", coords=[species_type])

    seq.read_parameter(
        name="weight", table="weight", coords=[year, region, species_type]
    )

    value = seq.elementary.ne_m(cf_i=seq.step.cf_i.value, weight=seq.step.weight.value)

    seq.store_result(
        name="ne_m",
        value=value,
        unit="MJ/piece/day",
        year=year,
    )

    if species_type.startswith(("cattle", "buffalo", "sheep", "goat")):
        if species_type.startswith(("cattle", "buffalo")):
            seq.read_parameter(
                name="c_a", table="c_a_cattle", coords=[feeding_situation]
            )

            value = seq.elementary.nea_cattle_(
                c_a=seq.step.c_a.value, ne_m=seq.step.ne_m.value
            )
            seq.store_result(
                name="ne_a",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="bw", table="weight", coords=[year, region, species_type]
            )

            seq.read_parameter(name="c", table="c", coords=[species_type])

            seq.read_parameter(
                name="mw", table="mw", coords=[year, region, species_type]
            )

            seq.read_parameter(
                name="wg", table="wg", coords=[year, region, species_type]
            )

            value = seq.elementary.neg_cattle_(
                bw=seq.step.bw.value,
                c=seq.step.c.value,
                mw=seq.step.mw.value,
                wg=seq.step.wg.value,
            )
            seq.store_result(
                name="ne_g",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="milk", table="milk", coords=[year, region, species_type]
            )

            seq.read_parameter(
                name="fat", table="fat", coords=[year, region, species_type]
            )

            value = seq.elementary.nel_cattle_(
                milk=seq.step.milk.value, fat=seq.step.fat.value
            )
            seq.store_result(
                name="ne_l",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="workhours", table="workhours", coords=[year, region, species_type]
            )

            value = seq.elementary.ne_work(
                ne_m=seq.step.ne_m.value, hours=seq.step.workhours.value
            )
            seq.store_result(
                name="ne_work",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="c_pregnancy", table="c_pregnancy", coords=[species_type]
            )

            seq.read_parameter(
                name="ratio_preg",
                table="ratio_preg",
                coords=[year, region, species_type],
            )

            value = seq.elementary.ne_p(
                ne_m=seq.step.ne_m.value,
                c_pregnancy=seq.step.c_pregnancy.value,
                ratio_preg=seq.step.ratio_preg.value,
            )
            seq.store_result(
                name="ne_p",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="de", table="de", coords=[year, region, species_type]
            )
            value = seq.elementary.rem(de=seq.step.de.value)
            seq.store_result(
                name="rem",
                value=value,
                unit="MJ/MJ",
                year=year,
            )

            value = seq.elementary.reg(de=seq.step.de.value)
            seq.store_result(
                name="reg",
                value=value,
                unit="MJ/MJ",
                year=year,
            )

            if "cattle" in species_type and "calve" in species_type:
                seq.read_parameter(
                    name="ne_mf", table="ne_mf", coords=[year, region, diet_type]
                )

                value = seq.elementary.dmi_calve_(
                    ne_mf=seq.step.ne_mf.value, bw=seq.step.bw.value
                )
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            elif "cattle" in species_type and "growing" in species_type:
                seq.read_parameter(
                    name="ne_mf", table="ne_mf", coords=[year, region, diet_type]
                )

                value = seq.elementary.dmi_growing_(
                    ne_mf=seq.step.ne_mf.value, bw=seq.step.bw.value
                )
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            elif "cattle" in species_type and "bull" in species_type:

                value = seq.elementary.dmi_steer_(bw=seq.step.bw.value)
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(name="ge", value=value, unit="mj/piece/day", year=year)
            elif "cattle" in species_type and "heifer" in species_type:
                value = seq.elementary.dmi_heifer_(bw=seq.step.bw.value)
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            elif "cattle" in species_type and "dairy" in species_type:
                value = seq.elementary.fcm(
                    milk=seq.step.milk.value, fat=seq.step.fat.value
                )
                seq.store_result(
                    name="fcm",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )

                value = seq.elementary.dmi_lactating_(
                    bw=seq.step.bw.value, fcm=seq.step.fcm.value
                )
                seq.store_result(
                    name="dmi",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.dmi_to_ge(dmi=seq.step.dmi.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            else:
                value = seq.elementary.ge_cattletier2_(
                    ne_m=seq.step.ne_m.value,
                    ne_a=seq.step.ne_a.value,
                    ne_l=seq.step.ne_l.value,
                    ne_p=seq.step.ne_p.value,
                    ne_work=seq.step.ne_work.value,
                    ne_g=seq.step.ne_g.value,
                    reg=seq.step.reg.value,
                    rem=seq.step.rem.value,
                    de=seq.step.de.value,
                )
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )

    elif species_type.startswith(("sheep", "goat")):
        seq.read_parameter(name="c_a", table="c_a_sheep")

        value = seq.elementary.nea_sheep_(
            c_a=seq.step.c_a.value, weight=seq.step.weight.value
        )
        seq.store_result(
            name="ne_a",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(
            name="bw_i", table="bw_i", coords=[year, region, species_type]
        )

        seq.read_parameter(
            name="bw_f", table="bw_f", coords=[year, region, species_type]
        )

        seq.read_parameter(name="a", table="a", coords=[species_type])

        seq.read_parameter(name="b", table="b", coords=[species_type])

        value = seq.elementary.neg_sheep_(
            bw_f=seq.step.bw_f.value,
            bw_i=seq.step.bw_i.value,
            a=seq.step.a.value,
            b=seq.step.b.value,
        )
        seq.store_result(
            name="ne_g",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        # eq 10.9 or 10.10
        seq.read_parameter(
            name="milk", table="milk", coords=[year, region, species_type]
        )

        seq.read_parameter(
            name="ev_milk", table="ev_milk", coords=[year, region, species_type]
        )

        value = seq.elementary.nel_asheep_(
            milk=seq.step.milk.value, ev_milk=seq.step.ev_milk.value
        )
        seq.store_result(
            name="ne_l",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )
        # 10.10
        # seq.read_parameter(
        #    name="WG_mean", table="WG_mean", coords=[year, region, species_type]
        # )
        # seq.read_parameter(
        #    name="EV_milk", table="EV_milk", coords=[year, region, species_type]
        # )
        # value = seq.elementary.nel_bsheep_(
        #    W=seq.step.MILK.value, EV_milk=seq.step.EV_milk.value
        # )
        # seq.store_result(
        #    name="NE_L",
        #    value=value,
        #    unit="MJ/piece/day",
        #    year=year,
        # )

        seq.read_parameter(
            name="ev_wool", table="ev_wool", coords=[year, region, species_type]
        )
        seq.read_parameter(
            name="pr_wool", table="pr_wool", coords=[year, region, species_type]
        )

        value = seq.elementary.ne_wool(
            ev_wool=seq.step.ev_wool.value, pr_wool=seq.step.pr_wool.value
        )
        seq.store_result(
            name="ne_wool",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(
            name="c_pregnancy", table="c_pregnancy", coords=[species_type]
        )

        seq.read_parameter(
            name="ratio_preg",
            table="ratio_preg",
            coords=[year, region, species_type],
        )
        value = seq.elementary.ne_p(
            ne_m=seq.step.ne_m.value,
            c_pregnancy=seq.step.c_pregnancy.value,
            ratio_preg=seq.step.ratio_preg.value,
        )
        seq.store_result(
            name="ne_p",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="de", table="de", coords=[year, region, species_type])
        value = seq.elementary.rem(de=seq.step.de.value)
        seq.store_result(
            name="rem",
            value=value,
            unit="MJ/MJ",
            year=year,
        )
        value = seq.elementary.reg(de=seq.step.de.value)
        seq.store_result(
            name="reg",
            value=value,
            unit="MJ/MJ",
            year=year,
        )

        value = seq.elementary.ge_sheeptier2_(
            ne_m=seq.step.ne_m.value,
            ne_a=seq.step.ne_a.value,
            ne_l=seq.step.ne_l.value,
            ne_p=seq.step.ne_p.value,
            ne_wool=seq.step.ne_wool.value,
            ne_g=seq.step.ne_g.value,
            reg=seq.step.reg.value,
            rem=seq.step.rem.value,
            de=seq.step.de.value,
        )
        seq.store_result(
            name="ge",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

    seq.read_parameter(name="ash", table="ash", coords=[year, region, species_type])
    seq.read_parameter(name="ue", table="ue", coords=[year, region, species_type])
    value = seq.elementary.vs_tier2_(
        ge=seq.step.ge.value,
        de=seq.step.de.value,
        ue=seq.step.ue.value,
        ash=seq.step.ash.value,
    )
    seq.store_result(
        name="vs",
        value=value,
        unit="kg/piece/day",
        year=year,
    )

    seq.read_parameter(name="b0", table="b0", coords=[year, region, species_type])
    seq.read_parameter(
        name="mcf",
        table="mcf_v4c10",
        coords=[manuretreat_type, climate_zone, moisture_regime],
    )
    seq.read_parameter(
        name="awms", table="ms", coords=[year, region, species_type, manuretreat_type]
    )
    value = seq.elementary.ef_mm(
        vs=seq.step.vs.value,
        b0=seq.step.b0.value,
        mcf=seq.step.mcf.value,
        awms=seq.step.awms.value,
    )
    seq.store_result(
        name="ef",
        value=value,
        unit="kg/piece/year",
        year=year,
    )

    seq.read_parameter(name="n", table="n", coords=[year, region, species_type])
    value = seq.elementary.ch4_mm(
        n=seq.step.n.value,
        vs=seq.step.vs.value,
        ef=seq.step.ef.value,
        awms=seq.step.awms.value,
    )
    seq.store_result(
        name="ch4",
        value=value,
        unit="kg/year",
        year=year,
    )

    logger.info("---> livestock-manure-treat sequence finalized.")
    return seq.step
