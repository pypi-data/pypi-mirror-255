import numpy as np
from scipy import interpolate
import functions.utils as Ut

def phase_conv(Photon,pix,conv_wv,conv_phase,resolution):
    r"""Convert the wavelength in phase on each pixel

    Parameters:
    -----------

    Photon: array
        Photon's wavelength on each pixel

    pix: array
        Pixel id

    conv_wv: array
        Calibration's wavelength

    conv_phase: array
        Calibration's phase

    resolution: float
        Spectrale resolution of the detector

    Output:
    -------

    signal: array
        Phase on each pixel 
    
    
    """
    dim = np.shape(Photon)
    signal = np.zeros(dim,dtype = object)
    dict = {}
    for i in range(len(pix)):
        dict[pix[i]] = [conv_wv[i],conv_phase[i]]
    for i in range(dim[0]):
        for j in range(dim[1]):
            signal[i,j] = photon2phase(Photon[i,j],dict[str(i)+str(j)][0],dict[str(i)+str(j)][1], resolution)
    return(signal)


def photon2phase(Photon,conv_wv,conv_phase, resolution):
    r"""Convert the wavelength in phase

    Parameters:
    -----------

    Photon: array
        Photon's wavelength on each pixel

    conv_wv: array
        Calibration's wavelength

    conv_phase: array
        Calibration's phase

    Output:
    -------

    signal: array
        Signal converted in phase 
    
    
    """
    signal = np.copy(Photon)
    curv = Ut.fit_parabola(conv_wv,conv_phase)
    ph = curv[0] * Photon[1] ** 2 +  curv[1] * Photon[1] + curv[2] #µ
    sigma = ph / (2*resolution*np.sqrt(2*np.log10(2)))
    signal[1] = np.where(Photon[1]==0,Photon[1],np.random.normal(ph, sigma))
    return(signal)

def exp_adding(phase,decay):
    r""" Add the exponential decay after the photon arrival on each pixel

    Parameters:
    -----------

    phase: array
        Signal on each pixel

    decay: float
        The decay of the decreasing exponential
    
    Output:
    -------
    
    signal: array
        The signal with the exponential decrease on each pixel 
    
    """
    dim = np.shape(phase)
    signal = np.zeros(dim,dtype = object)
    for i in range(dim[0]):
          for j in range(dim[1]):
            #    print(i,j)
               signal[i,j] = exp(phase[i,j],decay)
    return(signal)


def exp(sig,decay):
    r""" Add the exponential decay after the photon arrival

    Parameters:
    -----------

    sig: array
        Signal with the photon arrival

    decay: float
        The decay of the decreasing exponential
    
    Output:
    -------
    
    signal: array
        The signal with the exponential decrease
    
    """
    sig_time = np.copy(sig[0])
    sig_amp = np.zeros((len(sig_time)))
    
    phase_point = np.copy(sig[1])
    for i in range(len(sig[1])):
        if phase_point[i] !=0:
                if i+500 < len(sig[0]):
                    for j in range(0,500):
                        exp_time = sig[0][i:i+500]
                        sig_amp[i+j] += sig[1][i] * np.exp(decay * (exp_time[j]-exp_time[0])) 
                else:
                     for j in range(0,len(sig[1])-i):
                        exp_time = sig[0][i:len(sig[1])]
                        sig_amp[i+j] += sig[1][i] * np.exp(decay * (exp_time[j]-exp_time[0]))
    return([sig_time,sig_amp])


