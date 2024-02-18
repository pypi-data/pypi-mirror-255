import numpy as np
from scipy.optimize import least_squares


def fit_parabola(wavelength, phase):
        def model(x,u):
            return(x[0]*u**2 + x[1]*u + x[2])     
        def fun(x,u,y):
            return(model(x,u) - y)
        def Jac(x,u,y):
            J = np.empty((u.size,x.size))
            J[:,0] = u**2
            J[:,1] = u
            J[:,2] = 1
            return(J)
        t = np.array(wavelength)
        dat = np.array(phase)
        x0 = [1,1,1]
        res = least_squares(fun, x0, jac=Jac, args=(t,dat)) 
        return res.x[0],res.x[1],res.x[2]