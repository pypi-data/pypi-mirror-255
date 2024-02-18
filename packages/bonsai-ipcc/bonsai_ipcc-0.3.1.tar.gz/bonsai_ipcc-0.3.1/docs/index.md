# bonsai_ipcc

The `bonsai_ipcc` python package enables users to calculate national greenhouse gas (GHG) inventories based on the guidelines provided by the International Panel on Climate Change (IPCC).

This package provides utility functions to calculate greenhouse gas inventories based on [IPCC Guidelines for National Greenhouse Gas Inventories](https://www.ipcc-nggip.iges.or.jp/public/2006gl/).
Wherever possible, 2019 refinement to the guidelines is used.
The structure of the package follows the volumes of the guidelines:
- [energy](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol2.html)
- [industry](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol3.html)
- [agriculture](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html)
- [waste](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol5.html)

Each volume consists of chapters, which include equations to calculate the inventories. Each chapter consists of individual elementary equations and sequences. Elementary equations specify the (numbered) equations of the IPCC guidelines. Sequences combine elementary eqautions in a specific order to quantify a greenhouse gas inventory (i.e., tier 1, tier 2 and tier 3).

You can download the documentation as a pdf [here](https://bonsamurais.gitlab.io/bonsai/util/ipcc/user_guide.pdf).
## Contents

```{toctree}
:maxdepth: 1

Overview <readme>
Contributions & Help <contributing>
tutorials
License <license>
Authors <authors>
Changelog <changelog>
Module Reference <api/modules>
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
