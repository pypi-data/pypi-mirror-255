import yaml
from yaml.loader import SafeLoader
from pathlib import Path


def read_yaml(FilePath):
        r""""
        Read yaml file and store all information in data

        Parameter
        ---------

        FilePath: string
            Position and name of the yaml file

        Attributes
        ----------

        Data: Dictionnary
            Contains all information that contains the yaml file correctly ordered
        """
        with open(FilePath) as f:
            data = yaml.load(f, Loader=SafeLoader)
        return data


