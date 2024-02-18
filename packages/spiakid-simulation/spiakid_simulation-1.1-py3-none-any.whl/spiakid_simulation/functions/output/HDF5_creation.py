import h5py
import numpy as np
from scipy.signal import find_peaks


def recursively_save_dict_contents_to_group(h5file, path, dic):
    """
    ....
    """
    for key, item in dic.items():
        if isinstance(item, (np.ndarray, np.int64, np.float64,int,float, str, bytes)):
            h5file['Config/'+path + key] = item
        elif isinstance(item, dict):
            recursively_save_dict_contents_to_group(h5file, path + key + '/', item)
        else:
            raise ValueError('Cannot save %s type'%type(item))
        

def save_dict_to_hdf5(dic, filename,sim,size):
    """
    ....
    """
    h5file = h5py.File(filename, 'w')
    recursively_save_dict_contents_to_group(h5file, '/', dic)
    h5file['star'] = sim.star_pos
    h5file['spectrum'] = sim.star_spec
    h5file['psf'] = sim.psf_visu


    for i in range(size):
        for j in range(size):
            h5file['wavelength/'+str(i)+'_'+str(j)] = sim.wavelength[i,j]
            h5file['time/'+str(i)+'_'+str(j)] = sim.time[i,j]
            h5file['phase/'+str(i)+'_'+str(j)] = sim.phase[i,j]

    

def save_photon_list(filename,dic,filtered_signal,noise):
    h5file = h5py.File(filename, 'w')
    recursively_save_dict_contents_to_group(h5file, '/', dic)
    size, _ = np.shape(filtered_signal)
    
    for i in range(size):
        for j in range(size):
            m_noise = max(noise[i,j][1])
            peaks, _ = find_peaks(filtered_signal[i,j][1],prominence = 10, height=m_noise)
            h5file['Photons/'+str(i)+'_'+str(j)]  = [np.float32(filtered_signal[i,j][0][peaks]), np.float32(filtered_signal[i,j][1][peaks])]
        
