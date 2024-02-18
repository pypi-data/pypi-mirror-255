import numpy as np
from tkinter import * 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure


def displacement(Ntot,Npsf):
    N,new_ntot  = Screen_size(Ntot,Npsf)

    Disp_x = np.zeros(new_ntot+1)
    Disp_y = np.zeros(new_ntot+1)
    Disp_x[0] = 0
    Disp_y[0] = 0
    ind_x = 0
    ind_y = 0
    dir = 0
    for i in range(1,new_ntot+1):
        # Déplacement coté droit
        if Disp_x[i-1] + 1 + Npsf <= N and Disp_y[i-1] + 1 + Npsf <= N and Disp_y[i-1]%Npsf == 0 and dir == 0: 
            Disp_x[i] = Disp_x[i-1] + 1
            Disp_y[i] = Disp_y[i-1]
            ind_x += 1
            ind_y += 1

        # Déplacement coté gauche
        elif Disp_x[i-1] - 1 >=0 and Disp_y[i-1] - 1 >=0 and Disp_y[i-1]%Npsf == 0 and dir == 1: 

            Disp_x[i] = Disp_x[i-1] -1
            Disp_y[i] = Disp_y[i-1]
            ind_x += 1
            ind_y += 1

        #On monte

        else:
            Disp_x[i] = Disp_x[i-1]
            Disp_y[i] = Disp_y[i-1] + 1
            if Disp_y[i]%Npsf == 0 and Disp_x[i]//(N - Npsf)== 1:
                dir = 1
            elif Disp_y[i]%Npsf == 0 and Disp_x[i]//(N - Npsf) == 0:
                dir = 0
    Displacement = [Disp_x,Disp_y]
    return(Displacement)




def Screen_size(Ntot,Npsf):
    N = Npsf
    
    while N//Npsf *(N-Npsf) + (N//Npsf - 1 ) * Npsf +  (N%Npsf) < Ntot :
          N+=1
    new_Ntot = N//Npsf *(N-Npsf) + (N//Npsf - 1 ) * Npsf + (N%Npsf) 
    print(N)
    return(N, new_Ntot)

Npsf = 2
Ntot = 9


Displacement = displacement(Ntot,Npsf)
for i in range(len(Displacement[0])):
     print(Displacement[0][i],Displacement[1][i])
