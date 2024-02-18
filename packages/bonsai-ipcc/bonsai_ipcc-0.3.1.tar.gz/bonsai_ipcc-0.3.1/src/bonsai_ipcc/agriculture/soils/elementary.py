from ..generic.elementary import delta_c_mineral, n2o, soc
from ..livestock_manure.elementary import n_mms, nex_tier1_

# EQUATIONS TIER 1


def n2o_n_direct(n2o_n_inputs, n2o_n_os, n2o_n_prp):
    """
    Equation 11.1

    DIRECT N2O EMISSIONS as N FROM MANAGED SOILS (TIER 1)

    Argument
    --------
    n2o_n_inputs (kg/year) : float
         annual direct N 2O–N emissions produced from managed soils.
    n2o_n_os (kg/year) : float
        annual direct N 2O–N emissions from N inputs to managed soils.
    n2o_n_prp (kg/kg) : float
        annual direct N 2O–N emissions from managed organic soil.

    Returns
    -------
    VALUE: float
        DIRECT N2O EMISSIONS FROM MANAGED SOILS as N (kg/year)
    """
    n2o_n_direct = n2o_n_inputs + n2o_n_os + n2o_n_prp
    return n2o_n_direct


def n2o_n_inputs(f_sn, f_on, f_cr, f_som, ef1):
    """
    Equation 11.1

    annual direct N 2O–N emissions from N inputs to managed soil (tier1)
    also applicable for rice.

    Argument
    --------
    f_sn (kg/year) : float
        annual amount of synthetic fertiliser N applied to soils
    f_on (kg/year) : float
        annual amount of animal manure, compost, sewage sludge and other organic N additions applied to soils
    f_cr (kg/year) : float
        annual amount of N in crop residues
    f_som (kg/year) : float
        annual amount of N in mineral soils that is mineralised, in association with loss of soil C from soil organic matter as a result of changes to land use or management
    ef1 (kg/kg) : float
        emission factor for N2O emissions from N inputs (also for rice)

    Returns
    -------
    VALUE: float
        n2o_n_inputs (kg/year)
    """
    n2o_n_inputs = (f_sn + f_on + f_cr + f_som) * ef1
    return n2o_n_inputs


def n2o_n_os(f_os, ef2):
    """
    Equation 11.1

    annual direct N2O–N emissions from managed organic soils (tier1)
    modified - different sub-paramaters are merged into two.

    Argument
    --------
    f_os (ha) : float
        annual area of managed/drained organic soils
    ef2 (kg/ha/year) : float
        emission factor for N 2O emissions from drained/managed organic soil

    Returns
    -------
    VALUE: float
        n2o_n_os (kg/year)
    """
    n2o_n_os = f_os * ef2
    return n2o_n_os


def n2o_n_prp(f_prp, ef3):
    """
    Equation 11.1

    annual direct N2O–N emissions from urine and dung inputs to grazed soil (tier1)
    modified - different sub-paramaters are merged into two.

    Argument
    --------
    f_prp (kg/yr) : float
        annual amount of urine and dung N deposited by grazing animals on pasture, range and paddock
    ef3 (kg/kg) : float
        emission factor for N2O emissions from urine and dung N deposited on pasture, range and paddock by grazing animals

    Returns
    -------
    VALUE: float
        n2o_n_prp (kg/year)
    """
    n2o_n_prp = f_prp * ef3
    return n2o_n_prp


def f_on(f_am, f_sew, f_comp, f_ooa):
    """
    Equation 11.3

    N FROM ORGANIC N ADDITIONS APPLIED TO SOILS (tier1)

    Argument
    --------
    f_am (kg/year) : float
        total annual amount of organic N fertiliser applied to soils other than by grazing animals
    f_sew (kg/year) : float
        annual amount of animal manure N applied to soils
    f_comp (kg/year) : float
        annual amount of total sewage N
    f_ooa (kg/year) : float
        annual amount of total compost N applied to soils

    Returns
    -------
    VALUE: float
        f_on (kg/year)
    """
    f_on = f_am + f_sew + f_comp + f_ooa
    return f_on


def f_am(n_mms, frac_feed, frac_fuel, frac_cnst):
    """
    Equation 11.4

    N FROM ANIMAL MANURE APPLIED TO SOILS (tier1)

    Argument
    --------
    n_mms (kg/year) : float
        amount of managed manure N available for soil application, feed, fuel or construction
    frac_feed (kg/kg) : float
        fraction of managed manure used for feed
    frac_fuel (kg/kg) : float
        fraction of managed manure used for fuel
    frac_cnst (kg/kg) : float
       fraction of managed manure used for construction

    Returns
    -------
    VALUE: float
        f_on (kg/year)
    """
    f_on = n_mms * (1 - (frac_feed + frac_fuel + frac_cnst))
    return f_on


def f_cr(crop, r_ag, area, n_ag, frac_remove, frac_burnt, frac_renew, c_f, rs, n_bg):
    """
    Equation 11.6

    N FROM CROP RESIDUES AND FORAGE /PASTURE RENEWAL (TIER 1)

    Argument
    --------
    crop (kg/ha/year) : float
        harvested annual dry matter yield for crop
    r_ag (kg//ha/year) : float
        ratio of above-ground residue dry matter to harvested yield for crop
    area (ha/year) : float
        total annual area harvested of crop
    frac_renew (kg/kg) : float
       fraction of total area under crop T that is renewed annually
    frac_burnt (kg/kg) : float
       fraction of annual harvested area of crop
    frac_remove (kg/kg) : float
       fraction of above-ground residues of crop removed annually for purposes such as feed, bedding and construction
    c_f (kg/kg) : float
       combustion factor
    rs (kg/ha) : float
       ratio+ of below-ground root biomass to above-ground shoot biomass for crop
    n_bg (kg/kg) : float
       N content of below-ground residues for crop

    Returns
    -------
    VALUE: float
        f_cr (kg/year)
    """
    f_cr = crop * r_ag * n_ag * (1 - frac_remove - (frac_burnt * c_f)) + (
        (crop + crop * r_ag) * rs * area * frac_renew * n_bg
    )
    return f_cr


def crop(yield_fresh, dry):
    """
    Equation 11.7

    DRY- WEIGHT CORRECTION OF REPORTED CROP YIELDS (tier1)

    Argument
    --------
    yield_fresh (kg/ha) : float
        harvested fresh yield for crop
    dry (kg/kg) : float
        dry matter fraction of harvested crop

    Returns
    -------
    VALUE: float
        crop (kg/ha)
    """
    crop = yield_fresh * dry
    return crop


def f_prp(n, nex, ms):
    """
    Equation 11.5

    N IN URINE AND DUNG DEPOSITED BY GRAZING ANIMALS ON PASTURE, RANGE AND PADDOCK (tier1)

    Argument
    --------
    n (species/yr) : float
        umber of head of livestock species/category in the country
    nex (kg/species/yr) : float
        annual average N excretion per head of species/category in the country

    Returns
    -------
    VALUE: float
        f_prp (kg/yr)
    """
    f_prp = n * nex * ms
    return f_prp


def f_som(delta_c_mineral, r):
    """
    Equation 11.8
    N MINERALISED IN MINERAL SOILS AS A RESULT OF LOSS OF SOIL C THROUGH CHANGE IN LAND USE OR MANAGEMENT (TIERS 1 AND 2)

    Argument
    --------
    delta_c (t/yr) : float
        average annual loss of soil carbon for each land-use type
    r (t/t) : float
        C:N ratio of the soil organic matter

    Returns
    -------
    VALUE: float
        f_som (kg/yr)
    """
    f_som = delta_c_mineral * 1 / r * 1000
    return f_som
