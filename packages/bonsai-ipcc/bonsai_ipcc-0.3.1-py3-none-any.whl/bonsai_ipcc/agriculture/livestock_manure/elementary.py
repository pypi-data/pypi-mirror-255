# EQUATIONS TIER 1


def n2o_direct_mm(n, nex, ms, ef):
    """
    Equation 10.25

    Calculates the N20 for manure treatment
    Contrary to equations in guidelines, no summation over treatment types.

    Argument
    --------
    n (piece/year) : float
        number of head of livestock.
    nex (kg/piece/year) : float
        annual average N excretion per head of species
    ms (kg/kg) : float
        fraction of total annual nitrogen excrection for each livestock spiecies
    ef (kg/kg) : float
        emission factor for direct N2O emissions from manure management system,
        kg N2O / kg N

    Returns
    -------
    VALUE: float
        direct N20 emissions from manure management (kg/year)
    """
    n2o_direct_mm = n * nex * ms * ef * 44 / 28
    return n2o_direct_mm


def nex_tier1_(n_rate, tam):
    """
    Equation 10.30

    Annual N excretion rate (tier1)

    Argument
    --------
    n_rate (kg/t/day) : float
        default N excreation rate
    tam (kg/piece) : float
        typical animal mass for species

    Returns
    -------
    VALUE: float
        nex (kg/piece/year)
    """
    nex = n_rate * tam / 1000 * 365
    return nex


# EQUATIONS TIER 2


def nex_atier2_(n_intake, n_retention_frac):
    """
    Equation 10.31a

    Annual N excretion rate (tier2)

    Argument
    --------
    n_intake (kg/piece/day) : float
        the daily N intake per head of animal of species
    n_retention_frac (kg/kg) : float
        fraction of daily N intake that is retained by animal species

    Returns
    -------
    VALUE: float
        nex_tier2 (kg/piece/year)
    """
    nex = n_intake * (1 - n_retention_frac) * 365
    return nex


def nex_btier2_(n_intake, n_retention):
    """
    Equation 10.31a

    Annual N excretion rate (tier2)

    Argument
    --------
    n_intake (kg/piece/day) : float
        the daily N intake per head of animal of species
    n_retention (kg/piece) : float
        typical animal mass for species

    Returns
    -------
    VALUE: float
        nex_tier2_a (kg/piece/year)
    """
    nex = (n_intake - n_retention) * 365
    return nex


def nretention_cattletier2_(milk, milk_pr, wg, ne):
    """
    Equation 10.33

    N retention rates for cattle (tier2)

    Argument
    --------
    milk (kg/piece/day) : float
        milk production
    milk_pr (kg/kg) : float
        percent of protein in milk
    wg (kg/day) : float
        weight gain, input for each livestock category
    ne (MJ/day) : float
        net energy for growth, calculated in livestock characterisation

    Returns
    -------
    VALUE: float
        n_retention (kg/piece/year)
    """
    n_retention = ((milk * milk_pr / 100) / 6.38) + (
        wg * (268 - (7.03 * ne / wg) / 1000) / 6.25
    )
    return n_retention


def nretention_sowtier2_(fr, litsize, ckg, n_wp):
    """
    Equation 10.33a

    N retention rates for breeding sows (tier2)

    Argument
    --------
    fr (piece/year) : float
        fertility rate
    litsize (piece) : float
        litter size
    ckg (kg/piece) : float
        live wight of piglets at birth
    n_wp (kg/piece/year) : float
        amount of N in piglets weaned calculated as i eq.10.33

    Returns
    -------
    VALUE: float
        n_retention (kg/piece/year)
    """
    n_retention = (0.025 * fr * litsize * ckg / 0.806) + n_wp
    return n_retention


def nretention_piglettier2_(litsize, fr, wkg, ckg):
    """
    Equation 10.33b

    N retention rates for piglets (tier2)

    Argument
    --------
    litsize (pieces) : int
        litter size, heads per birth
    fr (1/year) : float
        fertility rate of sows per year
    wkg (kg/piece) : float
        live weight of piglets at weaning
    ckg (kg/piece) : float
        live weight of piglets at birth

    Returns
    -------
    VALUE: float
        n_retention_b (kg/piece/year)
    """
    n_retention = 0.025 * litsize * fr * (wkg - ckg) / 0.98
    return n_retention


def nretention_growingtier2_(bw_final, bw_initial, n_gain):
    """
    Equation 10.33c

    N retention rates for growing pigs (tier2)

    Argument
    --------
    bw_final (kg) : float
        live weight of the animal at the end of the growth stage
    bw_initial (kg) : float
        live weight of the animal at the beginning of the growth stage
    n_gain (kg/kg) : float
        fraction of N retained at a given BW per defined growth stage

    Returns
    -------
    VALUE: float
        n_retention_c (kg/piece/year)
    """
    n_retention = (bw_final - bw_initial) * n_gain
    return n_retention


def nretention_hentier2_(n_lw, wg, n_egg, egg):
    """
    Equation 10.33d

    N retention rates for layer type hens (tier2)

    Argument
    --------
    n_lw (kg/kg) : float
        average content of nitrogen in live weight
    wg (kg/piece/day) : float
        average daily weight gain
    n_egg (g/piece) : float
        average content of nitrogen in eggs
    egg (g/piece/day) : float
        egg mass production

    Returns
    -------
    VALUE: float
        n_retention_d (kg/piece/year)
    """
    n_retention = n_lw * wg + ((n_egg * egg) / 1000)
    return n_retention


def nretention_pullettier2_(bw_final, bw_initial, n_gain, production_period):
    """
    Equation 10.33e

    N retention rates for pullets or broilers (tier2)

    Argument
    --------
    bw_final (kg) : float
        live weight of the animal at the end of the growth stage
    bw_initial (kg) : float
        live weight of the animal at the beginning of the growth stage
    n_gain (kg/kg) : float
        fraction of N retained at a given BW per defined growth stage
    production_period (days) : float
        length of time from chick to slaughter

    Returns
    -------
    VALUE: float
        n_retention_e (kg/piece/year)
    """
    n_retention = (bw_final - bw_initial) * n_gain / production_period
    return n_retention


def nintake_cattletier2_(ge, cp):
    """
    Equation 10.32

    N intake rates for cattle, sheep and goats (tier2),
    per animal and growth stage

    Argument
    --------
    ge (MJ/piece/year) : float
        gross energy intake of the animal
    cp (kg/kg) : float
        percent crude protein in dry matter for growth stage

    Returns
    -------
    VALUE: float
        n_intake (kg/piece/day)
    """
    n_intake = ge / 18.45 * (cp / 6.25)
    return n_intake


def nintake_swinetier2_(dmi, cp):
    """
    Equation 10.32a

    N intake rates for swine and poultry (tier2),
    per animal and growth stage

    Argument
    --------
    dmi (kg/piece/day) : float
        dry matter intake per day during a specific growth stage
    cp (kg/kg) : float
        percent crude protein in dry matter for growth stage

    Returns
    -------
    VALUE: float
        n_intake (kg/piece/day)
    """
    n_intake = dmi * (cp / 6.25)
    return n_intake


def ge_cattletier2_(ne_m, ne_a, ne_l, ne_work, ne_p, rem, de, ne_g, reg):
    """
    Equation 10.16 (distinguished between cattle and sheep)

    Gross energy for cattle/buffalo (tier2)

    Argument
    --------
    ne_a (MJ/day) : float
        net energy for lanimal activity
    ne_l (MJ/day) : float
        net energy for lactation
    ne_work (MJ/day) : float
        net energy for work
    ne_p (MJ/day) : float
        net energy for pregnancy
    ne_g (MJ/day) : float
        net energy for growth
    rem (MJ/MJ) : float
        ratio of net energy available in a diet for maintenance to  digestible energy
    reg (MJ/MJ) : float
        ratio of net energy available for growthin a diet to digestible energy consumed
    de (MJ/MJ) : float
        digestiblilty of feed expressed as a fraction of gross energy

    Returns
    -------
    VALUE: float
        ge_cattle (MJ/piece/day)
    """
    ge_cattle = (((ne_m + ne_a + ne_l + ne_work + ne_p) / rem) + ((ne_g) / reg)) / de
    return ge_cattle


def ge_sheeptier2_(ne_m, ne_a, ne_l, ne_p, rem, de, ne_g, ne_wool, reg):
    """
    Equation 10.16 (distinguished between cattle and sheep)

    Gross energy for sheep and goats (tier2)

    Argument
    --------
    ne_a (MJ/day) : float
        net energy for lanimal activity
    ne_l (MJ/day) : float
        net energy for lactation
    ne_p (MJ/day) : float
        net energy for pregnancy
    ne_wool (MJ/day) : float
        net energy for producing a year of wool
    ne_g (MJ/day) : float
        net energy for growth
    rem (MJ/MJ) : float
        ratio of net energy available in a diet for maintenance to  digestible energy
    reg (MJ/MJ) : float
        ratio of net energy available for growthin a diet to digestible energy consumed
    de (MJ/MJ) : float
        digestiblilty of feed expressed as a fraction of gross energy

    Returns
    -------
    VALUE: float
        ge_sheep (MJ/piece/day)
    """
    ge_sheep = (((ne_m + ne_a + ne_l + ne_p) / rem) + ((ne_g + ne_wool) / reg)) / de
    return ge_sheep


def dmi_to_ge(dmi):
    """
    Equation 10.x (information in text)

    Conversion from dry matter intake to gross energy.
    (default factor)

    Argument
    --------
    dmi (kg/piece/day) : float
        dry matter intake

    Returns
    -------
    VALUE : float
        gross energy (MJ/piece/day)
    """
    dmi_to_ge = 18.45 * dmi
    return dmi_to_ge


def ne_m(cf_i, weight):
    """
    Equation 10.3

    Net energy for maintenance (tier2)

    Argument
    --------
    cf_i (MJ/day/kg) : float
        coefficient for calculating NE_M
    weight (kg/piece) : float
        live-weight of animal

    Returns
    -------
    VALUE: float
        ne_m (MJ/piece/day)
    """
    ne_m = cf_i * weight**0.76
    return ne_m


def nea_cattle_(c_a, ne_m):
    """
    Equation 10.4

    Net energy for activity, for cattle and buffalo (tier2)

    Argument
    --------
    c_a (MJ/MJ) : float
        coefficient corresponding to animals feeding situation
    ne_m (MJ/piece/day) : float
        net energy required by the animal maintenance

    Returns
    -------
    VALUE: float
        ne_a_cattle (MJ/day)
    """
    nea = c_a * ne_m
    return nea


def nea_sheep_(c_a, weight):
    """
    Equation 10.5

    Net energy for activity, for sheep and goats (tier2)

    Argument
    --------
    c_a (MJ/day/kg) : float
        coefficient corresponding to animals feeding situation
    weight (kg/piece) : float
        live-weight of animal

    Returns
    -------
    VALUE: float
        ne_a_sheep (MJ/day)
    """
    nea = c_a * weight
    return nea


def neg_cattle_(bw, mw, wg, c):
    """
    Equation 10.6

    Net energy for growth, for cattle and buffalo (tier2)

    Argument
    --------
    bw (kg/piece) : float
        average body live-weight of the population
    mw (kg/piece) : float
        mature body live-weight of an adult animal individually, mature females, mature males and steers) in moderate body condition
    wg (kg/piece/day) : float
        the average daily weight gain of the animals in the population
    c (MJ/MJ) : float
        coefficient for distinguishing sex and age


    Returns
    -------
    VALUE: float
        ne_g (MJ/piece/day)
    """
    neg = 22.02 * (bw / (c * mw)) ** 0.75 * wg**1.097
    return neg


def neg_sheep_(bw_i, bw_f, a, b):
    """
    Equation 10.7

    Net energy for growth, for sheeps and goats (tier2)

    Argument
    --------
    bw_i (kg/piece) : float
        body live-weight at weaning
    bw_f (kg/piece) : float
        the live bodyweight at 1-year old or at slaughter (live-weight) if slaughtered prior to 1 year of age
    a (MJ/kg) : float
        constant for calculating NE_G
    b (MJ/kg) : float
        constant for calculating NE_G

    Returns
    -------
    VALUE: float
        ne_g (MJ/piece/day)
    """
    neg = (bw_f - bw_i) * (a + 0.5 * b * (bw_i + bw_f)) / 365
    return neg


def nel_cattle_(milk, fat):
    """
    Equation 10.8

    Net energy for lactation, for beef cattle, dairy cattle and buffalo (tier2)

    Argument
    --------
    milk (kg/piece/day) : float
        amount of milk produced
    fat (kg/kg) : float
        fat content of milk, percent by weight

    Returns
    -------
    VALUE: float
        ne_l_cattle (MJ/piece/day)
    """
    nel = milk * (1.47 + 0.4 * fat)
    return nel


def nel_asheep_(milk, ev_milk):
    """
    Equation 10.9

    Net energy for lactation, for sheep and goats - known milk production (tier2)

    argument
    --------
    milk (kg/piece/day) : float
        amount of milk produced
    ev_milk (kg/kg) : float
        net energy required to produce 1 liter of milk

    Returns
    -------
    VALUE: float
        ne_l_sheep_a (MJ/piece/day)
    """
    nel = milk * ev_milk
    return nel


def nel_bsheep_(wg_wean, ev_milk):
    """
    Equation 10.10

    Net energy for lactation, for sheep and goats - unknown milk production (tier2)

    Argument
    --------
    wg_wean (kg/piece) : float
        weight gain of the lamb between birth and weaning
    ev_milk (kg/kg) : float
        net energy required to produce 1 liter of milk

    Returns
    -------
    VALUE: float
        ne_l_sheep_b (MJ/piece/day)
    """
    ne_l_sheep_b = ev_milk * (5 * wg_wean) / 365
    return nel


def ne_work(ne_m, hours):
    """
    Equation 10.11

    Net energy for work, cattle and buffalo (tier2)

    Argument
    --------
    ne_m (MJ/piece/day) : float
        net energy required by the animal for maintenance
    hours (h/day) : float
        number of hours of work per day

    Returns
    -------
    VALUE: float
        ne_work (MJ/piece/day)
    """
    ne_work = 0.1 * ne_m * hours
    return ne_work


def ne_wool(ev_wool, pr_wool):
    """
    Equation 10.12

    Net energy to produce wool, for sheep and goats (tier2)

    Argument
    --------
    ev_wool (MJ/kg) : float
        the energy value of each kg of wool
    pr_wool (kg/piece/year) : float
        annula wool production per sheep or goat

    Returns
    -------
    VALUE: float
        ne_wool (MJ/piece/day)
    """
    ne_wool = ev_wool * pr_wool / 365
    return ne_wool


def ne_p(c_pregnancy, ne_m, ratio_preg):
    """
    Equation 10.13 (adopted, due to text information)

    Net energy for pregnancy, cattle and buffalo and sheep and goats (tier2)

    Argument
    --------
    c_pregnancy (MJ/piece/day) : float
        pregnancy coefficient
    ne_m (h/day) : float
        net energy required by the animal for maintenance
    ratio_preg (piece/piece) : float
        ratio of animals of species type that gave birth over the year
        (introduced due to information in text)

    Returns
    -------
    VALUE: float
        ne_p (MJ/piece/day)
    """
    ne_p = c_pregnancy * ne_m * ratio_preg
    return ne_p


def rem(de):
    """
    Equation 10.14

    Ratio of net energy available in diet for mainzenance to digestible energy (tier2)

    Argument
    --------
    de (MJ/MJ) : float
        digestibility of feed expressed as a fraction of gross energy

    Returns
    -------
    VALUE: float
        rem (MJ/MJ)
    """
    rem = (1.123 - 0.004092) + ((0.00001126 * (de * 100) ** 2) - (25.4 / (de * 100)))
    return rem


def reg(de):
    """
    Equation 10.15

    Ratio of net energy available for growth in diet to digestible energy consumed (tier2)

    Argument
    --------
    de (MJ/MJ) : float
        digestibility of feed expressed as a fraction of gross energy

    Returns
    -------
    VALUE: float
        reg (MJ/MJ)
    """
    reg = (
        1.164
        - (5.16 * 10 ** (-3))
        + (1.308 * 10 ** (-5) * (de * 100) ** 2)
        - (37.4 / (de * 100))
    )
    return reg


def n_volatilization(n, nex, awms, frac_gas):
    """
    Equation 10.26

    N losses due to volatisation from manure management

    Argument
    --------
    n (piece/year) : float
        number of head of livestock species
    nex (kg/piece/year) : float
        annual average n excretion per head of species
    awms (kg/kg) : float
        fraction of total annual nitrogen excretion for each livestock
    frac_gas (kg/kg) : float
        fraction of managed manure nitrogen for livestock that volatilises as NH3 and NOx in the manure managemnet system

    Returns
    -------
    VALUE: float
        n_volatilization (kg/yearJ)
    """
    n_volatilization = (n * nex * awms) * frac_gas
    return n_volatilization


def n_leaching(n, nex, awms, frac_leach):
    """
    Equation 10.27

    N losses due to leaching from manure management

    Argument
    --------
    n (piece/year) : float
        number of head of livestock species
    nex (kg/piece/year) : float
        annual average n excretion per head of species
    awms (kg/kg) : float
        fraction of total annual nitrogen excretion for each livestock
    frac_leach (kg/kg) : float
        fraction of managed manure nitrogen for livestock that is leached from the manure managemnet system

    Returns
    -------
    VALUE: float
        n_leaching (kg/year)
    """
    n_leaching = (n * nex * awms) * frac_leach
    return n_leaching


def n2o_g(n_volatilization, ef4):
    """
    Equation 10.28

    indirect N2O emissions due to volatilisation of N from manure management

    Argument
    --------
    n_volatilization (kg/year) : float
        n losses due to volatilization
    ef4 (kg/kg) : float
        emission factor for N2O emissions from atmospheric deposition of nitrogen on soils and water

    Returns
    -------
    VALUE: float
        n2o_g (kg/year)
    """
    n2o_g = n_volatilization * ef4 * 44 / 28
    return n2o_g


def n2o_l(n_leaching, ef5):
    """
    Equation 10.29

    indirect N2O emissions due to leaching from manure management

    Argument
    --------
    n_leaching(kg/year) : float
        n losses due to leaching
    ef5 (kg/kg) : float
        emission factor for N2O emissions from nitrogen leaching

    Returns
    -------
    VALUE: float
        n2o_l (kg/year)
    """
    n2o_l = n_leaching * ef5 * 44 / 28
    return n2o_l


# TODO: use animal type as argument and merge functions into one (use startswith statements from sequneces)
def dmi_calve_(ne_mf, bw):
    """
    Equation 10.17

    Estimation of dry matter intake for calves

    Argument
    --------
    ne_mf (MJ/kg) : float
        estimated dietary net energy concentration of diet
    bw (kg/piece) : float
        live body weight

    Returns
    -------
    VALUE: float
        dmi (kg/day)
    """
    dmi = (
        bw**0.75 * (0.0582 * ne_mf - 0.00266 * ne_mf**2 - 0.1128) / (0.239 * ne_mf)
    )
    return dmi


def dmi_growing_(ne_mf, bw):
    """
    Equation 10.18

    ESTIMATION OF DRY MATTER INTAKE FOR GROWING CATTLE

    Argument
    --------
    ne_mf (MJ/kg) : float
        estimated dietary net energy concentration of diet
    bw (kg/piece) : float
        live body weight

    Returns
    -------
    VALUE: float
        dmi (kg/day)
    """
    dmi = (
        bw**0.75 * (0.0582 * ne_mf - 0.00266 * ne_mf**2 - 0.0869) / (0.239 * ne_mf)
    )
    return dmi


def dmi_steer_(bw):
    """
    Equation 10.18a1

    ESTIMATION OF DRY MATTER INTAKE FOR STEERS AND BULLS

    Argument
    --------
    bw (kg/piece) : float
        live body weight

    Returns
    -------
    VALUE: float
        dmi (kg/day)
    """
    dmi = 3.83 + 0.0143 * bw * 0.96
    return dmi


def dmi_heifer_(bw):
    """
    Equation 10.18a2

    ESTIMATION OF DRY MATTER INTAKE FOR HEIFERS

    Argument
    --------
    bw (kg/piece) : float
        live body weight

    Returns
    -------
    VALUE: float
        dmi (kg/day)
    """
    dmi = 3.184 + 0.01536 * bw * 0.96
    return dmi


def dmi_lactating_(bw, fcm):
    """
    Equation 10.18b

    ESTIMATION OF DRY MATTER INTAKE FOR LACTATING DAIRY COWS

    Argument
    --------
    bw (kg/piece) : float
        live body weight
    fcm (kg/day) : float
        fat corrected milk

    Returns
    -------
    VALUE: float
        dmi_lactating (kg/day)
    """
    dmi = 0.0185 * bw + 0.305 * fcm
    return dmi


def fcm(milk, fat):
    """
    Equation added. Parameter in eq. 10.18

    Fat corrected milk

    Argument
    --------
    milk (kg/piece/day) : float
        milk yield
    fat (kg/day) : float
        fat content

    Returns
    -------
    VALUE: float
        fcm (kg/day)
    """
    fcm = 3.5 * (0.4324 * milk + 16.216 * (fat))
    return fcm


def e(ef, n):
    """
    Equation 10.19 (Tier 1)

    ENTERIC FERMENTATION EMISSIONS FROM A LIVESTOCK CATEGORY

    Argument
    --------
    ef (kg/piece/year) : float
        emission factor for the defined livestock population
    n (piece/year) : float
        the number of head of livestock species

    Returns
    -------
    VALUE: float
        e (Gg/year)
    """
    e = ef * n / (10**6)
    return e


def ef_atier2_(ge, ym):
    """
    Equation 10.21 (Tier 2)

    METHANE EMISSION FACTORS FOR ENTERIC FERMENTATION FROM A LIVESTOCK CATEGORY

    Argument
    --------
    ge (MJ/piece/year) : float
        gross energy intake
    ym (MJ/MJ) : float
        methane conversion factor, as ratio of gross energy in feed converted to methane

    Returns
    -------
    VALUE: float
        ef (kg/piece/year)
    """
    ef = ge * ym * 365 / 55.65
    return ef


def ef_btier2_(dmi, my):
    """
    Equation 10.21a (Tier 2, simplified)

    METHANE EMISSION FACTORS FOR ENTERIC FERMENTATION FROM A LIVESTOCK CATEGORY

    Argument
    --------
    dmi (kg/piece/day) : float
        dry matter intake
    my (g/kg) : float
        methane yield

    Returns
    -------
    VALUE: float
        ef_a (kg(piece/year)
    """
    ef = dmi * my / 1000 * 365
    return ef


def ch4_mm(n, vs, awms, ef):
    """
    Equation 10.22 (Tier 1)

    METHANE EMISSION FACTORS FOR ENTERIC FERMENTATION FROM A LIVESTOCK CATEGORY

    Argument
    --------
    n (piece/year) : float
        number of head of livestock species
    vs (kg/piece/year) : float
        annual average vs excretion per head of species
    awms (piece/piece) : float
        fraction of total annual vs for each livestock species
    ef (g/kg) : float
        emission factor for direct CH4 emissions from manure management system

    Returns
    -------
    VALUE: float
        ch4_mm (kg(piece/year)
    """
    ch4_mm = (n * vs * awms * ef) / 1000
    return ch4_mm


def vs_tier1_(vs_rate, tam):
    """
    Equation 10.22a (Tier 1).

    Annual VS excretion rate

    Argument
    --------
    vs_rate (kg/1000kg/day) : float
        default vs excretion rate
    tam (kg/piece) : float
        typical animal mass for livestock category

    Returns
    -------
    VALUE: float
        vs (kg/piece/year)
    """
    vs = vs_rate * tam / 1000 * 365
    return vs


def ch4_other_animals(n, ef_others):
    """
    Equation added (Tier 1).

    CH4 emissions from manure for other animals (deer, reindeer, rabbit, fear-bearing, ostrich)

    Argument
    --------
    n (piece/year) : float
        number of head of livestock species
    ef_others (kg/piece/year) : float
        emission factor for direct CH4 emissions from manure for other animals

    Returns
    -------
    VALUE: float
        ch4_other_animals (kg(piece/year)
    """
    ch4_other_animals = n * ef_others
    return ch4_other_animals


def ef_mm(vs, b0, mcf, awms):
    """
    Equation 10.23 (Tier 2).

    CH4 EMISSION FACTOR FROM MANURE MANAGEMENT

    Argument
    --------
    vs (kg/piece/day) : float
        daily volatile solid excreted for livestock category
    b0 (m3/kg) : float
        maximum methane producing capacity for manure produced by livestock
    mcf (m3/m3) : float
        methane conversion factors for each manure management system
    awms (piece/piece) : float
        fraction of livestock category's manure handled using animal waste management system

    Returns
    -------
    VALUE: float
        ef_mm (kg/piece/year)
    """
    ef_mm = vs * 365 * b0 * 0.67 * mcf * awms
    return ef_mm


def vs_tier2_(ge, de, ue, ash):
    """
    Equation 10.24 (Tier 2).

    VOLATILE SOLID EXCRETION RATES

    Argument
    --------
    ge (MJ/piece/day) : float
        gross energy intake
    de (MJ/MJ) : float
        digestibility of the feed (ratio)
    ue (MJ/MJ) : float
        urinary energy fraction
    ash (kg/kg) : float
        the ash content of feed calculated as a fraction of the dry matter feed intake

    Returns
    -------
    VALUE: float
        vs (kg/piece/day)
    """
    vs = ge * (1 - de) + (ue * ge) * (1 - ash) / 18.45
    return vs


def n_mms(n, nex, awms, n_cdg, frac_loss, n_bedding):
    """
    Equation 10.34 (Tier 1).

    M ANAGED MANURE N AVAILABLE FOR APPLICATION TO MANAGED SOILS , FEED , FUEL OR CONSTRUCTION USES

    Argument
    --------
    n (piece/year) : float
        number of head of livestock species/category in the country
    nex (kg/piece/year) : float
        annual average N excretion per animal of species/category in the country
    awms (kg/kg) : float
        fraction of total annual nitrogen excretion for each livestock species/category that is managed in manure management system in the country
    n_cdg (kg/year) : float
        amount of nitrogen from co-digestates added to biogas plants such as food wastes or purpose grown crops


    Returns
    -------
    VALUE: float
        n_mns (kg/piece/day)
    """
    n_mms = (n * nex * awms + n_cdg) * (1 - frac_loss) + (n * awms * n_bedding)
    return n_mms


def frac_loss(frac_gas, frac_leachs, frac_n2ms, ef3):
    """
    Equation 10.34a (Tier 1).

    FRACTION OF MANAGED MANURE N LOST PRIOR TO APPLICATION TO MANAGED SOILS FOR THE PRODUCTION OF FEED, FUEL OR FOR CONSTRUCTION USES

    Argument
    --------
    frac_gas (kg/kg) : float
        traction of managed manure nitrogen for livestock category that is lost by volatilisation in the manure management system
    frac_leachs (kg/kg) : float
        fraction of managed manure nitrogen for livestock category that is lost in the manure management system S by leaching or run-off
    frac_n2ms (kg/kg) : float
        fraction of total annual nitrogen excretion for each livestock species/category that is managed in manure management system in the country
    ef3 (kg/kg) : float
        emission factor for direct N2O emissions from manure management system


    Returns
    -------
    VALUE: float
        frac_loss (kg/kg)
    """
    frac_loss = frac_gas + frac_leachs + frac_n2ms + ef3
    return frac_loss


def frac_n2ms(r_n2, ef3):
    """
    Equation 10.34b (Tier 1).

    FESTIMATION OF FRAC_N2MS

    Argument
    --------
    r_n2 (kg/kg) : float
        Ratio of N2 : N2O emission
    ef3 (kg/kg) : float
        emission factor for direct N2O emissions from manure management system in the country

    Returns
    -------
    VALUE: float
        frac_n2ms (kg/kg)
    """
    frac_n2ms = r_n2 * ef3
    return frac_n2ms
