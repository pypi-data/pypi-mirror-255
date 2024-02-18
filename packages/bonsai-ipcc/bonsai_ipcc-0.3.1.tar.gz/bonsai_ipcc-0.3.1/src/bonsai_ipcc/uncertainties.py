"""
Chapter 3 (Uncertainties) of Volume 1 (General Guidance and Reporting)

Min and max values provided by the IPCC guidelines are considerred to be
2.5th and 97.5th percentile, respectively (p 3.9).

Two ways of uncertainty propagation are implemented: analytical error propagation and Monte Carlo simulation.
If analytical error propagation is choosen, asymmetric parameter ranges are transferred by a simple rule of thumb into symmetric ranges.
If Monte Carlo, propability distributions can be determined automatically in regard to the properties of the parameter (by "check").
"""

import logging

import numpy as np
from scipy.stats import beta, norm, truncexpon, truncnorm
from uncertainties import ufloat

logger = logging.getLogger(__name__)


def two_side_trunc(mobs, sobs, vmin, vmax):
    """Helper function for adjusting mean and sd for two-sided truncated normal distribution.

    Given observed mean m, std-dev s, lower and upper bounds,
    vmin and vmax, (all floats) such that:
    vmin < mobs < vmax, and
    0.0 < sobs < min(mobs - vmin, vmax - mobs)

    Argument
    --------
    mobs : float
        observed mean
    sobs : float
        observed standard deviation
    vmin : float
        absolut minimum
    vmax : float
        absolut maximum

    Returns
    -------
    VALUES: float, float
        adjusted mean, adjusted standard deviation
    """
    if not isinstance(mobs, float):
        raise TypeError(f"Observed mean is not float: {type(mobs)}")
    if not isinstance(sobs, float):
        raise TypeError(f"Observed std-dev is not float: {type(sobs)}")
    if not isinstance(vmin, float):
        raise TypeError(f"Observed lower bound is not float: {type(vmin)}")
    if not isinstance(vmax, float):
        raise TypeError(f"Observed upper bound is not float: {type(vmax)}")

    if mobs <= vmin:
        raise ValueError(
            f"Observed mean is not larger than " f"lower bound: {mobs} <= {vmin}"
        )
    if vmax <= mobs:
        raise ValueError(
            f"Observed mean is not lower than " f"lower bound: {vmax} <= {mobs}"
        )
    if sobs <= 0:
        raise ValueError(f"Observed std-dev is not positive: {mobs}")
    if (sobs >= (mobs - vmin)) and ((mobs - vmin) < (vmax - mobs)):
        raise ValueError(
            f"Observed std-dev is too large: "
            f"{sobs} > {mobs - vmin}\nWhile mean closer "
            f"to lower bound: {(mobs - vmin)} < "
            f"{(vmax - mobs)}"
        )
    if (sobs >= (vmax - mobs)) and ((mobs - vmin) < (vmax - mobs)):
        raise ValueError(
            f"Observed std-dev is too large: "
            f"{sobs} > {vmax - mobs}\nWhile mean closer "
            f"to upper bound: {(mobs - vmin)} > "
            f"{(vmax - mobs)}"
        )

    if (
        (mobs - vmin) < (vmax - mobs)
        and sobs / (mobs - vmin) > 0.3
        and sobs / (mobs - vmin) < 1.167 - 1.69 * (mobs - vmin)
    ):
        # print('truncated left')
        mtmp, stmp = one_side_trunc(mobs - vmin, sobs)
        return vmin + mtmp, stmp
    elif (
        (mobs - vmin) > (vmax - mobs)
        and sobs / (vmax - mobs) > 0.3
        and sobs / (vmax - mobs) < 1.167 - 1.69 * (vmax - mobs)
    ):
        # print('truncated right')
        mtmp, stmp = one_side_trunc(vmax - mobs, sobs)
        return vmax - mtmp, stmp
    else:
        # print('non-truncated')
        return mobs, sobs


def one_side_trunc(mobs, sobs):
    """Helper function for adjusting mean and sd for one-sided truncated normal distribution.

    Given observed mean m > 0.0 and std-dev, 0.0 < s < m, return
    parameter mean and std-dev of one-sided truncated Gaussian
    distribution X, with X > 0.0

    Rodrigues 2015, Maximum-Entropy Prior Uncertainty and Correlation of Statistical Economic Data:
    Supplementary Informatiom.

    Argument
    --------
    mobs : float
        observed mean
    sobs : float
        observed standard deviation

    Returns
    -------
    VALUES: float, float
        adjusted mean, adjusted standard deviation
    """

    if not isinstance(mobs, float):
        raise TypeError(f"Observed mean is not float: {type(mobs)}")
    if not isinstance(sobs, float):
        raise TypeError(f"Observed std-dev is not float: {type(sobs)}")

    if mobs <= 0:
        raise ValueError(f"Observed mean is not positive: {mobs}")
    if sobs <= 0:
        raise ValueError(f"Observed std-dev is not positive: {mobs}")
    if sobs >= mobs:
        raise ValueError(
            f"Observed std-dev is not smaller than " f"observed mean: {sobs} > {mobs}"
        )

    cm1 = 0.937492
    cm2 = 1.78863
    cm3 = 7.13173
    cm4 = 5.42261
    cg1 = 0.468838
    cg2 = 0.118555
    cg3 = 0.00235939
    cs1 = 0.546626
    cs2 = 0.439319
    cs3 = 1.83447
    cr1 = 0.83179
    cr2 = 0.617251
    cr3 = 6.3836

    def gm(u):
        tmp0 = cm4 + cm3 * abs(u - cm1) ** cm2
        tmp1 = cg3 / cg2 * norm.pdf((u - cg1) / cg2)
        res = 1.0 - (1.0) / (1.0 - u) * np.exp(-(1.0 - u) * tmp0) + tmp1
        return res

    def gs(u):
        return (1.0 - u) * cs3 / cs2 * norm.pdf((u - cs1) / cs2)

    def gr(u):
        return (1.0 - u) * cr3 / cr2 * norm.pdf((u - cr1) / cr2) - 1.0

    uobs = sobs / mobs
    if uobs < 0.3:
        return mobs, sobs
    else:
        pass

    mpar = mobs * gm(uobs)

    if uobs <= 0.8:
        spar = sobs / np.sqrt(gs(uobs))
    else:
        spar = -sobs * gm(uobs) / np.sqrt(gm(uobs) * gr(uobs))

    return mpar, spar


def analytical(min95, max95):
    """
    Creates ufloat value to be used in error propagation.
    Simple asumption of normal distribution.

    Argument
    --------
    min : float
        2.5th percentile
    max : float
        97.5th percentile

    Returns
    -------
    VALUE: ufloat
    """

    mean = (min95 + max95) / 2
    sd = (max95 - mean) / 1.96

    return ufloat(mean, sd)


def monte_carlo(
    min95,
    max95,
    default=None,
    abs_min=None,
    abs_max=None,
    size=1000,
    distribution="check",
):
    """
    Creates numpy array of random numbers to be used in monte carlo simulation.
    Choices of different distributions possible.

    Argument
    ---------
    min : float
        2.5th percentile
    max : float
        97.5th percentile
    default : float
        default value (mean)
    abs_min : float
        theoretic lower bound of parameter
    abs_max : float
        theoretic upper bound of parameter
    distribution : str
        Specifies type of density distribution.
        'normal', 'lognormal', 'truncnormal', 'uniform', 'check' for automatized choice
    size : int
         Number of random numbers to be generated.

    Returns
    -------
    VALUE: numpy.array
    """

    if distribution == "normal":
        mean = (min95 + max95) / 2
        sd = (max95 - mean) / 1.96
        return np.random.normal(mean, sd, size)

    elif distribution == "lognormal":
        if min95 == 0 and max95 == 0:
            return 0
        else:
            mean = (np.log(min95) + np.log(max95)) / 2
            sd = (np.log(max95) - mean) / 1.96
            return np.random.lognormal(mean, sd, size)

    elif distribution == "truncnormal":
        if min95 == 0 and max95 == 0:
            return 0
        else:
            mean = (min95 + max95) / 2
            sd = (max95 - mean) / 1.96
            a, b = (min95 - mean) / sd, (max95 - mean) / sd
            return truncnorm.rvs(a, b, size=size, loc=mean, scale=sd)

    elif distribution == "uniform":
        return np.random.uniform(low=abs_min, high=abs_max, size=size)

    # Do some checks and chose the distribution
    elif distribution == "check":
        if (
            not isinstance(min95, (int, float, np.int64, np.float64))
            and not isinstance(max95, (int, float, np.int64, np.float64))
            and not isinstance(default, (int, float, np.int64, np.float64))
        ):
            logger.info("uniform distribution")
            return np.random.uniform(low=abs_min, high=abs_max, size=size)

        else:
            # adjust if mean equals the upper bound
            mean = (max95 + min95) / 2
            sd = (max95 - min95) / (2 * 1.96)

            if (sd == 0.0 or mean == 0.0) and mean != abs_max:
                logger.info("no uncertainty in value")
                return mean

            elif sd == 0.0 and mean == 0.0:
                logger.info("no uncertainty in value")
                return mean

            elif abs_min == 0.0 and abs_max == np.inf:
                if min95 == abs_min:
                    min95 = mean * 0.99  # otherwise numeric issues
                logger.info("lognormal distribution")
                mean = (np.log(min95) + np.log(max95)) / 2
                sd = (np.log(max95) - mean) / 1.96
                return np.random.lognormal(mean, sd, size)

            elif abs_min == 0.0 and abs_max == 1.0:
                if max(sd / (mean - abs_min), sd / (abs_max - mean)) <= 0.3:
                    logger.info("normal distribution, lower uncertainty")
                    return np.random.normal(mean, sd, size)
                elif (
                    max(sd / (mean - abs_min), sd / (abs_max - mean)) == 1.0
                    and mean > 0.7
                ):
                    logger.info("truncated exponential distribution (inv)")
                    return 1 - truncexpon(
                        b=(abs_max - abs_min) / sd, loc=abs_min, scale=sd
                    )
                elif (
                    max(sd / (mean - abs_min), sd / (abs_max - mean)) == 1.0
                    and mean < 0.3
                ):
                    logger.info("truncated exponential distribution")
                    return truncexpon(b=(abs_max - abs_min) / sd, loc=abs_min, scale=sd)
                elif (
                    max(sd / (mean - abs_min), sd / (abs_max - mean)) > 0.3
                    and max(sd / (mean - abs_min), sd / (abs_max - mean)) <= 0.8
                    and (mean < 0.3 or mean > 0.7)
                ):
                    logger.info(
                        "truncated normal distribution with adjusting based on Rodriques 2015 (moderate)"
                    )
                    a = (abs_min - mean) / sd
                    b = (abs_max - mean) / sd
                    new_mean, new_sd = two_side_trunc(mean, sd, abs_min, abs_max)
                    a = (abs_min - new_mean) / new_sd
                    b = (abs_max - new_mean) / new_sd
                    return truncnorm.rvs(a, b, size=size, loc=new_mean, scale=new_sd)
                elif max(sd / (mean - abs_min), sd / (abs_max - mean)) > 0.8 and (
                    mean <= 0.3 or mean > 0.7
                ):
                    logger.info(
                        "truncated normal distribution with adjusting based on Rodriques 2015 (high)"
                    )
                    a = (abs_min - mean) / sd
                    b = (abs_max - mean) / sd
                    new_mean, new_sd = two_side_trunc(mean, sd, abs_min, abs_max)
                    a = (abs_min - new_mean) / new_sd
                    b = (abs_max - new_mean) / new_sd
                    return truncnorm.rvs(a, b, size=size, loc=new_mean, scale=new_sd)
                elif (
                    max(sd / (mean - abs_min), sd / (abs_max - mean)) > 0.3
                    and max(sd / (mean - abs_min), sd / (abs_max - mean)) <= 0.8
                    and (mean > 0.3 and mean <= 0.7)
                ):
                    logger.info("truncated normal distribution")
                    a = (abs_min - mean) / sd
                    b = (abs_max - mean) / sd
                    return truncnorm.rvs(a, b, size=size, loc=mean, scale=sd)
                elif (
                    max(sd / (mean - abs_min), sd / (abs_max - mean)) > 0.8
                    and max(sd / (mean - abs_min), sd / (abs_max - mean)) < 1.0
                    and (mean > 0.3 and mean <= 0.7)
                ):
                    logger.info("beta distribution (Danger zone 2 needs adjustment)")
                    a = (((1 - mean) / (sd**2)) - (1 / mean)) * mean**2
                    b = a * ((1 / mean) - 1)
                    return beta.rvs(a, b, size=size)
            else:
                raise NotImplementedError("Rule is required")
                return
