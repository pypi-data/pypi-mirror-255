import os
from pathlib import Path

import pandas as pd
from pandas._libs.parsers import STR_NA_VALUES

ROOT_PATH = Path(os.path.dirname(__file__))

accepted_na_values = STR_NA_VALUES - {"NA"}


class Dimension:
    def __init__(self, path_in):
        path = ROOT_PATH.joinpath(path_in)
        filenames = next(os.walk(path), (None, None, None, None, None, []))[2]
        if filenames is not None:
            if len(filenames) == 0:
                print("No files in folder path")
            for filename in filenames:
                if (
                    filename[:4] == "dim_"
                    and filename[-4:] == ".csv"
                    and len(filename) > 8
                ):
                    try:
                        df = pd.read_csv(
                            path.joinpath(filename),
                            index_col="code",
                            keep_default_na=False,
                            na_values=accepted_na_values,
                        )
                        setattr(self, filename[4:-4], df)
                    except:
                        print(f"error reading {filename}")


class Parameter:
    def __init__(self, path_in):
        for p in path_in:
            path = ROOT_PATH.joinpath(p)
            filenames = next(os.walk(path), (None, None, None, None, None, []))[2]
            if filenames is not None:
                if len(filenames) == 0:
                    print("No files in folder path")
                for filename in filenames:
                    if (
                        filename[:4] == "par_"
                        and filename[-4:] == ".csv"
                        and len(filename) > 8
                    ):
                        try:
                            df = pd.read_csv(
                                path.joinpath(filename),
                                keep_default_na=False,
                                na_values=accepted_na_values,
                            )
                            index = [
                                val
                                for val in list(df.columns)
                                if val not in ["value", "unit"]
                            ]
                            df = df.set_index(index)
                            setattr(self, filename[4:-4], df)
                        except:
                            print(f"error reading {filename}")


class Concordance:
    def __init__(self, path_in):
        path = ROOT_PATH.joinpath(path_in)
        filenames = next(os.walk(path), (None, None, None, None, None, []))[2]
        if filenames is not None:
            if len(filenames) == 0:
                print("No files in folder path")
            for filename in filenames:
                if (
                    filename[:12] == "concordance_"
                    and filename[-4:] == ".csv"
                    and len(filename) > 8
                ):
                    try:
                        df = pd.read_csv(
                            path.joinpath(filename),
                            keep_default_na=False,
                            na_values=accepted_na_values,
                        )
                        index = df.columns[0]
                        df = df.set_index(index)
                        setattr(self, filename[12:-4], df)
                    except:
                        print(f"error reading {filename}")
