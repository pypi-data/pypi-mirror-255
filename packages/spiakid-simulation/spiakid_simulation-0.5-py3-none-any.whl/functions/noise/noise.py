import numpy as np
import numpy.random as rand


def gaussian(x,location=0,scale=4):
    r""" Add Gaussian noise on the signal

    Parameters:
    -----------

    x: array
        Signal on each pixel
    
    location: float
        Expected value of the guassian noise
    
    scale: float
        Standard deviation of the gaussian noise
    
    Output:
    -------

    signal: array
        The signal with the Gaussian noise
    """
    dim = np.shape(x)
    if (type(x[0,0]) == np.int16) | (type(x[0,0]) == np.float64):
        signal = np.zeros(dim,dtype = float)
        for i in range(dim[0]):
            for j in range(dim[1]):
                signal[i,j] = x[i,j] +  rand.normal(loc = location,scale = scale)
    else:
        signal = np.zeros(dim,dtype = object)
        for i in range(dim[0]):
            for j in range(dim[1]):
                signal[i,j] = np.zeros(np.shape(x[i,j]))
                signal[i,j][0] = x[i,j][0]
                for k in range (len(x[i,j][0])):
                    signal[i,j][1][k] = x[i,j][1][k] + rand.normal(loc = location,scale = scale)
    return(signal)

def poisson(x):
    r""" Add Poisson noise on the signal

    Parameters:
    -----------

    x: array
        Signal on each pixel
    
    Output:
    -------

    signal: array
        The signal with the Poisson noise
    """
    rng = rand.default_rng()
    dim = np.shape(x)
    if (type(x[0,0]) == np.int16) | (type(x[0,0]) == np.float64):
        signal = np.zeros(dim,dtype = float)
        for i in range(dim[0]):
            for j in range(dim[1]):
                signal[i,j] = float(rng.poisson(x[i,j]))
    else:
        signal = np.zeros(dim,dtype = object)
        for i in range(dim[0]):
            for j in range(dim[1]):
                signal[i,j] = np.zeros(np.shape(x[i,j]))
                signal[i,j][0] = x[i,j][0]
                for k in range (len(signal[i,j][0])):
                    signal[i,j][1][k] = rng.poisson(x[i,j][1][k])
    return(signal)
