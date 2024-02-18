import numpy as np

import Calc as kidcalc
import SC
import scipy.constants as const
from scipy.optimize import minimize_scalar as minisc
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.optimize import curve_fit

class KID(object):


    def __init__(
        self,
        Qc = 2e4,
        hw0 = 5 * 0.6582 * 2 * np.pi, # hbar in µeV so f in GHz
        kbT0 = 0.2 * 86.17, # 86.17 is Boltzmann cte in µeV and 0.2 temperature in K
        kbT = 0.2 * 86.17,
        ak = 0.0268,
        SCvol = SC.Vol(SC.Al,0.05,15.)
                ):
        
        self.SCvol = SCvol
        self.SC = SCvol.SC
        self.d = SCvol.d
        self.V = SCvol.V
        self.tesc = SCvol.tesc
        self.Qc = Qc  # -
        self.hw0 = hw0  # µeV
        self.kbT0 = kbT0  # µeV
        self.kbT = kbT  # µeV
        self.ak = ak  # -
        self.epb = 0.6 - 0.4 * np.exp(-self.tesc / self.SC.tpb)  # Pair breaking effinciency
        # arbitary, see Guruswamy2014 for more details on pair-breaking efficiency

    @property
    def D_0(self):
        """Energy gap at T"""
        return kidcalc.D(self.kbT, self.SC.N0, self.SC.kbTc,self.SC.kbTD)
        
    @property  # takes 1.2s to calculate
    def hwread(self):
        """Gives the read frequency such that it is equal to the resonance
        frequency."""
        return kidcalc.hwread(self.hw0, self.kbT0, self.ak,self.SC.lbd0,self.d,self.D_0,self.SC.D0, self.kbT, self.SC.N0,self.SC.kbTc,self.SC.kbTD)
        
    @property
    def Nqp_0(self):
        """Initial particle number"""
        return self.V * kidcalc.nqp(self.kbT, self.D_0, self.SC.N0)
    
    @property
    def tqp_0(self):
        """"Initial recombinaison time"""
        return (
            self.V
            * self.SC.t0
            * self.SC.N0
            * self.SC.kbTc ** 3
            / (2 * self.D_0 ** 2 * self.Nqp_0)
        )

    @property
    def tqp_1(self):
        return self.tqp_0 * (1 + self.tesc / self.SC.tpb) / 2
    

    @property
    def Qi_0(self):
        """"Initial intern quality factor"""
        hwread = self.hwread
        s_0 = kidcalc.cinduct(hwread, self.D_0, self.kbT)
        return kidcalc.Qi(s_0[0], s_0[1], self.ak,self.SC.lbd0,self.d, self.D_0,self.SC.D0, self.kbT)
    
    @property
    def Q_0(self):
        """"Initial quality factor"""
        return self.Qc * self.Qi_0 / (self.Qc + self.Qi_0)

    @property
    def tres(self):
        return 2 * self.Q_0 / (self.hwread / (const.hbar / const.e * 1e12))

    @property
    def s20(self):
        """Part of the transmission"""
        D_0 = kidcalc.D(self.kbT0, self.SC.N0, self.SC.kbTc,self.SC.kbTD)
        return kidcalc.cinduct(self.hw0, D_0, self.kbT0)[1]
    
    def fit_epb(self, peakdata, wvl, *args, var="phase"):
        """Sets the pair-breaking efficiency to match the maximum of 
        the predicted pulse the highest point of peakdata."""
        peakheight = peakdata.max()
        hwrad = const.Planck / const.e * 1e12 * const.c / (wvl * 1e-3)
        tres = self.tres

        def minfunc(epb, hwrad, tres, var, peakheight):
            self.epb = epb
            _, _, dAtheta = self.calc_respt(hwrad, *args, tStop=3 * tres, points=10)
            if var == "phase":
                return np.abs(dAtheta[1, :].max() - peakheight)
            elif var == "amp":
                return np.abs(dAtheta[0, :].max() - peakheight)

        res = minisc(
            minfunc,
            args=(hwrad, tres, var, peakheight),
            bounds=(0, 1),
            method="bounded",
            options={"maxiter": 5, "xatol": 1e-3},
        )
        self.epb = res.x


    def calc_params(self):
        # R = (2 * self.SC.D0 / self.SC.kbTc) ** 3 / (
        #     2 * self.SC.D0 * 2 * self.SC.N0 * self.SC.t0
        # )  # µs^-1*um^3 (From Wilson2004 or 2.29)   -> recombination constant
        R = 4 * self.SC.D0 ** 2 / (self.SC.N0 * self.SC.t0 * (self.SC.kbTc)**3)
        G_B = 1 / self.SC.tpb  # µs^-1 (From chap8)
        G_es = 1 / self.tesc  # µs^-1 (From chap8)
        N_w0 = R * self.Nqp_0 ** 2 * self.SC.tpb / (2 * self.V)  # arb. Number of quasiparticule in the film at t=0
        return [R, self.V, G_B, G_es, N_w0]
    
    def set_Teff(self, eta, P):
        """Calculates the effective temperature, based on a quasiparticle
        generation term eta*P/D. """
        R, V, G_B, G_es, N_w0 = self.calc_params()
        Nqp0 = np.sqrt(V * ((1 + G_B / G_es) * eta * P / self.D_0 + 2 * G_B * N_w0) / R)
        self.kbT = kidcalc.kbTeff(Nqp0 / self.V, self.SC)


    def rateeq(self, N, t, params):
        """Rate equations (or Rothwarf-Taylor equations) that 
        govern the quasiparticle dynamics."""
        N_qp, N_w = N
        R, V, G_B, G_es, N_w0 = params
        derivs = [
            -R * N_qp ** 2 / V + 2 * G_B * N_w,
            R * N_qp ** 2 / (2 * V) - G_B * N_w - G_es * (N_w - N_w0)
        ]
        return derivs
    

    def calc_Nqpevol(self, dNqp, tStop=None, tInc=None):
        print('calc_Nqpevol')
        # we suppose quasiparticle in the substrat cte
        if tStop is None:
            tStop = 2 * self.tqp_1
        if tInc is None:
            tInc = tStop / 1000
        params = self.calc_params()
        # Initial values
        Nqp_ini = self.Nqp_0 + dNqp
        N_0 = [Nqp_ini, params[-1]]

        # Time array
        t = np.arange(0.0, tStop, tInc)
        return t, odeint(self.rateeq, N_0, t, args=(params,))
    
    def calc_linNqpevol(self, Nqp_ini, tStop=None, tInc=None):
        print('calc_linNqpevol')
        if tStop is None:
            tStop = 2 * self.tqp_1
        if tInc is None:
            tInc = tStop / 1000
        t = np.arange(0.0, tStop, tInc)
        return (Nqp_ini - self.Nqp_0) * np.exp(-t / self.tqp_1)
    
    def calc_resNqpevol(self, t, Nqpt, hwread):
        print('calc_resNqpevol')
        tres = self.tres
        X = np.exp(-t / tres) / np.sum(np.exp(-t / tres))
        dNqpt = np.convolve(Nqpt - self.Nqp_0, X)[: len(t)]
        return dNqpt + self.Nqp_0
    
    def calc_S21(self, Nqp, hwread, s20, dhw=0):
        # print('calc_S21')
        kbTeff = kidcalc.kbTeff(Nqp, self.SC.N0, self.V, self.SC.kbTc, self.SC.kbTD)   #Nqp / self.V
        D = kidcalc.D(kbTeff, self.SC.N0, self.SC.kbTc,self.SC.kbTD)

        s1, s2 = kidcalc.cinduct(hwread + dhw, D, kbTeff)

        Qi = kidcalc.Qi(s1, s2, self.ak,self.SC.lbd0,self.d, D,self.SC.D0, kbTeff)
        
        hwres = kidcalc.hwres(s2, self.hw0, s20, self.ak,self.SC.lbd0,self.d,D,self.D_0, kbTeff)
        return kidcalc.S21(Qi, self.Qc, hwread, dhw, hwres)
    
    def calc_resp(self, Nqp, hwread, s20, D_0, dhw=0):
        # print('calc_resp')
        # Calculate S21
        S21 = self.calc_S21(Nqp, hwread, s20, dhw)
        # Define circle at this temperature:
        s_0 = kidcalc.cinduct(hwread, D_0, self.kbT)
        Qi_0 = kidcalc.Qi(s_0[0], s_0[1], self.ak, self.SC.lbd0, self.d,D_0,self.SC.D0, self.kbT)
        S21min = self.Qc / (self.Qc + Qi_0)  # Q/Qi
        xc = (1 + S21min) / 2
        # translate S21 into this circle:
        dA = 1 - np.sqrt((np.real(S21) - xc) ** 2 + np.imag(S21) ** 2) / (1 - xc)
        theta = np.arctan2(np.imag(S21), (xc - np.real(S21)))
        return S21, dA, theta
    
    def calc_linresp(self, Nqp, hwread, D_0):
        print('calc_linresp')
        s_0 = kidcalc.cinduct(hwread, D_0, self.kbT)
        Qi_0 = kidcalc.Qi(s_0[0], s_0[1], self.ak, self.SC.lbd0, self.d,D_0,self.SC.D0, self.kbT)
        Q = Qi_0 * self.Qc / (Qi_0 + self.Qc)
        beta = kidcalc.beta(self.SC.lbd0,self.d,D_0,self.SC.D0,self.kbT)

        kbTeff = kidcalc.kbTeff(Nqp, self.SC.N0,self.V, self.SC.kbTc,self.SC.kbTD) #N_qp / self.V
        D = kidcalc.D(kbTeff, self.SC.N0, self.SC.kbTc,self.SC.kbTD)
        s1, s2 = kidcalc.cinduct(hwread, D, kbTeff)

        lindA = self.ak * beta * Q * (s1 - s_0[0]) / s_0[1]
        lintheta = -self.ak * beta * Q * (s2 - s_0[1]) / s_0[1]
        return lindA, lintheta
    
    def calc_dNqp(self, hwrad):
        print('calc_dNqp')
        return hwrad/ self.D_0 * self.epb
    

    def calc_respt(self, hwrad, *args, tStop=None, tInc=None, points=50):
        print('calc_respt')
        if tStop is None:
            tStop = self.tqp_1
        if tInc is None:
            tInc = tStop / 100000
        hwread = self.hwread
        s20 = self.s20
        D_0 = self.D_0

        dNqp = self.calc_dNqp(hwrad)

        t, Nqpwt = self.calc_Nqpevol(dNqp, tStop, tInc, *args)
        print(Nqpwt[:,0])
        resNqpt = self.calc_resNqpevol(t, Nqpwt[:, 0], hwread)
        #         mask = np.rint(np.linspace(0,len(t)-1,points)).astype(int)
        mask = np.rint(np.logspace(-1, np.log10(len(t) - 1), points)).astype(int)
        Nqpts = resNqpt[mask]

        ts = t[mask]

        dAtheta = np.zeros((2, len(Nqpts)))
        S21 = np.zeros((len(Nqpts)), dtype="complex")

        for i in range(len(Nqpts)):
            S21[i], dAtheta[0, i], dAtheta[1, i] = self.calc_resp(Nqpts[i], hwread, s20, D_0)
        return ts, S21, dAtheta
    

    # Noise calculation functions
    def calc_respsv(self, plot=False):
        print('calc_respsv')
        hwread = self.hwread
        s20 = self.s20
        D_0 = self.D_0
        Nqp_0 = self.Nqp_0

        dNqp = Nqp_0 * 1e-2
        Nqparr = np.arange(Nqp_0 - 10 * dNqp, Nqp_0 + 10 * dNqp, dNqp)
        S21 = np.zeros(len(Nqparr), dtype=np.complex64)
        dA = np.zeros(len(Nqparr))
        theta = np.zeros(len(Nqparr))
        for i in range(len(Nqparr)):
            dA[i], theta[i] = self.calc_linresp(Nqparr[i], hwread, D_0)
        dAspl = interpolate.splrep(Nqparr, dA, s=20)
        thetaspl = interpolate.splrep(Nqparr, theta, s=20)
        dAdNqp = interpolate.splev(Nqp_0, dAspl, der=1)
        dThetadNqp = interpolate.splev(Nqp_0, thetaspl, der=1)
        if plot:
            Nqpspl = np.linspace(Nqparr.min(), Nqparr.max(), 100)
            plt.figure()
            plt.plot(Nqparr, dA, "bo")
            plt.plot(Nqpspl, interpolate.splev(Nqpspl, dAspl), "b-")
            plt.xlabel("$N_{qp}$")
            plt.ylabel("$dA$", color="b")
            plt.twinx()
            plt.plot(Nqparr, theta, "ro")
            plt.plot(Nqpspl, interpolate.splev(Nqpspl, thetaspl), "r-")
            plt.ylabel("$\\theta$", color="r")
            plt.tight_layout()
        return dAdNqp, dThetadNqp

    # def calc_SATheta(self, fstart=1e0, fstop=1e6, points=200):
    #     print('calc_SATheta')
    #     dAdNqp, dThetadNqp = self.calc_respsv()

    #     f = np.logspace(np.log10(fstart), np.log10(fstop), points)
    #     Sn = (
    #         4
    #         * self.Nqp_0
    #         * self.tqp_1
    #         * 1e-6
    #         / (1 + (2 * np.pi * f * self.tqp_1 * 1e-6) ** 2)
    #     )
    #     Sat = Sn * dAdNqp * dThetadNqp / (1 + (2 * np.pi * f * self.tres * 1e-6) ** 2)
    #     return f, Sat
    
    def plot_S21resp(self, hwrad, tStop=None, tInc=None, points=20):
        print('plot_S21resp')
        plt.figure(figsize=(5, 5))
        self.plot_freqsweep()
        ts, S21, dAtheta = self.calc_respt(hwrad, tStop=tStop, tInc=tInc, points=points)

        plt.plot(np.real(S21), np.imag(S21), ".b")


    def plot_freqsweep(self, start=None, stop=None, points=20):
        print('plot_freqsweep')
        hwread = self.hwread
        D_0 = self.D_0
        s20 = self.s20

        s_0 = kidcalc.cinduct(hwread, D_0, self.kbT)
        Qi_0 = kidcalc.Qi(s_0[0], s_0[1], self.ak, self.SC.lbd0, self.d,D_0,self.SC.D0, self.kbT)
        Q = Qi_0 * self.Qc / (Qi_0 + self.Qc)
        S21min = self.Qc / (self.Qc + Qi_0)  # Q/Qi
        xc = (1 + S21min) / 2
        if start is None:
            start = -self.hw0 / Q * 2
        if stop is None:
            stop = self.hw0 / Q * 2

        for dhw in np.linspace(start, stop, points):
            S21_0 = self.calc_S21(self.Nqp_0, hwread, s20, dhw=dhw)
            plt.plot(np.real(S21_0), np.imag(S21_0), "r.")
        plt.plot(xc, 0, "kx")
        plt.plot(S21min, 0, "gx")

    def plot_resp(self, hwrad, tStop=None, tInc=None, points=50, plot="all"):
        print('plot_resp')
        ts, S21, dAtheta = self.calc_respt(hwrad, tStop=tStop, tInc=tInc, points=points)
        if plot == "all" or "S21" in plot:
            plt.figure(1, figsize=(5, 5))
            # self.plot_freqsweep()
            plt.plot(np.real(S21), np.imag(S21), ".b")
            plt.xlabel(r"$Re(S_{21})$")
            plt.ylabel(r"$Im(S_{21})$")
        if plot == "all" or "Amp" in plot:
            plt.figure(2)
            print(max(dAtheta[0,:]))
            plt.plot(ts, dAtheta[0, :])
            plt.xlabel("t (µs)")
            plt.ylabel(r"$\delta A$")
            plt.yscale("log")
        if plot == "all" or "Phase" in plot:
            plt.figure(3)
            print(max(dAtheta[1,:]) * 180 / np.pi)
            print(max(dAtheta[0,:]))
            plt.plot(ts, dAtheta[1, :])
            plt.xlabel("t (µs)")
            plt.ylabel(r"$\theta$")
        if plot == "all" or "Nqp" in plot:
            plt.figure(4)
            self.plot_Nqpt(hwrad, tStop, tInc)
            plt.ylabel(r"$\delta N_{qp}$")
            plt.xlabel("t (µs)")
            plt.yscale("log")


    def plot_Nqpt(
        self,
        hwrad,
        tStop=None,
        tInc=None,
        plot_phonon=True,
        fit_secondhalf=False,
        plot_lin=True,
    ):
        print('plot_Nqpt')
        if tStop is None:
            tStop = 2 * self.tqp_1
        if tInc is None:
            tInc = tStop / 1000

        Nqp_ini = self.Nqp_0 + self.calc_dNqp(hwrad)

        t, Nqpevol = self.calc_Nqpevol(self.calc_dNqp(hwrad), tStop, tInc)
        Nqpt = Nqpevol[:, 0]
        Nwt = Nqpevol[:, 1]

        plt.plot(t, Nqpt - self.Nqp_0,label='Nqpt-Nqp_0')
        plt.yscale("log")

        if plot_lin:
            Nqptlin = self.calc_linNqpevol(Nqp_ini, tStop, tInc)
            plt.plot(t, Nqptlin,label = 'Nqpt_lin')

        if fit_secondhalf:
            fit = curve_fit(
                lambda x, a, b: b * np.exp(-x / a),
                t[np.round(len(t) / 2).astype(int) :],
                Nqpt[np.round(len(t) / 2).astype(int) :] - self.Nqp_0,
                p0=(self.tqp_0, Nqp_ini - self.Nqp_0),
            )
            print(fit[0][0])
            plt.plot(t, fit[0][1] * np.exp(-t / fit[0][0]))

        if plot_phonon:
            plt.figure()
            plt.plot(t, Nwt)
            plt.yscale("log")