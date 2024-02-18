import numpy as np 
from astropy.io import fits
from pathlib import Path

def Photon_gen(FitsPath,detector_dim,center = True, zoom = True):
    """Read the Fits file and generate the number of photon to simulate according to the detector's dimension

    Parameters:
    -----------

    FitsPath: string
        Path to the Fits file
    
    detector_dim: array
        Dimension of the detector
    
    center: Boolean (optional)
        Simulate the center of the image

    zoom: Bolean (optional)
        Simulate a zoom or the whole image
    
    Output:
    -------

    Photon: array
        Number of photon per pixel
    
    """
    filename = Path(FitsPath).resolve()
    data = fits.getdata(filename)
    data = np.array(data)

    if center == True:
        base = [int(len(data[0])/2),int(len(data[1])/2)]

        if zoom == True:
            
            photon = data[base[0]-int(detector_dim[0]/2):base[0]+int((detector_dim[0]+1)/2) , base[1]-int(detector_dim[1]/2):base[1]+int((detector_dim[1]+1)/2)]

        else:
            photon = []
            center_x = int(np.floor((len(data[0]) - int(np.floor(len(data[0]))/detector_dim[0])*detector_dim[0]) / 4))
            center_y = int(np.floor((len(data[1]) - int(np.floor(len(data[1]))/detector_dim[1])*detector_dim[0])/ 4))

            ratio0 = int(len(data[0])/detector_dim[0])
            ratio1 = int(len(data[1])/detector_dim[1])
            for i in range(detector_dim[0]):
                for j in range(detector_dim[1]):
                    photon.append(np.mean(data[center_x + int(i*ratio0 ):center_x + int((i+1)*ratio0 ),center_y + int(j*ratio1):center_y + int((j+1)*ratio1)]))
            photon = np.reshape(photon,detector_dim)
    
    else:
        base = [int(detector_dim[0]/2),int(detector_dim[1]/2)]
        if zoom == True:
            photon = data[base[0]-int(detector_dim[0]/2):base[0]+int((detector_dim[0]+1)/2) , base[1]-int(detector_dim[1]/2):base[1]+int((detector_dim[1]+1)/2)]

        else:
            photon = []
            center_x = 0
            center_y = 0

            ratio0 = int(len(data[0])/detector_dim[0])
            ratio1 = int(len(data[1])/detector_dim[1])
            for i in range(detector_dim[0]):
                for j in range(detector_dim[1]):
                    photon.append(np.mean(data[center_x + int(i*ratio0 ):center_x + int((i+1)*ratio0 ),center_y + int(j*ratio1):center_y + int((j+1)*ratio1)]))
            photon = np.reshape(photon,detector_dim)
    
    return(photon)