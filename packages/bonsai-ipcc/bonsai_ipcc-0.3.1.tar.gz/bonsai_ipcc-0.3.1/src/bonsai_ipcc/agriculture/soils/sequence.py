"""
Sequences to determine GHG emissions from managed soils.


"""


import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def tier1_n2o_inputs(
    year=2019,
    region="DE",
    crop_type="wheat_spring",
    landuse_type="CL-ANNUAL",
    cultivation_type="N_unspec",
    climate_zone="temperate",
    moisture_regime="wet",
    landusechange=False,  # {"year_ref"=int, "landusechange_type":"CL_CL"}
    uncertainty="def",
):
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("soils sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(
        name="yield_fresh",
        table="yield_fresh",
        coords=[year, region, landuse_type, crop_type],
    )

    seq.read_parameter(
        name="dry",
        table="dry",
        coords=[year, region, crop_type],
    )

    value = seq.elementary.crop(
        yield_fresh=seq.step.yield_fresh.value, dry=seq.step.dry.value
    )
    seq.store_result(
        name="crop",
        value=value,
        unit="kg/ha",
        year=year,
    )

    seq.read_parameter(
        name="r_ag",
        table="r_ag",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="rs",
        table="rs",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="n_ag",
        table="n_ag",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="n_bg",
        table="n_bg",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="area",
        table="area",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="frac_renew",
        table="frac_renew",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="frac_remove",
        table="frac_remove",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="frac_burnt",
        table="frac_burnt",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="c_f",
        table="c_f",
        coords=[year, region, crop_type],
    )

    value = seq.elementary.f_cr(
        crop=seq.step.crop.value,
        r_ag=seq.step.r_ag.value,
        area=seq.step.area.value,
        n_ag=seq.step.n_ag.value,
        frac_remove=seq.step.frac_remove.value,
        frac_burnt=seq.step.frac_burnt.value,
        frac_renew=seq.step.frac_renew.value,
        c_f=seq.step.c_f.value,
        rs=seq.step.rs.value,
        n_bg=seq.step.n_bg.value,
    )
    seq.store_result(
        name="f_cr",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="f_am",
        table="n_mms",
        coords=[year, region, landuse_type, crop_type],
    )

    seq.read_parameter(
        name="f_comp",
        table="f_comp",
        coords=[year, region, landuse_type, crop_type],
    )

    seq.read_parameter(
        name="f_sew",
        table="f_sew",
        coords=[year, region, landuse_type, crop_type],
    )

    seq.read_parameter(
        name="f_ooa",
        table="f_ooa",
        coords=[year, region, landuse_type, crop_type],
    )

    value = seq.elementary.f_on(
        f_am=seq.step.f_am.value,
        f_sew=seq.step.f_sew.value,
        f_comp=seq.step.f_comp.value,
        f_ooa=seq.step.f_ooa.value,
    )
    seq.store_result(
        name="f_on",
        value=value,
        unit="kg/year",
        year=year,
    )

    if landusechange is not False:
        # inventory year
        # sum over all management types
        # climate_zone,moisture_regime,soil_type,landuse_type,management_practice,amendment_level
        year_ref = landusechange["year_ref"]
        landusechange_type = landusechange["landusechange_type"]

        d = seq.get_inventory_levels(table="a", year=year, region=region)
        value = 0.0
        for i in range(len(list(d.values())[0])):
            climate_zone = d["climate_zone"][i]
            moisture_regime = d["moisture_regime"][i]
            soil_type = d["soil_type"][i]
            landuse_type = d["landuse_type"][i]
            management_practice = d["management_practice"][i]
            amendment_level = d["amendment_level"][i]

            seq.read_parameter(
                name="a_0",
                table="a",
                coords=[
                    year,
                    region,
                    climate_zone,
                    moisture_regime,
                    soil_type,
                    landuse_type,
                    management_practice,
                    amendment_level,
                ],
            )

            seq.read_parameter(
                name="soc_ref_0",
                table="soc_ref",
                coords=[climate_zone, moisture_regime, soil_type],
            )

            seq.read_parameter(
                name="f_lu_0",
                table="f_lu",
                coords=[landuse_type, climate_zone, moisture_regime],
            )

            seq.read_parameter(
                name="f_mg_0",
                table="f_mg",
                coords=[management_practice, climate_zone, moisture_regime],
            )

            seq.read_parameter(
                name="f_i_0",
                table="f_i",
                coords=[amendment_level, climate_zone, moisture_regime],
            )

            value += seq.elementary.soc(
                soc_ref=seq.step.soc_ref_0.value,
                f_lu=seq.step.f_lu_0.value,
                f_mg=seq.step.f_mg_0.value,
                f_i=seq.step.f_i_0.value,
                a=seq.step.a_0.value,
            )
        seq.store_result(
            name="soc_0",
            value=value,
            unit="t",
            year=year,
        )

        # inventory year
        # sum over all management types
        d = seq.get_inventory_levels(table="a", year=year_ref, region=region)
        value = 0.0
        for i in range(len(list(d.values())[0])):
            climate_zone = d["climate_zone"][i]
            moisture_regime = d["moisture_regime"][i]
            soil_type = d["soil_type"][i]
            landuse_type = d["landuse_type"][i]
            management_practice = d["management_practice"][i]
            amendment_level = d["amendment_level"][i]

            seq.read_parameter(
                name="soc_ref_T",
                table="soc_ref",
                coords=[climate_zone, moisture_regime, soil_type],
            )

            seq.read_parameter(
                name="f_lu_T",
                table="f_lu",
                coords=[landuse_type, climate_zone, moisture_regime],
            )

            seq.read_parameter(
                name="f_mg_T",
                table="f_mg",
                coords=[management_practice, climate_zone, moisture_regime],
            )

            seq.read_parameter(
                name="f_i_T",
                table="f_i",
                coords=[amendment_level, climate_zone, moisture_regime],
            )

            seq.read_parameter(
                name="a_T",
                table="a",
                coords=[
                    year_ref,
                    region,
                    climate_zone,
                    moisture_regime,
                    soil_type,
                    landuse_type,
                    management_practice,
                    amendment_level,
                ],
            )

            value += seq.elementary.soc(
                soc_ref=seq.step.soc_ref_T.value,
                f_lu=seq.step.f_lu_T.value,
                f_mg=seq.step.f_mg_T.value,
                f_i=seq.step.f_i_T.value,
                a=seq.step.a_T.value,
            )
        seq.store_result(
            name="soc_T",
            value=value,
            unit="t",
            year=year_ref,
        )

        value = seq.elementary.delta_c_mineral(
            soc_0=seq.step.soc_0.value,
            soc_t=seq.step.soc_T.value,
            d=20,
        )
        seq.store_result(
            name="delta_c_mineral",
            value=value,
            unit="t/year",
            year=year,
        )

        seq.read_parameter(
            name="r",
            table="r",
            coords=[year, region, landusechange_type],
        )

        value = seq.elementary.f_som(
            delta_c_mineral=seq.step.delta_c_mineral.value, r=seq.step.r.value
        )
        seq.store_result(
            name="f_som",
            value=value,
            unit="kg/year",
            year=year,
        )

    else:
        logger.info(
            "Not able to estimate gross changes of mineral soil C. Consider to collect the required data. Bias in the N2O estimate."
        )
        value = 0.0
        seq.store_result(
            name="f_som",
            value=value,
            unit="kg/year",
            year=year,
        )

    seq.read_parameter(
        name="ef1",
        table="ef1",
        coords=[year, region, cultivation_type, moisture_regime],
    )

    seq.read_parameter(
        name="f_sn",
        table="f_sn",
        coords=[year, region, landuse_type, cultivation_type],
    )

    value = seq.elementary.n2o_n_inputs(
        f_sn=seq.step.f_sn.value,
        f_on=seq.step.f_on.value,
        f_cr=seq.step.f_cr.value,
        f_som=seq.step.f_som.value,
        ef1=seq.step.ef1.value,
    )
    seq.store_result(
        name="n2o_n_inputs",
        value=value,
        unit="kg/year",
        year=year,
    )

    value = seq.elementary.n2o(n2o_n=seq.step.n2o_n_inputs.value)
    seq.store_result(
        name="n2o_inputs",
        value=value,
        unit="kg/year",
        year=year,
    )

    logger.info("---> soil sequence finalized.")
    return seq.step


def tier1_n2o_os(
    year=2019,
    region="DE",
    landuse_type="CL",
    climate_zone="temperate",
    uncertainty="def",
):
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("soils sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(
        name="ef2",
        table="ef2",
        coords=[landuse_type, climate_zone],
    )

    seq.read_parameter(
        name="f_os",
        table="f_os",
        coords=[year, region, landuse_type, climate_zone],
    )

    value = seq.elementary.n2o_n_os(f_os=seq.step.f_os.value, ef2=seq.step.ef2.value)
    seq.store_result(
        name="n2o_n_os",
        value=value,
        unit="kg/year",
        year=year,
    )

    value = seq.elementary.n2o(n2o_n=seq.step.n2o_n_os.value)
    seq.store_result(
        name="n2o_os",
        value=value,
        unit="kg/year",
        year=year,
    )

    logger.info("---> soil sequence finalized.")
    return seq.step


def tier1_n2o_prp(
    year=2010,
    region="DE",
    landuse_type="CL",
    species_type="cattle-dairy",
    climate_zone="temperate",
    uncertainty="def",
):
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("soils sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(
        name="TAM",
        table="WEIGHT",
        coords=[year, region, species_type],
    )
    logger.info("N_RATE")
    seq.read_parameter(
        name="N_RATE",
        table="N_RATE",
        coords=[year, region, species_type],
    )

    value = seq.elementary.nex_tier1_(
        N_RATE=seq.step.N_RATE.value,
        TAM=seq.step.TAM.value,
    )

    seq.store_result(
        name="NEX",
        value=value,
        unit="kg/piece/year",
        year=year,
    )

    seq.read_parameter(
        name="n",
        table="N",
        coords=[year, region, species_type],
    )

    seq.read_parameter(
        name="ms",
        table="MS",
        coords=[year, region, species_type, "pasture"],
    )

    value = seq.elementary.f_prp(
        n=seq.step.n.value,
        nex=seq.step.nex.value,
        ms=seq.step.ms.value,
    )

    seq.store_result(
        name="f_prp",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="ef3",
        table="ef3",
        coords=[landuse_type, climate_zone],
    )

    value = seq.elementary.n2o_n_prp(f_prp=seq.step.f_prp.value, ef3=seq.step.ef3.value)
    seq.store_result(
        name="n2o_n_prp",
        value=value,
        unit="kg/year",
        year=year,
    )

    value = seq.elementary.n2o(n2o_n=seq.step.n2o_n_prp.value)
    seq.store_result(
        name="n2o_prp",
        value=value,
        unit="kg/year",
        year=year,
    )

    logger.info("---> soil sequence finalized.")
    return seq.step


def tier1_n2o_direct(
    year=2019,
    region="DE",
    crop_type="wheat_spring",
    landuse_type="CL",
    cultivation_type="N_unspec",
    species_type="cattle-dairy",
    moisture_regime="wet",
    climate_zone="temperal",
    uncertainty="def",
):
    """
    can be also used for tier 2
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("soils sequence started --->")
    seq.store_signature(locals())

    # N2O directly from N inputs (inputs)
    seq.read_parameter(
        name="yield_fresh",
        table="yield_fresh",
        coords=[year, region, landuse_type, crop_type],
    )

    seq.read_parameter(
        name="dry",
        table="dry",
        coords=[year, region, crop_type],
    )

    value = seq.elementary.crop(
        yield_fresh=seq.step.yield_fresh.value, dry=seq.step.dry.value
    )
    seq.store_result(
        name="crop",
        value=value,
        unit="kg/ha",
        year=year,
    )

    seq.read_parameter(
        name="r_ag",
        table="r_ag",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="rs",
        table="rs",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="n_ag",
        table="n_ag",
        coords=[year, region, landuse_type, crop_type],
    )

    seq.read_parameter(
        name="n_bg",
        table="n_bg",
        coords=[year, region, landuse_type, crop_type],
    )

    seq.read_parameter(
        name="area",
        table="area",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="frac_renew",
        table="frac_renew",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="frac_remove",
        table="frac_remove",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="frac_burnt",
        table="frac_burnt",
        coords=[year, region, crop_type],
    )

    seq.read_parameter(
        name="c_f",
        table="c_d",
        coords=[year, region, crop_type],
    )

    value = seq.elementary.f_cr(
        crop=seq.step.crop.value,
        r_ag=seq.step.r_ag.value,
        area=seq.step.area.value,
        n_ag=seq.step.n_ag.value,
        frac_remove=seq.step.frac_remove.value,
        frac_burnt=seq.step.frac_burnt.value,
        frac_renew=seq.step.frac_renew.value,
        c_f=seq.step.c_f.value,
        rs=seq.step.rs.value,
        n_bg=seq.step.n_bg.value,
    )
    seq.store_result(
        name="f_cr",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="n_mms",
        table="f_am",
        coords=[year, region, landuse_type, crop_type],
    )

    seq.read_parameter(
        name="f_comp",
        table="f_comp",
        coords=[year, region, landuse_type, crop_type],
    )

    seq.read_parameter(
        name="f_sew",
        table="f_sew",
        coords=[year, region, landuse_type, crop_type],
    )

    seq.read_parameter(
        name="f_ooa",
        table="f_ooa",
        coords=[year, region, landuse_type, crop_type],
    )

    value = seq.elementary.f_on(
        f_am=seq.step.f_am.value,
        f_sew=seq.step.f_sew.value,
        f_comp=seq.step.f_comp.value,
        f_ooa=seq.step.f_ooa.value,
    )
    seq.store_result(
        name="f_on",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="ef1",
        table="ef1",
        coords=[year, region, cultivation_type, moisture_regime],
    )

    seq.read_parameter(
        name="f_sn",
        table="f_sn",
        coords=[year, region, landuse_type, cultivation_type],
    )

    value = seq.elementary.n2o_n_inputs(
        f_sn=seq.step.f_sn.value,
        f_on=seq.step.f_on.value,
        f_cr=seq.step.f_cr.value,
        f_som=seq.step.f_som.value,
        ef1=seq.step.ef1.value,
    )
    seq.store_result(
        name="n2o_n_inputs",
        value=value,
        unit="kg/year",
        year=year,
    )

    # N2O from organic soils (os)
    seq.read_parameter(
        name="ef2",
        table="ef2",
        coords=[landuse_type, climate_zone],
    )

    seq.read_parameter(
        name="f_os",
        table="f_os",
        coords=[year, region, landuse_type, climate_zone],
    )

    value = seq.elementary.n2o_n_os(f_os=seq.step.f_os.value, ef2=seq.step.ef2.value)
    seq.store_result(
        name="n2o_n_os",
        value=value,
        unit="kg/year",
        year=year,
    )

    # N2O from urine of animals on pasture-range-paddock (prp)
    seq.read_parameter(
        name="TAM",
        table="WEIGHT",
        coords=[year, region, species_type],
    )
    logger.info("N_RATE")
    seq.read_parameter(
        name="N_RATE",
        table="N_RATE",
        coords=[year, region, species_type],
    )

    value = seq.elementary.nex_tier1_(
        N_RATE=seq.step.N_RATE.value,
        TAM=seq.step.TAM.value,
    )

    seq.store_result(
        name="NEX",
        value=value,
        unit="kg/piece/year",
        year=year,
    )

    seq.read_parameter(
        name="n",
        table="N",
        coords=[year, region, species_type],
    )

    seq.read_parameter(
        name="ms",
        table="MS",
        coords=[year, region, species_type, "pasture"],
    )

    value = seq.elementary.f_prp(
        n=seq.step.n.value,
        nex=seq.step.nex.value,
        ms=seq.step.ms.value,
    )

    seq.store_result(
        name="f_prp",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="ef3",
        table="ef3",
        coords=[landuse_type, climate_zone],
    )

    value = seq.elementary.n2o_n_prp(f_prp=seq.step.f_prp.value, ef3=seq.step.ef3.value)
    seq.store_result(
        name="n2o_n_prp",
        value=value,
        unit="kg/year",
        year=year,
    )

    # sum up
    value = seq.elementary.n2o_n_direct(
        n2o_n_inputs=seq.step.n2o_n_inputs.value,
        n2o_n_os=seq.step.n2o_n_inputs.value,
        n2o_n_prp=seq.step.n2o_n_prp.value,
    )
    seq.store_result(
        name="n2o_n_direct",
        value=value,
        unit="kg/year",
        year=year,
    )

    value = seq.elementary.n2o(n2o_n=seq.step.n2o_n_direct.value)
    seq.store_result(
        name="n2o_direct",
        value=value,
        unit="kg/year",
        year=year,
    )

    logger.info("---> soil sequence finalized.")
    return seq.step
