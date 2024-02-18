import numpy as np
import numpy.random as rand

def Black_Body(Temperature,NbPhoton,wv_min,wv_max):
    r"""Give photons with a random wavelength and radiance and sort them according to Black Body

    Parameters:
    -----------

    Temperature: float
        The temperature of the Black Body
    
    NbPhton: int
        How many photon to sort
    
    wv_min: float
        The minimum wavelength
    
    wv_max: float
        The maximum wavelength
    
    Output:
    -------

    wv_ok: array
        Wavelength of simulated photon which fit in the Black Body

    bb_ok: array
        Radiance of simulated photon which fit in the Black Body

    wv_out: array
        Wavelength of simulated photon which doesn't fit in the Black Body

    bb_out:
        Radiance of photon which doesn't fit in the Black Body

    """
    kb = 1.380469e-23 #J.K-1
    h = 6.62607015e-34 #J.Hz-1
    c = 299792458e6 #µm.s-1
    NbPhoton = int(NbPhoton)
    wv_ok = []
    bb_ok =[]
    wv_out = []
    bb_out =[]
    array = np.linspace(wv_min,wv_max,100000) # Wavelength in µm
    Black_Body =  2 * h * c*c /(array**4 *(np.exp(h*c/(array*kb*Temperature))-1))
    norm = max(Black_Body)
    while len(wv_ok) !=NbPhoton:
            Photon=[rand.uniform(0.38,1),rand.uniform(0,1)]
            
            if Photon[1] <= 2 * h * c*c /(Photon[0]**4 *(np.exp(h*c/(Photon[0]*kb*Temperature))-1))/norm:
                wv_ok.append(Photon[0])
                bb_ok.append(Photon[1])
            else:
                wv_out.append(Photon[0])
                bb_out.append(Photon[1])
    return (wv_ok,bb_ok,wv_out,bb_out)


def BB_filter(Temperature,FitsPhoton,wv_min=0.38,wv_max=1):
    r"""Give photons with a random wavelength and radiance and sort them according to Black Body for each pixel

    Parameters:
    -----------

    Temperature: float
        The temperature of the Black Body
    
    FitsPhoton: int
        How many photon to sort
    
    wv_min: float
        The minimum wavelength
    
    wv_max: float
        The maximum wavelength
    
    Output:
    -------

    wv_ok: array
        Wavelength of simulated photon which fit in the Black Body for each pixel

    bb_ok: array
        Radiance of simulated photon which fit in the Black Body for each pixel

    wv_out: array
        Wavelength of simulated photon which doesn't fit in the Black Body for each pixel

    bb_out:
        Radiance of simulated photon which doesn't fit in the Black Body for each pixel

    """
    BB_photon_ok = np.zeros(np.shape(FitsPhoton), dtype=object)
    BB_photon_out = np.zeros(np.shape(FitsPhoton), dtype=object)
    BB_radiance_ok = np.zeros(np.shape(FitsPhoton), dtype=object)
    BB_radiance_out = np.zeros(np.shape(FitsPhoton), dtype=object)


    for i in range(len(FitsPhoton[0])):
        for j in range(len(FitsPhoton[1])):

            wv_ok,bb_ok,wv_out,bb_out =Black_Body(Temperature=Temperature, NbPhoton=FitsPhoton[i,j],wv_min=wv_min,wv_max=wv_max)
            BB_photon_ok[i,j] = wv_ok
            BB_photon_out[i,j] = wv_out
            BB_radiance_ok[i,j] = bb_ok
            BB_radiance_out[i,j] = bb_out
    return(BB_photon_ok,BB_radiance_ok,BB_photon_out,BB_radiance_out)


# #Test
# Fits = [[300,500,200],
#         [100,405,200],
#         [102,807,51]]
# Fits = np.array(Fits)
# temperature = 5800
# a,b,c,d = BB_filter(temperature,Fits)
# print(len(a[2,1]))

