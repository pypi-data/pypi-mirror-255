import os
import numpy as np
import scipy.integrate as integrate
from scipy import interpolate
from scipy.optimize import minimize_scalar as minisc
import warnings

def f(E, kbT):
    '''The Fermi-Dirac distribution.'''
    with np.errstate(over='raise',under='ignore'):
        try:
            return 1 / (1 + np.exp(E/kbT))
        except FloatingPointError: #use low temperature approx. if normal fails.
            return np.exp(-E/kbT)
        

def D(kbT, N0, kbTc, kbTD,kb=86.17):
    '''Calculates the thermal average energy gap, Delta. Tries to load Ddata, 
    but calculates from scratch otherwise. Then, it cannot handle arrays.  '''

    warnings.warn('D takes long.. \n N0={}\n kbTD={}\n Tc={}'.format(N0,kbTD,kbTc/kb))
    _Vsc = Vsc(kbTc,N0,kbTD)
    def integrandD(E, D, kbT, N0, _Vsc):
            return N0 * _Vsc * (1 - 2 * f(E, kbT)) / np.sqrt(E ** 2 - D ** 2)

    def dint(D, kbT, N0, _Vsc, kbTD):
            return np.abs(
                integrate.quad(integrandD, D, kbTD,
                               args=(D, kbT, N0, _Vsc))[0] - 1
            )

    res = minisc(dint, args=(kbT, N0, _Vsc, kbTD))
    if res.success:
        return np.clip(res.x,0,None)


def Vsc(kbTc,N0,kbTD):
    '''Calculates the superconducting coupling strength in BSC-theory 
    from the BSC relation 2D=3.52kbTc.'''
    D0 = 1.76*kbTc # BSC-relation
    def integrand1(E, D):
        return 1/np.sqrt(E**2-D**2)
    return 1/(integrate.quad(integrand1, D0, kbTD,args=(D0,))[0]*N0)


def hwread(hw0, kbT0, ak, lbd0, d, D_, D0, kbT, N0, kbTc, kbTD):
    '''Calculates at which frequency, on probes at resonance. 
    This must be done iteratively, as the resonance frequency is 
    dependent on the complex conductivity, which in turn depends on the
    read frequency.'''
    D_0 = D(kbT0, N0, kbTc, kbTD)
    s20 = cinduct(hw0, D_0, kbT0)[1]

    def minfuc(hw, hw0, s20, ak, lbd0, d, D_, D0, kbT):
        s1, s2 = cinduct(hw, D_, kbT)
        return np.abs(hwres(s2, hw0, s20, ak, lbd0, d, D_, D0, kbT) - hw)

    res = minisc(
        minfuc,
        bracket=(.5*hw0,hw0,2*hw0),
        args=(hw0, s20, ak, lbd0, d, D_, D0, kbT),
        method="brent",
        options={"xtol": 1e-21},
    )
    if res.success:
        return res.x
    

def hwres(s2, hw0, s20, ak, lbd0, d, D, D0, kbT):
    '''Gives the resonance frequency in µeV, from the sigma2,
    from a linearization from point hw0,sigma20. See PdV PhD eq. (2.24)'''
    b = beta(lbd0, d, D, D0, kbT)
    return hw0 * (
        1 + ak * b / 4 / s20 * (s2 - s20)
    )  # note that is a linearized approach

def beta(lbd0, d, D, D0, kbT):
    '''calculates beta, a measure for how thin the film is, 
    compared to the penetration depth.
    d -- film thickness
    D -- energy gap
    D0 -- energy gap at T=0
    kbT -- temperature in µeV'''
    lbd = lbd0 * 1 / np.sqrt(D / D0 * np.tanh(D / (2 * kbT)))
    return 1 + 2 * d / (lbd * np.sinh(2 * d / lbd))

def cinduct(hw, D, kbT):
    '''Mattis-Bardeen equations.'''
    def integrand11(E, hw, D, kbT):
        nume = 2 * (f(E, kbT) - f(E + hw, kbT)) * (E ** 2 + D ** 2 + hw * E)
        deno = hw * ((E ** 2 - D ** 2) * ((E + hw) ** 2 - D ** 2)) ** 0.5
        return nume / deno
        
    def integrand12(E, hw, D, kbT):
        nume = (1 - 2 * f(E + hw, kbT)) * (E ** 2 + D ** 2 + hw * E)
        deno = hw * ((E ** 2 - D ** 2) * ((E + hw) ** 2 - D ** 2)) ** 0.5
        return nume / deno

    def integrand2(E, hw, D, kbT):
        nume = (1 - 2 * f(E + hw, kbT)) * (E ** 2 + D ** 2 + hw * E)
        deno = hw * ((D ** 2 - E ** 2) * ((E + hw) ** 2 - D ** 2)) ** 0.5
        return nume / deno

    s1 = integrate.quad(integrand11, D, np.inf, args=(hw, D, kbT))[0]
    if hw > 2 * D:
        s1 -= integrate.quad(integrand12, D - hw, -D, args=(hw, D, kbT))[0]
    s2 = integrate.quad(integrand2, np.max(
        [D - hw, -D]), D,args=(hw, D, kbT))[0]
    return s1,s2


def nqp(kbT, D, N0):
    '''Thermal average quasiparticle denisty. It can handle arrays 
    and uses a low temperature approximation, if appropriate.'''
    if (kbT<D/20).all():
        return 2*N0*np.sqrt(2*np.pi*kbT*D)*np.exp(-D/kbT)
    else:
        def integrand(E, kbT, D, N0):
            return 4 * N0 * E / np.sqrt(E ** 2 - D ** 2) * f(E, kbT)
        if any([type(kbT) is float, type(D) is float,
               type(kbT) is np.float64, type(D) is np.float64]):#make sure it can deal with kbT,D arrays
            return integrate.quad(integrand, D, np.inf, args=(kbT, D, N0))[0]
        else:
            assert (kbT.size == D.size),'kbT and D arrays are not of the same size'
            result = np.zeros(len(kbT))
            for i in range(len(kbT)):
                result[i] = integrate.quad(
                    integrand, D[i], np.inf, args=(kbT[i], D[i], N0))[0]
            return result
        

def Qi(s1, s2, ak, lbd0, d, D, D0, kbT):
    '''Calculates the internal quality factor, 
    from the complex conductivity. See PdV PhD thesis eq. (2.23)'''
    b = beta(lbd0, d, D, D0, kbT)
    return 2 * s2 / (ak * b * s1)


def S21(Qi, Qc, hwread, dhw, hwres):
    '''Gives the complex transmittance of a capacatively coupled
    superconducting resonator (PdV PhD, eq. (3.21)), with:
    hwread -- the read out frequency
    dhw -- detuning from hwread (so actual read frequency is hwread + dhw)
    hwres -- resonator frequency'''
    Q = Qi * Qc / (Qi + Qc)
    dhw += hwread - hwres
    return (Q / Qi + 2j * Q * dhw / hwres) / (1 + 2j * Q * dhw / hwres)



def kbTeff(N_qp, N0, V, kbTc, kbTD):
    '''Calculates the effective temperature (in µeV) at a certain 
    number of quasiparticles.'''
    # Ddata = load_Ddata(N0,kbTc,kbTD)
    # if Ddata is not None:
    #     kbTspl = interpolate.splrep(Ddata[2,:],Ddata[0,:])
    #     return interpolate.splev(N_qp/V,kbTspl)
    # else:
    def minfunc(kbT, N_qp, N0, V, kbTc, kbTD):
            Dt = D(kbT, N0, kbTc, kbTD)
            return np.abs(nqp(kbT, Dt, N0) - N_qp/V)
    res = minisc(
            minfunc,
            bounds = (0,1*86.17),
            args=(N_qp, N0, V, kbTc, kbTD), 
            method="bounded",
            options = {'xatol':1e-15}
        )
    if res.success:
            return res.x