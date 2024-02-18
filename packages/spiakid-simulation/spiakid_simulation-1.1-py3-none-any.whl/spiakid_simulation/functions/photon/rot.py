import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate


def rotation(lat_tel,coo_guide,coo_star,time,size):
  # omega = -7.2921 * 10 **-5 # radian/sec
  omega = 7.292115 * 10**-5 
  t = np.linspace(0,time,time * 10)
  alt, az = coo_guide
  X0, Y0, Z0 = [np.cos(alt)*np.cos(az), -np.cos(alt)*np.sin(az), np.sin(alt)]
  coo_guide = np.array([X0,Y0,Z0])
  # print('coo_guide: ',coo_guide)
  R_inv = np.array([[-X0*Z0/np.sqrt((X0**2+Y0**2)*(X0**2+Y0**2+Z0**2)), Y0/np.sqrt(X0**2+Y0**2), X0/np.sqrt(X0**2+Y0**2+Z0**2)],
                  [-Y0*Z0/np.sqrt((X0**2+Y0**2)*(X0**2+Y0**2+Z0**2)), -X0/np.sqrt(X0**2+Y0**2), Y0/np.sqrt(X0**2+Y0**2+Z0**2)],
                  [np.sqrt(X0**2+Y0**2)/np.sqrt((X0**2+Y0**2+Z0**2)), 0, Z0/np.sqrt(X0**2+Y0**2+Z0**2)]])
  new_pos_x = np.zeros(len(t))
  new_pos_y = np.zeros(len(t))
  alt_ev = np.zeros(len(t))
  for i in range (len(t)):
    normalisation = 2 * size
    coo = [coo_star[1]/normalisation,coo_star[2]/normalisation]

    z = np.sqrt(1-coo[0]**2 - coo[1]**2)

    coo.append(z)
    # print('coo_star: ',coo_star)
    r1_prime = np.array(coo) - np.array([0,0,1])
    # print('r1_prime:' ,r1_prime)
    r1   = R_inv@r1_prime 
    # print('r1: ',r1)
    coo_star_XYZ = r1 + coo_guide

    theta = omega * t[i]

    Up = np.array([[np.cos(lat_tel)**2 + np.sin(lat_tel)**2 * np.cos(theta), -np.sin(lat_tel) * np.sin(theta), (1-np.cos(theta))*np.cos(lat_tel)*np.sin(lat_tel)],
                [np.sin(lat_tel) * np.sin(theta), np.cos(theta), -np.cos(lat_tel) * np.sin(theta)],
                [(1-np.cos(theta))*np.cos(lat_tel)*np.sin(lat_tel), np.cos(lat_tel)*np.sin(theta), np.sin(lat_tel)**2+np.cos(lat_tel)**2*np.cos(theta)]])

    pos_guide_t = Up@coo_guide
    pos_star_t = Up@coo_star_XYZ
    X0_t = pos_guide_t[0]
    Y0_t = pos_guide_t[1]
    Z0_t = pos_guide_t[2]

    r1 = pos_star_t - pos_guide_t


    R_t = np.array([[-X0_t*Z0_t/np.sqrt((X0_t**2+Y0_t**2)*(X0_t**2+Y0_t**2+Z0_t**2)), -Y0_t*Z0_t/np.sqrt((X0_t**2+Y0_t**2)*(X0_t**2+Y0_t**2+Z0_t**2)), np.sqrt(X0_t**2 + Y0_t**2)/np.sqrt(X0_t**2+Y0_t**2+Z0_t**2)],
              [Y0_t/np.sqrt(X0_t**2 + Y0_t**2), -X0_t/np.sqrt(X0_t**2+Y0_t**2), 0],
              [X0_t/np.sqrt(X0_t**2 + Y0_t**2 + Z0_t**2), Y0_t/np.sqrt(X0_t**2 + Y0_t**2 + Z0_t**2), Z0_t/np.sqrt(X0_t**2 + Y0_t**2 + Z0_t**2)]])

    res = R_t@r1
    norm = np.sqrt(res[0]**2+res[1]**2)
    angle = np.arctan2(res[1],res[0])
    x = norm * np.cos(angle)
    y = norm * np.sin(angle)
    new_pos_x[i] = x * normalisation
    new_pos_y[i] = y * normalisation
    alt_ev[i] = np.arcsin(Z0_t)
    # print(new_pos)

  new_pos_func_x = interpolate.interp1d(t,new_pos_x)
  new_pos_func_y = interpolate.interp1d(t,new_pos_y)
  new_pos = (new_pos_func_x,new_pos_func_y)
  alt_func = interpolate.interp1d(t,alt_ev)
  return(new_pos,alt_func)