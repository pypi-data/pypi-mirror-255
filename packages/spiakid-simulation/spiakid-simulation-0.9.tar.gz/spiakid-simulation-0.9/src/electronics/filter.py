import numpy as np
from scipy import signal as sg
import scipy as sp

def psd(Noise,nperseg):

    dim = np.shape(Noise)
    psd_phase = np.zeros(dim,dtype = object)
    # psd_amp = np.zeros(dim,dtype = object)
    for i in range(dim[0]):
        for j in range(dim[1]):
            psd_phase[i,j] = sg.welch(Noise[i,j][1]-np.mean(Noise[i,j][1]), fs = 1/(Noise[i,j][0][1]-Noise[i,j][0][0]), nperseg=nperseg)

    return(psd_phase)

def template(Noise, decay, template_time, trigerinx, point_nb):
    
    dim = np.shape(Noise)
    templ = np.zeros(dim,dtype = object)
    t = np.linspace(0,template_time,point_nb)
    for i in range(dim[0]):
        for j in range(dim[1]):
            templ[i,j] = np.zeros(len(t))
            templ[i,j][trigerinx:] = -np.exp(decay * (t[trigerinx:]-t[trigerinx]))

    return(templ)


def filter_creation(Noise, template, psd):
    dim = np.shape(Noise)
    wifilter = np.zeros(dim,dtype = object)

    for i in range(dim[0]):
        for j in range(dim[1]):
            wifilter[i,j] = wiener(template[i,j], psd[i,j][1], (len(psd[i,j][1])-1)*2)
    return(wifilter)

def covariance_from_psd(psd, size=None, window=None, dt=1.):
    autocovariance = np.real(np.fft.irfft(psd / 2., window) / dt)  # divide by 2 for single sided PSD
    if size is not None:
        autocovariance = autocovariance[:size]
    covariance = sp.linalg.toeplitz(autocovariance)
    return covariance

def filter_cutoff(filter_, cutoff):
    """
    This function addresses a problem encountered when generating filters from
    oversampled data. The high frequency content of the filters can be
    artificially large due to poor estimation of the noise and template.

    In this case it is useful to remove frequencies above the cutoff from the
    filter. Only use this function when addressing the above issue and if the
    majority of the signal frequencies are < cutoff.

    It is best to avoid this procedure if possible since removing the high
    frequency content will artificially make the filter periodic, throws away
    some information in the signal, and may negatively influence some of the
    intended filter properties.
    """
    freq = np.fft.rfftfreq(filter_.shape[0], d=1)
    filter_fft = np.fft.rfft(filter_, axis=0)
    filter_fft[freq > cutoff, ...] = 0
    filter_ = np.fft.irfft(filter_fft, filter_.shape[0], axis=0)
    return filter_

def wiener(*args, **kwargs):
    """
    Create a filter that minimizes the chi squared statistic when aligned
    with a photon pulse.

    Args:
        template:  numpy.ndarray
            The template with which to construct the filter.
        psd:  numpy.ndarray
            The power spectral density of the noise.
        nwindow: integer
            The window size used to compute the PSD.
        nfilter: integer (optional)
            The number of taps to use in the filter. The default is to use
            the template size.
        cutoff: float (optional)
            Set the filter response to zero above this frequency (in units of
            1 / dt). If False, no cutoff is applied. The default is False.
        fft: boolean (optional)
            If True, the filter will be computed in the Fourier domain, which
            could be faster for very long filters but will also introduce
            assumptions about periodicity of the signal. In this case, the
            psd must be the same size as the filter Fourier transform
            (nfilter // 2 + 1 points). The default is False, and the filter is
            computed in the time domain.
        normalize: boolean (optional)
            If False, the template will not be normalized. The default is True
            and the template is normalized to a unit response.
    Returns:
        filter_: numpy.ndarray
            The computed wiener filter.
    """
    # collect inputs
    template, psd, nwindow = args[0], args[1], args[2]
    nfilter = kwargs.get("nfilter", len(template))
    cutoff = kwargs.get("cutoff", False)
    fft = kwargs.get("fft", True)
    normalize = kwargs.get("normalize", True)

    # need at least this long of a PSD
    if nwindow < nfilter:
        raise ValueError("The psd must be at least as long as the length of the FFT of the filter")

    # pad the template if it's shorter than the filter (linear ramp to avoid discontinuities)
    if nfilter > len(template):
        template = np.pad(template, (0, nfilter - len(template)), mode='linear_ramp')
    # truncate the template if it's longer than the filter
    elif nfilter < len(template):
        template = template[:nfilter]

    if fft:  # compute the filter in the frequency domain (introduces periodicity assumption, requires nwindow=nfilter)
        if nwindow != nfilter:
            raise ValueError("The psd must be exactly the length of the FFT of the filter to use the 'fft' method.")
        template_fft = np.fft.rfft(template)
        filter_ = np.fft.irfft(np.conj(template_fft) / psd, nwindow)  # must be same size else ValueError
        filter_ = np.roll(filter_, -1)  # roll to put the zero time index on the far right
    else:  # compute filter in the time domain (nfilter should be << nwindow for this method to be better than fft)
        covariance = covariance_from_psd(psd, size=nfilter, window=nwindow)
        filter_ = np.linalg.solve(covariance, template)[::-1]

    # remove high frequency filter content
    if cutoff:
        filter_ = filter_cutoff(filter_, cutoff)

    # normalize
    if normalize:
        filter_ /= -np.matmul(template, filter_[::-1])
    else:
        filter_ *= -1   # "-" to give negative pulse heights after filtering
    return filter_


def filtering(Signal, filter):
    dim = np.shape(Signal)
    sig = np.zeros_like(Signal,dtype = object)
    for i in range(dim[0]):
        for j in range(dim[1]):
            sig[i,j] = [Signal[i,j][0],sg.lfilter(filter[i,j],1,Signal[i,j][1])]


    return(sig)