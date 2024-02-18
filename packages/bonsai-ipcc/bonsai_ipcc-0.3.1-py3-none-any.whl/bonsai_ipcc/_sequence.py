import inspect
import logging
from dataclasses import dataclass
from itertools import product

import numpy as np
import pandas as pd

from . import _checks as checks
from . import uncertainties as unc

logger = logging.getLogger(__name__)


@dataclass
class Step:
    position: int
    year: int  # or list of int
    unit: str
    value: float  # ufloat, np.array or list of those
    type: str


class Sequence:
    def __init__(self, dim, par, elem, conc, uncert):
        self.dimension = dim
        self.parameter = par
        self.elementary = elem
        self.concordance = conc
        self.uncertainty = uncert
        self.step = DataClass()
        self.order = []

    def _validate_coordinate(self, coord, dim):
        """
        Validate if the given coordinate exists in the specified dimension.

        Args:
            coord (str): Coordinate to validate.
            dim (str): Dimension name.

        Raises:
            ValueError: If the coordinate does not exist in the dimension.
        """
        df_dim = getattr(self.dimension, dim)
        checks.check_set(coord, df_dim.index, "coordinate")

    def _read_parameter_with_concordance(self, df, _coords, name, table):
        """
        Read parameter data and uncertainty information with concordance handling.

        Args:
            df (pd.DataFrame): Parameter DataFrame.
            _coords (tuple): Coordinates for data retrieval.
            name (str): Parameter name.
            table (str): Parameter table name.

        Returns:
            tuple: Tuple containing value, unit and new coords.
        """
        conc_dim_list = []
        for _dim in df.index.names:
            if _dim in [k for k in self.concordance.__dict__]:
                conc_dim = _dim
                conc_dim_list.append(conc_dim)
        if not conc_dim_list:
            raise KeyError("No concordance data found for any dimension")

        conc_df_list = []
        for conc_dim in conc_dim_list:
            try:
                conc_df = getattr(self.concordance, conc_dim)
                conc_df_list.append(conc_df)
            except AttributeError:
                raise KeyError(f"No concordance data found for dimension '{conc_dim}'")

        tmp, u = None, None

        new_coords_list = []
        for conc_df in conc_df_list:

            for j in range(len(conc_df.columns)):
                new_coords = []
                for c in _coords:
                    if c in conc_df.index:
                        old_c = c
                        new_c = conc_df.loc[c][j]
                        new_coords.append(new_c)
                    else:
                        new_coords.append(c)
                new_coords_list.append(new_coords)

        # create all combinations of new coordinates that are possible and check if values are available
        a = np.array(new_coords_list).T.tolist()
        l = []
        for p in a:
            l.append(p)
        aa = product(*l)

        def is_number(s):
            """Convert years into integer"""
            try:
                int(float((s)))
                return int(float(s))
            except ValueError:
                return s

        new_coords_list = []
        for b in aa:
            new_coords_list.append(list([is_number(x) for x in list(b)]))
        new_coords_list = [list(x) for x in set(tuple(x) for x in new_coords_list)]

        # try reading the paramater based on the potential coordinates, stop at the first match
        for new_coords in new_coords_list:
            try:
                tmp, u = self._read_parameter_uncertainty(df, new_coords, table)
                logger.info(
                    f"'Coordinates {str(_coords)}' has been replaced by '{str(new_coords)}' during reading parameter table '{str(table)}'"
                )
                break
            except Exception:
                pass

        if tmp is None or u is None:
            raise KeyError("No data or uncertainty found using concordance")

        return tmp, u, new_coords

    def _read_parameter_uncertainty(self, df, coords, name):
        """
        Read parameter data with uncertainty information.

        Args:
            df (pd.DataFrame): Parameter DataFrame.
            coords (iterable): Coordinates for data retrieval.
            name (str): Parameter name.

        Returns:
            tuple: Tuple containing value and unit.
        """
        coords = list(coords)
        if self.uncertainty not in ["analytical", "monte_carlo", "def", "min", "max"]:
            raise ValueError(f"Unsupported uncertainty type: {self.uncertainty}")

        elif (
            self.uncertainty not in ["analytical", "monte_carlo"]
            and "property" in df.index.names
        ):
            coords = coords + [self.uncertainty]
            tmp = df.loc[tuple(coords)].value
            u = df.loc[tuple(coords)].unit
        elif self.uncertainty == "monte_carlo" and "property" in df.index.names:
            d = df.loc[tuple(coords + ["def"])].value
            min_val = df.loc[tuple(coords + ["min"])].value
            max_val = df.loc[tuple(coords + ["max"])].value
            abs_min = df.loc[tuple(coords + ["abs_min"])].value
            abs_max = df.loc[tuple(coords + ["abs_max"])].value
            logger.info(f"Uncertainty distribution for parameter '{name}':")
            tmp = unc.monte_carlo(
                default=d,
                min95=min_val,
                max95=max_val,
                abs_min=abs_min,
                abs_max=abs_max,
                size=1000,
                distribution="check",
            )
            u = df.loc[tuple(coords + ["max"])].unit
        elif self.uncertainty == "analytical" and "property" in df.index.names:
            min_val = df.loc[tuple(coords + ["min"])].value
            max_val = df.loc[tuple(coords + ["max"])].value
            tmp = unc.analytical(min_val, max_val)
            u = df.loc[tuple(coords + ["max"])].unit
        else:
            tmp = df.loc[tuple(coords)].value
            u = df.loc[tuple(coords)].unit

        return tmp, u

    def read_parameter(self, name, table, coords):
        """
        Read parameter data and uncertainty information, then store it in the step.

        Args:
            name (str): Name of the parameter.
            table (str): Name of the parameter table.
            coords (iterable): Coordinates to retrieve the data.

        Raises:
            KeyError: If coordinates or their concordance are not found.
        """

        # validate parameter table exists
        checks.check_set(table, self.parameter.__dict__.keys(), "parameter table")

        # validate name does not yet exist
        checks.check_set(name, self.order, "name", include=False)

        df = getattr(self.parameter, table)

        # check for duplicates in index
        if df.index.duplicated().any():
            raise ValueError(f"Duplicated indices in parameter {name}")

        _coords = tuple(coords)
        new_coords = coords
        for coord, dim in zip(_coords, df.index.names):
            self._validate_coordinate(coord, dim)

        try:
            tmp, u = self._read_parameter_uncertainty(df, _coords, table)
        except Exception:
            try:
                tmp, u, new_coords = self._read_parameter_with_concordance(
                    df, _coords, name, table
                )
            except Exception:
                raise KeyError(
                    f"Coordinate '{_coords}' or its concordance not found for parameter '{name}' with table '{table}'. If uncertainty analysis, also check required properties (e.g. max, min)."
                )

        # add year to step
        if "year" in df.index.names:
            year = [x for x in new_coords if isinstance(x, int)][0]
            # df = df.reset_index(level="year")
            # year = list(df.loc[tuple(no_integers + [self.uncertainty])]["year"])
        else:
            year = None

        position = len(self.order)
        setattr(
            self.step,
            name,
            Step(
                position=position, year=year, value=tmp, unit=u, type="data"
            ),  # year=year,
        )
        self.order.append(name)

    def store_result(self, name, value, unit, year=None):
        """
        Store a result in the step.

        Args:
            name (str): Name of the result.
            value (float): Result value.
            unit (str): Unit of the result.
            year (int, optional): Year associated with the result. Defaults to None.
        """
        position = len(self.order)
        setattr(
            self.step,
            name,
            Step(
                position=position,
                year=year,
                value=value,
                unit=unit,
                type="elementary",  # year=year,
            ),
        )
        self.order.append(name)

    def store_signature(self, d):
        """
        Store a the signature in the step.

        Args:
            d (dict): signature dictionary (e.g. by locals())
        """
        try:
            del d["seq"]
        except:
            pass
        setattr(
            self.step,
            "signature",
            d,
        )
        self.order.append("signature")

    def get_inventory_levels(self, table, year, region):
        """
        Returns the dimensions and its unique level values in a dict, without the dimensions year and region.
        """
        df = getattr(self.parameter, table)
        try:
            df = df[df.index.get_level_values("property") == "def"]
            df1 = df.loc[year, region]
            # df1 = df1[df1["property"] == "def"]
        except Exception:
            raise KeyError(
                f"Year '{year}' and region '{region}' not found in parameter table '{table}'."
            )
        return {
            level_name: df1.index.get_level_values(level).tolist()
            for level, level_name in enumerate(df1.index.names)
        }


@dataclass
class DataClass:
    def to_frame(self):
        """
        Convert the DataClass instance to a DataFrame.

        Returns:
            pd.DataFrame: DataFrame representation of the DataClass instance.
        """
        df_out = pd.DataFrame({})
        for p in self.__dict__:
            # Create DataFrame for each parameter attribute
            if p == "signature":
                sig = self.__dict__[p]
            else:
                df = pd.DataFrame(
                    {
                        "parameter": p,
                        "year": [self.__dict__[p].year],
                        "unit": self.__dict__[p].unit,
                        "value": [self.__dict__[p].value],
                        "type": [self.__dict__[p].type],
                    },
                    index=[self.__dict__[p].position],
                )
                df_out = pd.concat([df_out, df])
                df_out.index.name = "position"
        return df_out, sig
