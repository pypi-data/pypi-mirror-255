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


def write_template_image(
          YamlPath: str,
          Time: int = 1,
          Output_Link = 0,
          Point_nb: int = 500000,
          Temperature: int = 5800):
    r""""
        Write a yaml template with needed information, and with all information is Details == True

        Parameter
        ---------

        FilePath: string
            Position where you want to create the yaml file


    """


    Yaml_link = str(YamlPath)

    # Main Parts
    Dict = {}
    Dict['1-Photon_Generation'] = {}
    Dict['2-Timeline'] = {}
    Dict['3-Phase'] = {}
    Dict['4-Output'] = {}


    # Method part
    Dict['1-Photon_Generation']['Method'] = {}
    Dict['1-Photon_Generation']['Method']['method'] = 'Fits'
    Dict['1-Photon_Generation']['Method']['Filter'] = 'Black Body'
    Dict['1-Photon_Generation']['Method']['Temperature'] = 5800
    Dict['1-Photon_Generation']['Method']['Path'] = '/home/sfaes/git/simulation/src/Functions/Image/galaxy.fits'
    Dict['1-Photon_Generation']['Method']['Zoom'] = False
    Dict['1-Photon_Generation']['Method']['Center'] = False
    # Detector part
    Dict['1-Photon_Generation']['Detector'] = {}
    Dict['1-Photon_Generation']['Detector']['row'] = 5
    Dict['1-Photon_Generation']['Detector']['col'] = 5
    # Noise 
    Dict['1-Photon_Generation']['Noise'] = {}
    Dict['1-Photon_Generation']['Noise']['type'] = 'Poisson'
    Dict['1-Photon_Generation']['Noise']['scale'] = 4
    Dict['1-Photon_Generation']['Noise']['loc'] = 0

    # Timeline

    Dict['2-Timeline']['Time'] = Time
    Dict['2-Timeline']['Point_nb'] = Point_nb
   

   # Phase

    Dict['3-Phase']['Phase'] = True
    Dict['3-Phase']['Calib_file'] = 'Calib.csv'
    Dict['3-Phase']['Decay'] = -33e3
    Dict['3-Phase']['Noise'] = {}
    Dict['3-Phase']['Noise']['type'] = 'Gaussian'
    Dict['3-Phase']['Noise']['scale'] = 4
    Dict['3-Phase']['Noise']['loc'] = 0
    
    # Output
    Dict['4-Output']['Link'] = './data.hdf5'


    # Creating the Yaml
    with open(Yaml_link,'w') as f:
        yaml.dump(Dict,f)



# write_template_image('/home/sfaes/git/simulation/src/Functions/Yaml/test.yaml')