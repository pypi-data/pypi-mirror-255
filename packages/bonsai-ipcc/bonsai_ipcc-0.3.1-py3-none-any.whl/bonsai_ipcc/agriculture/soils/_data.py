from ..._data import Concordance, Dimension, Parameter

dimension = Dimension("data/")

parameter = Parameter(
    [
        "data/agriculture/soils",
        "data/agriculture/livestock_manure",
        "data/agriculture/generic",
    ]
)

concordance = Concordance("data/")
