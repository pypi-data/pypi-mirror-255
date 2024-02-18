# Contributing

This Python package is developed in the context of the [Getting The Data Right](https://www.plan.aau.dk/forskning/dansk-center-for-miljovurdering-dcea/getting-the-data-right) project.


If you would like to contribute to this package or have any question [contact us](mailto:maikb@plan.aau.dk).
Please also use the GitLab issue feature to raise questions or to propose contributions!

Ideally, a contributer works on a specific chapter in one of the volumes of the [IPCC guidelines on national GHG inventories](https://www.ipcc-nggip.iges.or.jp/public/2019rf/index.html).
The volumes are the following:
- energy
- industry
- agriculture
- waste

Here you see the current status of the relevant chapters to be included (chapters containing elementary equations):

| Volume      | Chapter              |  Comment        | Status      |
| :-----------| :------------------- | :-------------- | :---------: |
| `energy`      | `stationary`       |  Vol. 2, Ch. 2  | Open        |
| `energy`      | `mobile`           |  Vol. 2, Ch. 3  | Open        |
| `energy`      | `fugitive`         |  Vol. 2, Ch. 4  | Open        |
| `energy`      | `storage`          |  Vol. 2, Ch. 5  | Open        |
| `industry`    | `mineral`          |  Vol. 3, Ch. 2  | In Progress |
| `industry`    | `chemical`         |  Vol. 3, Ch. 3  | In Progress |
| `industry`    | `metal`            |  Vol. 3, Ch. 4  | Open        |
| `industry`    | `nonenergy`        |  Vol. 3, Ch. 5  | Open        |
| `industry`    | `electronics`      |  Vol. 3, Ch. 6  | Open        |
| `industry`    | `ozone_depleting`  |  Vol. 3, Ch. 7  | Open        |
| `industry`    | `other`            |  Vol. 3, Ch. 8  | Open        |
| `agriculture` | `generic`          |  Vol. 4, Ch. 2  | In Progress |
| `agriculture` | `livestock_manure` |  Vol. 4, Ch. 10 | Completed   |
| `agriculture` | `soils`            |  Vol. 4, Ch. 11 | Completed   |
| `agriculture` | `wood_products`    |  Vol. 4, Ch. 12 | Open        |
| `waste`       | `waste_generation` |  Vol. 5, Ch. 2  | Completed   |
| `waste`       | `swd`              |  Vol. 5, Ch. 3  | Completed   |
| `waste`       | `biological`       |  Vol. 5, Ch. 4  | Completed   |
| `waste`       | `incineration`     |  Vol. 5, Ch. 5  | Completed   |
| `waste`       | `wastewater`       |  Vol. 5, Ch. 6  | Completed   |

> **_NOTE:_** The aim of this package is to be technology specific. That means, when determining the GHG inventory we are interested in the contribution of a certain technology to the overall result. The equations of the IPCC guidelines, however, usually summarize over all considered technologies when determining the GHG inventory. Thus, the contributer is required to adopt those equations.

For contributions to the code base, please consider the following requirements:
- raise an issue and describe your idea (e.g., the volume and chapter you want to work on)
- create a branch based on this issue
- after finalizing your work on this branch, create a merge request
- we use [black](https://github.com/psf/black/) and [isort](https://github.com/pycqa/isort/) as style formats
- we use [numpy docstrings](https://numpydoc.readthedocs.io/en/latest/format.html)

Before creating a merge request, make sure all tests pass locally. To do so, you can run the follwing [tox](https://tox.wiki/en/latest/index.html) command in the root of your local repository:
```
tox --  -vv --black
```

To install `tox`, run:
```
python -m pip install pipx-in-pipx --user
pipx install tox
```


## Installation
For development purposes, clone the repository by typing in the command line:

```bash
git clone git@gitlab.com:bonsamurais/bonsai/util/ipcc.git
cd bonsai_ipcc/
pip install -e .
```

## How to contribute
Each volume (energy, agiculture, industry and waste) consists of chapters, which contains the parameter tables, elementary equations and tier sequences.

```python
from bonsai_ipcc import IPCC
my_ipcc = IPCC()
my_ipcc.<volume>.<chapter>.parameter.<table>
my_ipcc.<volume>.<chapter>.elementary.<equation>
my_ipcc.<volume>.<chapter>.sequence.<tier_method>
```

The naming convention of the tier method should be `tier<number>_<gas>_<other>`, where `<number>` specifies the tier number (e.g., "1" or "2a"), `<gas>` is the greenhouse gas (e.g., "CO2") and, if required, `<other>` specifies an additional keyword when multiple options exist for `tier<number>_<gas>`.
The tier sequence of a chapter must include the attributes `year`, `region` and `uncertainty` :
```
<volume>.<chapter>.sequence.<tier_method>(year,region,<product>,<technology>,uncertainty)
```

The additional attributes `<technology>` and `<product>` depend on the specific chapter. For the chapter incineration in the waste volume, `waste_type` is used for `<product>` and `incin_type` is used for `<technology>`.
Depending on how complex the tier method of a chapter is, additional attributes might be required to define the sequence.

### 1. Add data
To create a new chapter wthin a volume, first place the parameter csv files in `data/<volume>/<chapter>`. Dimension and concordance csv files are valid across the ippc volumes and thus are located in `data/`. If you miss dimensions add these to the existing tables or create new files. The following conventions are valid:

- The name of dimension tables begin with `dim_` and that of parameter tables with `par_`. Names should be unique.

- Dimension tables have a mandatory `code` field. The corresponding parameter table fields should have the name of the dimension table.

- Parameter tables have mandatory fields `value` and `unit`. Unit records should be listed in the unit dimension table and if values are a dimension likewise (but usually a value is a float or integer).

> **_NOTE:_** The transformation of tables of the IPCC pdf documents into parameter tables can be challenging. Especially the choice of dimensions requires well-thought decisions. As a general rule, a lot of parameter tables require dimensions `year` and `region`, since higher tier methods (2 and 3) are region-specific. The keyword "World" for dimension `region` indicates default data, that can be used in tier 1 methods. For higher tiers, country-specific values may be required. If the dimesion `year` is part of a parameter table, the integer `2006` and `2019` should be chosen as default for parameters taken from the 2006 IPCC guidelines and the 2019 update, respectivelly. These default parameter values, i.e., for emission factors, may be also valid in other years. However, the user, not the developer, would be responsible to take care of it, i.e. by extending the specific parameter table or by adopting the concordance table `concordance_year`.

### 2. Add equations and sequences
Afterwards create the relevant code in `data/src/ipcc/<volume>/<chapter>/`, organized in the following files:

- `data.py` where instances of dimension and parameter are created.

- `elementary.py` and `sequence.py`where all elementary equations and equation sequences are listed

- `__init__.py` where relevant methods and attributes are imported.

The IPCC guidelines distinguish between three tier methods for the calculation of GHG inventories, tier 1, tier 2 and tier 3. The first step of such a sequence is always reading a parameter table. However, these three different tiers may differ in the following manner:
- the dimension `region` of parameter tables may require country-specific entries (tier 2 and tier 3)
- the dimension `<technology>` of paramter tables may require plant-specific entries (tier 3)
- the first parameter table of a sequence may differ among tiers
- different elementary equations (from `elementary.py`) might be required to specify higher tiers

> **_NOTE:_** See the volume waste for the boilerplate code.

### 3. Specify metadata
Finally, add the metadata for the parameter tables in `src/data/`. The metadata shall be listed in the `ipcc.datapackage.yaml` file. Use the [frictionless](https://pypi.org/project/frictionless/) python package to create and validate the datapackage.

> **_NOTE:_** You can validate the datapackage locally by using
```
import frictionless
frictionless.validate("src/data/ipcc.datapackage.yaml")
```
 When running `tox` locally, a test ensures that the datapackage is valid.
