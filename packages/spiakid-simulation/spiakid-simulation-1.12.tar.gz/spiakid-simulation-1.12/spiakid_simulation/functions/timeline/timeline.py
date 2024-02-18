import numpy as np

def pixel_sorting(time,data,point_nb,time_data):
        r""" Sort value according to the time

        Parameters:
        -----------

        time: float
            Time of observation

        data: array
            Photon's wavelength
        
        point_nb: int
            Number of point we want
        
        Output:
        -------

        signal: array
            Arrival time and wavelength of photons randomly spread
        
        """
        point_nb = int(point_nb)
        if type(data) == list:
            signal = list(np.zeros([2,point_nb-len(data)]))
            photon_time = time_data
            signal[0] = np.linspace(0,time,point_nb-len(data))
            signal[0] = list(signal[0]) + list(photon_time)
            signal[1] = list(signal[1]) + list(data)
            signal_int = []
            for i in range(len(signal[0])):
                signal_int.append((signal[0][i],signal[1][i]))
            Sorted_signal = sorted(signal_int,key=lambda x:x[0])
            for i in range(len(signal[0])):
                signal[0][i] = Sorted_signal[i][0]
                signal[1][i] = Sorted_signal[i][1]
        
        
        else:
             signal = list(np.zeros([2,point_nb]))
             signal[0] = np.linspace(0,time,point_nb)

        return(np.array(signal))
        


def sorting(time,data,point_nb, time_data):
    r""" Sort value according to the time on each pixel

        Parameters:
        -----------

        time: float
            Time of observation

        data: array
            Photon's wavelength
        
        point_nb: int
            Number of point we want
        
        Output:
        -------

        signal: array
            Arrival time and wavelength of photons randomly spread on each pixel
        
        """
    dim = np.shape(data)
    signal = np.zeros(dim,dtype = object)
    Point_number = point_nb * time
    for i in range(dim[0]):
          for j in range(dim[1]):
               signal[i,j] = pixel_sorting(time,data[i,j],Point_number,time_data[i,j])
    return(signal)