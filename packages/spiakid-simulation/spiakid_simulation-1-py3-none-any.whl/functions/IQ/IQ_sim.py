import numpy as np
import csv

import functions.utils as Ut

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

    IQ_dict: dictionnary
        Contains the coeeficient to convert the wavelength into I and Q according to the csv file
    
    
    """
    IQ_dict = {}
    with open(Path,'r') as file:
        data = csv.reader(file,delimiter = sep)
        for i in data:
            I = Ut.fit_parabola(eval(i[1]),eval(i[2]))
            Q = Ut.fit_parabola(eval(i[1]),eval(i[3]))
            IQ_dict[i[0]] = [I,Q]
    return(IQ_dict)

def IQ_interp():
    r""" Default conversion between Phase/Amplitude and IQ

    Parameters:
    -----------

    None

    Output:
    -------
    
    I: array
        Coefficients of the parabola to convert the wavelength in I
    
    Q: array
        Coefficients of the parabola to convert the wavelength in Q
    
    """
    amp = [0.0855, 0.0385, 0.02, 0.01368, 0.01] 
    phase = [17.5412, 7.3455, 3.7325, 2.503, 1.884]   #Degree
    lbd = [100,250,500,750,1000]   #nm
    I_num = amp * np.cos(phase)
    Q_num = amp * np.sin(phase)
    I = Ut.fit_parabola(lbd,I_num)
    Q = Ut.fit_parabola(lbd,Q_num)
    return I,Q

def photon2IQ_csv(Photon,Path):
    r""" Convert the wavelength into I and Q
    
    Parameters:
    -----------

    Photon: array
        Wavelength and timeline of photons per each pixels

    Output:
    -------

    I: array
        I for each photon on each pixel
    
    Q: array
        Q for each photon on each pixel
    
    """
    dim = np.shape(Photon)
    print(dim)
    I,Q = np.zeros(dim,dtype = object),np.zeros(dim,dtype = object)
    
    IQ_dict = read_csv(Path,sep='/')
   
    
    for i in range(dim[0]):
        for j in range(dim[1]):
            #  I[i,j] = [Photon[i,j][0],np.where(Photon[i,j][1] == 0,Photon[i,j][1],I_coeff[0] * Photon[i,j][1] ** 2 + I_coeff[1] * Photon[i,j][1]  + I_coeff[2])]
            #  Q[i,j] = [Photon[i,j][0],np.where(Photon[i,j][1] == 0,Photon[i,j][1],Q_coeff[0] * Photon[i,j][1] ** 2 + Q_coeff[1] * Photon[i,j][1]  + Q_coeff[2])]
            I[i,j] = [Photon[i,j][0],np.where(Photon[i,j][1] == 0,Photon[i,j][1],IQ_dict[str(i)+str(j)][0][0] * Photon[i,j][1] ** 2 + IQ_dict[str(i)+str(j)][0][1] * Photon[i,j][1] + IQ_dict[str(i)+str(j)][0][2])]
            Q[i,j] = [Photon[i,j][0],np.where(Photon[i,j][1] == 0,Photon[i,j][1],IQ_dict[str(i)+str(j)][1][0] * Photon[i,j][1] ** 2 + IQ_dict[str(i)+str(j)][1][1] * Photon[i,j][1] + IQ_dict[str(i)+str(j)][1][2])]
    return(I,Q)


def photon2IQ_th(Photon):
    r""" Convert the wavelength into I and Q
    
    Parameters:
    -----------

    Photon: array
        Wavelength and timeline of photons per each pixels

    Output:
    -------

    I: array
        I for each photon on each pixel
    
    Q: array
        Q for each photon on each pixel
    
    """
    dim = np.shape(Photon)
    I,Q = np.zeros(dim,dtype = object),np.zeros(dim,dtype = object)
    I_coeff,Q_coeff = IQ_interp()
    I_dict,Q_dict = {},{}
    for i in range(dim[0]):
        for j in range(dim[1]):
             I[i,j] = [Photon[i,j][0],np.where(Photon[i,j][1] == 0,Photon[i,j][1],I_coeff[0] * Photon[i,j][1] ** 2 + I_coeff[1] * Photon[i,j][1]  + I_coeff[2])]
             Q[i,j] = [Photon[i,j][0],np.where(Photon[i,j][1] == 0,Photon[i,j][1],Q_coeff[0] * Photon[i,j][1] ** 2 + Q_coeff[1] * Photon[i,j][1]  + Q_coeff[2])]
    return(I,Q)


def exp_adding(sig,decay):
    r""" Add the exponential decay after the photon arrival on each pixel

    Parameters:
    -----------

    sig: array
        Signal on each pixel

    decay: float
        The decay of the decreasing exponential
    
    Output:
    -------
    
    signal: array
        The signal with the exponential decrease on each pixel 
    
    """
    dim = np.shape(sig)
    signal = np.zeros(dim,dtype = object)
    for i in range(dim[1]):
          for j in range(dim[2]):
            #    print(i,j)
               signal[0][i,j] = exp(sig[0][i,j],decay)
               signal[1][i,j] = exp(sig[1][i,j],decay)
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