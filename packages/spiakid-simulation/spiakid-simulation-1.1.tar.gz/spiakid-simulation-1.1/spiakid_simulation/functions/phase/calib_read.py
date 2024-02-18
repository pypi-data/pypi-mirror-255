import csv
import numpy as np
import numpy.random as rand

def read_csv(Path,sep='/'):
    r"""Read the calibration file

    Parameters:
    -----------

    Path: string
        Path to the calibration file
    
    sep: string
        The delimiter

    Output:
    -------

    pix: array
        The pixel id

    wv: array
        Calibration wavelength

    phase: array
        Calibration phase          
    
    
    """
    pix = []
    wv = []
    phase = []
    with open(Path,'r') as file:
        data = csv.reader(file,delimiter = sep)
        for i in data:
            pix.append(i[0])
            wv.append(eval(i[2]))
            phase.append(eval(i[1]))
    return(pix,wv,phase)


def write_csv(Path,dim,sep='/'):
    r"""Write a default file for th ephase Calibration

    Parameters:
    -----------

    Path: string
        Path to the calibration file
    
    dim: array
        Dimension of the detector

    sep: string
        The delimiter
    
    Outputs:
    --------

    None
    """
    with open(Path,'w',newline='') as file:
        writer  =csv.writer(file,delimiter=sep)
        for i in range(dim[0]):
            for j in range(dim[1]):
                writer.writerow([str(i)+str(j),(rand.normal(loc = 150,scale = 1),rand.normal(loc = 30,scale = 1),rand.normal(loc = 10,scale = 1)),(rand.normal(loc = 0.4,scale = 0.05),rand.normal(loc = 0.65,scale = 0.05),rand.normal(loc = 0.9,scale = 0.05))])

# write_csv('/home/sfaes/git/simulation/src/Functions/Phase/test.csv',dim = [5,5])


