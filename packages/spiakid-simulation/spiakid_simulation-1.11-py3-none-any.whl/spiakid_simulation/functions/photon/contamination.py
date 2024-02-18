import numpy as np
import numpy.random as rand


def Continuous(Nb_photon, wv_min,wv_max,amp_min,amp_max):
    return(rand.uniform(low = wv_min,high = wv_max, size =int(np.ceil(Nb_photon))),rand.uniform(low = amp_min,high = amp_max, size =int(np.ceil(Nb_photon))))