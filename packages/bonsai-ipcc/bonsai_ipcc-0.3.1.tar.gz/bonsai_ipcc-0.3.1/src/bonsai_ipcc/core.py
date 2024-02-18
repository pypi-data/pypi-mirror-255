import inspect
import re
from importlib.resources import open_binary

import yaml

from . import agriculture, industry, waste


class IPCC:
    def __init__(self):
        self.waste = waste
        self.agriculture = agriculture
        self.industry = industry

    # TODO: when specifying sequence in yaml config, this needs revision
    @staticmethod
    def inspect(func):
        """Get the required parameters of a tier method.

        Argument
        --------
        func : function
            tier sequence of a volume, chapter

        Returns
        -------
        VALUE: list of str
            parameter names
        """
        s = inspect.getsource(func)
        parameters = list(set(re.findall('table="([a-z,_,A-Z,0-9,-]+)', s)))
        return parameters

    @staticmethod
    def metadata(volume, chapter, parameter):
        """Get the metadata of a parameter.

        Argument
        --------
        volume : string
            volume name
        chapter : string
            chapter name
        paramater : string
            parameter name

        Returns
        -------
        VALUE: dict
            metadata pointing to the source in the IPCC pdf documents
            (year, volume, chapter, page, equation)
        """
        with open_binary("ipcc.data", "ipcc.datapackage.yaml") as fp:
            metadata = yaml.load(fp, Loader=yaml.Loader)
        for k in range(len(metadata["resources"])):
            if (
                metadata["resources"][k]["path"]
                == f"{volume}/{chapter}/par_{parameter}.csv"
            ):
                d = metadata["resources"][k]
        try:
            return d
        except UnboundLocalError:
            raise KeyError(
                f"parameter '{parameter}' for volume '{volume}', chapter '{chapter}' not found in the metadata"
            )
