# Changelog

## Version 0.1.3

- implement all required parameter, dimension tables in the package, even though the IPCC guidelines do not provide data
- add sequences with higher tiers (2 and 3) for volume waste
- fix bugs in csv tables by using frictionless python package
- update folder structure of parameter, concordance and dimension tables
- add metadata for volume waste (ipcc.datapackage.yaml)

## Version 0.1.4

- update documentation
- add tutorials
- add test for swd (comparison with IPCC excel result)
- remove non-IPCC related data

## Version 0.1.5

- Chapter `Livestock` of Volume `Agriculture` implemented
- test for frictionless validation of datapackages
- refactoring of bonsai_ipcc/sequence.py
- signature of tier function added as first steps of the sequence
- pdf documention

## Version 0.1.9

- fix path for data when installing package
- fix CI pipeline

## Version 0.1.10

- clean namespaces
- add test for agri-livestock_manure
- renaming of chapters and modules

## Version 0.1.11

- Chapter `Soil` of Volume `Agriculture` initialized
- ubdate tutorials
- renaming of functions

## Version 0.2.0

- Chapter `Mineral` of Volume `Industry` initilialized
- Concept of `concordance` generalized to other parameters
- update documentation
- update tests

## Version 0.2.1

- revision for publication in JOSS

## Version 0.3.0

- change package name to `bonsai_ipcc` (revision for publication in JOSS)