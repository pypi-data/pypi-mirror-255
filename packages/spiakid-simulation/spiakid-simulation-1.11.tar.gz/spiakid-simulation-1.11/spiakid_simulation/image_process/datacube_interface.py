from tkinter import * 
from matplotlib.figure import Figure
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from astropy.io import fits 
from spectral_cube import SpectralCube

import warnings

def interface(path_file):
    fenetre = Tk()
    fenetre.geometry("1250x600")
    fenetre.grid()

    def double_plot(event):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            x = int(var_1.get())
            y = int(var_2.get())
            axes_2.clear()
            
            
            axes_2.plot(l,data[:,x,y])
            axes_2.set_xlabel('Wavelength [m]')
            axes_2.set_ylabel('Amplitude [W/m**2/nm]')
            # axes_2.set_xscale('log')
            canvas2.draw()
            canvas2.get_tk_widget().grid(column = 2, row = 0)

            pointer = np.zeros(np.shape(Data))
            pointer[x,y] = 1
            pointer = np.ma.masked_where(pointer !=1, pointer)
            axes.imshow(Data,cmap='gray_r')
            axes.imshow(pointer,cmap = 'spring')
            canvas.draw()
    hdr = fits.open(path_file)
    start = hdr[0].header['CRVAL3']
    step = hdr[0].header['CDELT3']
    hdr.close()
    data = fits.getdata(path_file)
    stop = len(data[:,0,0])*step+start
    l = np.linspace(start,stop, len(data[:,0,0]))*10**-9
    Image_size = len(data[0,:,:])
    figure = Figure(figsize=(6, 5), dpi=100)
    Data = np.zeros((Image_size ,Image_size ))
    for i in range(Image_size ):
        for j in range(Image_size ):
            Data[i,j] = sum(data[:,i,j])
    axes = figure.add_subplot()
    axes.imshow(Data,cmap='gray_r')
    canvas = FigureCanvasTkAgg(figure,master = fenetre)  

    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas,fenetre,pack_toolbar = False)
    toolbar.grid(column = 0,row = 1)
    canvas.get_tk_widget().grid(column = 0,row = 0)

    figure_2 = Figure(figsize=(6, 5), dpi=100)
    axes_2 = figure_2.add_subplot()
    canvas2 = FigureCanvasTkAgg(figure_2,master = fenetre) 

    var_1 = DoubleVar()
    var_2 = DoubleVar()
    scale_1 = Scale(fenetre, variable=var_2,from_=0,to=Image_size-1,orient=HORIZONTAL,length= 300)
    scale_1.grid(column = 0,row = 2)
    scale_2 = Scale(fenetre,variable=var_1,from_=0,to=Image_size-1,length = 300)
    scale_2.grid(column = 1,row = 0)
    scale_1.bind("<ButtonRelease-1>",double_plot)
    scale_2.bind("<ButtonRelease-1>",double_plot)


    fenetre.mainloop()


interface('/spiakid/data/Simulation_Image/Simulation_Test.fits')