import sys
from importlib.resources import files

import pytest
from frictionless import validate

source = files("bonsai_ipcc.data").joinpath("ipcc.datapackage.yaml")


def test_datapackage():
    report = validate(source)
    assert report.valid == True
