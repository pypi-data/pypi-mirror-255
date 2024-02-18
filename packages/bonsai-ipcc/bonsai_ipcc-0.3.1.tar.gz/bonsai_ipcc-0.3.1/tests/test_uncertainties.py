import logging
import sys
from collections import namedtuple

import numpy as np
import pytest

from bonsai_ipcc import uncertainties

LOGGER = logging.getLogger(__name__)


check = namedtuple("check", "default min95 max95 abs_min abs_max")

check1 = check(
    default=1.0, min95=0.9, max95=1.0, abs_min=0.0, abs_max=1.0
)  # moderate adjustment of truncnorm right
check2 = check(
    default=0.5, min95=0.4, max95=0.6, abs_min=0.0, abs_max=1.0
)  # normal disttribution
check3 = check(
    default=0.01, min95=0.0, max95=0.6, abs_min=0.0, abs_max=2.0
)  # not implemented
check4 = check(
    default=0.0, min95=0.0, max95=0.1, abs_min=0.0, abs_max=1.0
)  # moderate adjustment of truncnorm left
check5 = check(
    default=0.5, min95=0.2, max95=0.8, abs_min=0.0, abs_max=1.0
)  # truncated normal (Danger zone 1)


@pytest.mark.skipif(
    sys.platform != "darwin",
    reason="Skip test if not on Mac OS, sometimes fails because of random numbers",
)
def test_mc_check1(caplog):
    # rule that is implemented to deal with conflicting information
    mean = (check1.max95 + check1.min95) / 2
    sd = (check1.max95 - check1.min95) / (2 * 1.96)

    # expected values
    exp_mean = mean
    exp_sd = sd
    exp_abs_min = check1.abs_min
    exp_abs_max = check1.abs_max

    caplog.set_level(logging.INFO)
    # calc observe mean, abs_min, abs_max
    rand_numbers = uncertainties.monte_carlo(
        min95=check1.min95,
        max95=check1.max95,
        default=mean,
        abs_min=check1.abs_min,
        abs_max=check1.abs_max,
        size=1000,
        distribution="check",
    )
    obs_mean = np.mean(rand_numbers)
    obs_sd = np.std(rand_numbers)
    obs_abs_min = np.min(rand_numbers)
    obs_abs_max = np.max(rand_numbers)

    assert abs((obs_mean - exp_mean) / exp_mean) < 0.05
    assert abs((obs_sd - exp_sd) / exp_sd) < 0.05
    assert obs_abs_min > exp_abs_min
    assert obs_abs_max < exp_abs_max
    assert (
        "truncated normal distribution with adjusting based on Rodriques 2015 (moderate)"
        in caplog.text
    )


@pytest.mark.skipif(
    sys.platform != "darwin",
    reason="Skip test if not on Mac OS, sometimes fails because of random numbers",
)
def test_mc_check2(caplog):
    # rule that is implemented to deal with conflicting information
    mean = (check2.max95 + check2.min95) / 2
    sd = (check2.max95 - check2.min95) / (2 * 1.96)

    # expected values
    exp_mean = mean
    exp_sd = sd
    exp_abs_min = check2.abs_min
    exp_abs_max = check2.abs_max

    caplog.set_level(logging.INFO)
    # calc observe mean, abs_min, abs_max, sd
    rand_numbers = uncertainties.monte_carlo(
        min95=check2.min95,
        max95=check2.max95,
        default=mean,
        abs_min=check2.abs_min,
        abs_max=check2.abs_max,
        size=1000,
        distribution="check",
    )
    obs_mean = np.mean(rand_numbers)
    obs_sd = np.std(rand_numbers)
    obs_abs_min = np.min(rand_numbers)
    obs_abs_max = np.max(rand_numbers)

    assert abs((obs_mean - exp_mean) / exp_mean) < 0.05
    assert abs((obs_sd - exp_sd) / exp_sd) < 0.05
    assert obs_abs_min > exp_abs_min
    assert obs_abs_max < exp_abs_max
    assert "normal distribution, lower uncertainty" in caplog.text


def test_mc_check3():
    # rule that is implemented to deal with conflicting information
    mean = (check1.max95 + check1.min95) / 2
    sd = (check1.max95 - check1.min95) / (2 * 1.96)

    with pytest.raises(NotImplementedError):
        rand_numbers = uncertainties.monte_carlo(
            min95=check3.min95,
            max95=check3.max95,
            default=mean,
            abs_min=check3.abs_min,
            abs_max=check3.abs_max,
            size=1000,
            distribution="check",
        )


@pytest.mark.skipif(
    sys.platform != "darwin",
    reason="Skip test if not on Mac OS, sometimes fails because of random numbers",
)
def test_mc_check4(caplog):
    # rule that is implemented to deal with conflicting information
    mean = (check4.max95 + check4.min95) / 2
    sd = (check4.max95 - check4.min95) / (2 * 1.96)

    # expected values
    exp_mean = mean
    exp_sd = sd
    exp_abs_min = check4.abs_min
    exp_abs_max = check4.abs_max

    caplog.set_level(logging.INFO)
    # calc observe mean, abs_min, abs_max
    rand_numbers = uncertainties.monte_carlo(
        min95=check4.min95,
        max95=check4.max95,
        default=mean,
        abs_min=check4.abs_min,
        abs_max=check4.abs_max,
        size=1000,
        distribution="check",
    )
    obs_mean = np.mean(rand_numbers)
    obs_sd = np.std(rand_numbers)
    obs_abs_min = np.min(rand_numbers)
    obs_abs_max = np.max(rand_numbers)

    assert abs((obs_mean - exp_mean) / exp_mean) < 0.05
    assert abs((obs_sd - exp_sd) / exp_sd) < 0.05
    assert obs_abs_min > exp_abs_min
    assert obs_abs_max < exp_abs_max
    assert (
        "truncated normal distribution with adjusting based on Rodriques 2015 (moderate)"
        in caplog.text
    )


@pytest.mark.skipif(
    sys.platform != "darwin",
    reason="Skip test if not on Mac OS, sometimes fails because of random numbers",
)
def test_mc_check5(caplog):
    # rule that is implemented to deal with conflicting information
    mean = (check5.max95 + check5.min95) / 2
    sd = (check5.max95 - check5.min95) / (2 * 1.96)

    # expected values
    exp_mean = mean
    exp_sd = sd
    exp_abs_min = check5.abs_min
    exp_abs_max = check5.abs_max

    caplog.set_level(logging.INFO)
    # calc observe mean, abs_min, abs_max
    rand_numbers = uncertainties.monte_carlo(
        min95=check5.min95,
        max95=check5.max95,
        default=mean,
        abs_min=check5.abs_min,
        abs_max=check5.abs_max,
        size=1000,
        distribution="check",
    )
    obs_mean = np.mean(rand_numbers)
    obs_sd = np.std(rand_numbers)
    obs_abs_min = np.min(rand_numbers)
    obs_abs_max = np.max(rand_numbers)

    assert abs((obs_mean - exp_mean) / exp_mean) < 0.05
    assert abs((obs_sd - exp_sd) / exp_sd) < 0.05
    assert obs_abs_min > exp_abs_min
    assert obs_abs_max < exp_abs_max
    assert "truncated normal distribution" in caplog.text
