import sys
sys.path.append('EMG_Explorer_App/Explorer_package/summary_measurement')

from requirement_time_domain import *

try:
    from numpy.lib.stride_tricks import sliding_window_view
except ImportError:
    sliding_window_view = None

# from pyemgsp import __version__

__author__ = "Jeremy Laforet"
__copyright__ = "Jeremy Laforet"
__license__ = "mit"

# _logger = logging.getLogger(__name__)
# logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
# logging.basicConfig(stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S")

# Note:Function initially implemented by arrays of 64/128, but we just need to implement the function for one row/column


def general_stats(signals):
    """
    Compute various metrics describing the signals.

    :param signals: an array of signals
    :return
    mean (float) – Mean of the signal.
    median (float) – Median of the signal.
    max (float) – Maximum signal amplitude.
    var (float) – Signal variance (unbiased).
    std_dev (float) – Standard signal deviation (unbiased).
    abs_dev (float) – Absolute signal deviation.
    kurtosis (float) – Signal kurtosis (unbiased).
    skew (float) – Signal skewness (unbiased).:
    """

    return numpy.apply_along_axis(biosppy.signals.tools.signal_stats, signals, axis=0)


def mean(signals):
    """
    Compute the mean of the signals
    :param signals: an array of equally long signals
    :return: the mean of each signal
    """
    return numpy.mean(signals, axis=-1)


def variance(signals):
    """
    Compute the variance of the signals
    :param signals: an array of equally long signals
    :return: the variance of each signal
    """
    return numpy.var(signals, axis=-1)


def kurtosis(signals):
    """
    Compute the excess kurtosis of the signals
    :param signals: an array of equally long signals
    :return:
    """
    return st.kurtosis(signals, axis=-1)


def skewness(signals):
    """
    Compute the skewness of the signals
    :param signals: an array of equally long signals
    :return: the skewness of each signal
    """
    return st.skew(signals, axis=-1)


def arv(signals):
    """
    Compute the Average Rectified Value of the signals
    :param signals: an array of equally long signals
    :return Signal's ARV:
    """

    return numpy.mean(numpy.abs(signals), axis=-1)


def rmsa(signals):
    """
    Compute the Root Mean Square of signal Amplitude from Phyomark et al. 2012
    :param signals: an array of equally long signals
    :return signal's rmsA:
    """
    #return numpy.mean(signals, axis=-1)
    return numpy.sqrt(numpy.mean((signals ** 2), axis=-1))
    '''
    rmsas = []
    for i in range(signals.shape[0]):
        rmsas.append(biosppy.signals.tools.rms_error(2 * signals[i], signals[i])[0])
    return rmsas'''


def iemg(signals):
    """
    Computes Integrated EMG signal Phyomark et al. 2012
    (IEMG = sum (|x{i}| for i:1..N, x: electrode signal, N: number of electrodes)
    :param signals: an array of equally long signals
    :return signal's IENG:
    """
    return numpy.sum(numpy.abs(signals), axis=-1)


def ssi(signals):
    """
    Computes the Simple Square Integrated (SSI) Spiewak et al. 2018
    (SSI = sum (|x{i}|²) for i:1..N, x: electrode signal, N: number of electrods) .
    :param signals: an array of equally long signals
    :return Signal's SSI:
    """
    return numpy.sum(numpy.square(numpy.abs(signals)), axis=-1)


def mav(signals):
    """
    Compute the average of os the Hd-sEMG signal Amplitude
    mav = 1/l * sum(|xi|) for i = {1,...,l}
    l: length of electrode signal
    :param signals: an array of equally long signals
    :return The mean MAV over the N electrode signals:
    """

    """for a one dimensional array, it is the same formula as ARV"""

    return numpy.mean(numpy.abs(signals), axis=-1)


def emg_min(signals):
    """
    Find the minimum of the signal, indexe and value
    :param signals: an array of equally long signals
    :return minimum's value and index of the input signal
    """
    e_min = []
    for s in signals:
        min = numpy.apply_along_axis(
            biosppy.signals.tools.find_extrema, 0, s, mode="min"
        )
        e_min.append(numpy.min(min[1]))
    return e_min
    #return numpy.apply_along_axis(
    #    biosppy.signals.tools.find_extrema, 0, signals, mode="min"
    #)


def emg_max(signals):
    """
    Find the maximum of the signal, indexe and value
    :param signals: an array of equally long signals
    :return maximum's value and index of the input signal
    """
    e_max = []
    for s in signals:
        max = numpy.apply_along_axis(
            biosppy.signals.tools.find_extrema, 0, s, mode="max"
        )
        e_max.append(numpy.max(max[1]))
    return e_max
    #return numpy.apply_along_axis(
    #    biosppy.signals.tools.find_extrema, 0, signals, mode="max"
    #)


def wave_length(signals):
    """
    Compute the waves length among an emg signal,
     sum(|x(i+1) - x(i)|) for i in length of one electrode raw signal
    :param signals: an array of equally long signals
    :return: signal's Wave length:
    """

    s1 = signals[:, 1 : signals.shape[1]]
    s2 = signals[:, 0 : signals.shape[1] - 1]

    return numpy.sum(numpy.abs(s1 - s2), axis=-1)


# for two dimensional array, array of several signals
def aac(signal):
    """
    Compute the Average Amplitude Change (AAC), from Phyomark et al. 2012 study.
    aac = 1/l * sum(|x(i+1) - xi|) for i ={1,...,l}
    AAC = 1/N * sum(aac{j}) for j = {1,...,N}
    l: length of electrode signal
    N: Number of electrodes
    :param signal: The N electrode signals
    :return: The mean AAC over the N electrode signals
    """
    wl_electrode = []
    for s in signal:
        #s1 = s[1 : len(signal)]
        s1 = s[1 : len(s)]
        #s2 = s[0 : len(signal) - 1]
        s2 = s[0 : len(s) - 1]
        wl_electrode.append(numpy.mean(numpy.abs(s1 - s2)))
    return wl_electrode
    #return numpy.mean(wl_electrode)


def dasdv(signal):
    """

    Compute the Difference Absolute Standard Deviation value, from Phyomark et al. 2012 study.
    dasdv = sqrt( (1 / (l-1)) * sum((x[i+1] - x[i])**2 ) for i ={1,...,l}
    DASDV = 1/N * sum(dasdv{j}) for j = {1,...,N}
    l: length of electrode signal
    N: Number of electrodes
    :param signal: The N electrode signals
    :return: The mean DASDV over the N electrode signals
"""
    dasdv_electrode = []
    for s in signal:
        #s1 = s[1 : len(signal)]
        s1 = s[1 : len(s)]
        #s2 = s[0 : len(signal) - 1]
        s2 = s[0 :len(s) - 1]
        dasdv_electrode.append(numpy.mean((s1 - s2) ** 2))
    return(dasdv_electrode)
    #return numpy.mean(dasdv_electrode)


def wilson_amp(signals):
    """
    Compute the Wilson amplitude, from Phyomark et al. 2012 study.
    W_a = sum( f(|x[i] - x[i+1]|)) for i = {1,...,l-1}
    f(x){
            1 if x >= threshold
            0 otherwise
        }
    l: length of electrode signal
    :param signals: an array of equally long signals
    :return The signal's Wilson Amplitude:
    """
    threshold = numpy.mean(signals[:,], axis=-1).reshape(signals.shape[0], 1)
    s1 = signals[:, 1 : signals.shape[1]]
    s2 = signals[:, 0 : signals.shape[1] - 1]
    x = numpy.abs(s2 - s1)

    return numpy.sum(x >= threshold, axis=-1)


def myopulse_rate(signals):  # Note : original file, divide by l in formula, not in algo
    """
        Compute the Myopoulse percentage rate, from Phyomark et al. 2012 study.
        myo_r = 1/l * sum(f(x[i])) for i = {1,...,l}
        f(x){
                1 if x >= threshold
                0 otherwise
            }
        l: length of electrode signal
        :param signals: an array of equally long signals
        :return:
    """
    return numpy.mean(
        signals >= numpy.mean(signals, axis=-1).reshape(signals.shape[0], 1), axis=-1
    )


def mav_modified1(
    signals
):  # Note : original description does not match with th pysiology description
    """
        This function evaluate Average of EMG signal Amplitude, using the modified version n°.1.::

            IEMG = 1/N * sum(wi|xi|) for i = 1 --> N
            wi = {
                  1 if 0.25N <= i <= 0.75N,
                  0.5 otherwise
                  }

        * Input:
            * raw EMG Signal as list
        * Output:
            * Mean Absolute Value

        :param signals: an array of signals
        :return: the MAV (modified version n. 1)  of the EMG Signal
        :rtype: float
    """

    return numpy.apply_along_axis(pysiology.electromyography.getMAV1, 1, signals)


def mav_modified2(
    signals
):  # Note : original description does not match with th pysiology description
    """
        This function evaluate Average of EMG signal Amplitude, using the modified version n°.2.::

            IEMG = 1/N * sum(wi|xi|) for i = 1 --> N
            wi = {
                  1 if 0.25N <= i <= 0.75N,
                  4i/N if i < 0.25N
                  4(i-N)/N otherwise
                  }

        * Input:
            * raw EMG Signal as list
        * Output:
            * Mean Absolute Value

        :param signals: an array of signals
        :return: the MAV (modified version n. 2)  of the EMG Signal
        :rtype: float
    """
    return numpy.apply_along_axis(pysiology.electromyography.getMAV2, 1, signals)


def zero_crossing_count(signals):
    """
        Compute the number of times a signal crosses the 0 axis.
        :param signals: an array of equally long signals
        :return Signal's zero crossing:
    """
    return ((signals[:, :-1] * signals[:, 1:]) < 0).sum(axis=-1)


def samp_ent(signal):
    """
    dummy feature extraction function which just returns the signal samp_entropy.
    :param signal: which is a single row/column array:
    :return signal's samp_ent:
    """

    return [ant.sample_entropy(s, order=2) for s in signal]
    #return numpy.mean(
    #   [pyeeg.samp_entropy(signal[i], 2, 0.2 * numpy.std(signal[i])) for i in signal]
    #)

def amp_ent(signal):
    """
    dummy feature extraction function which just returns the signal approximate entropy.
    :param signal: which is a single row/column array:
    :return signal's amp_ent:
    """
    return [ant.app_entropy(s, order=2) for s in signal]
    #return numpy.mean(
    #    [pyeeg.ap_entropy(signal[i], 2, 0.2 * numpy.std(signal[i])) for i in signal]
    #)

def trev(signal):
    """
    Computes time reversibility of signal (d: delay). Investigate the nonlinear characteristic of EMG siganal.
    T_rev(d) = (1/(l - d)) * sum{(x[i] - x[i - d]) ** 3} for i = {d + 1,...,l}
    l: signal length
    d: delay (d = 1, common choice from Hassan et al. 2011 study.
    :param signal: which is a single row/column array:
    :return signal's time reversibility:
    """
    tau = 1
    return numpy.mean(numpy.power(signal[:, tau:] - signal[:, :-tau], 3), axis=-1)

def dfa(signals):
    """
    Computes detrented fluctuation analysis of signals.
    Non linear measure for dynamic systems
    :param signal: an array of signals
    :return signal's alpha for the Hurst parameter:
    """

    return numpy.apply_along_axis(nolds.dfa, 1, signals)#, numpy.apply_along_axis(pyeeg.dfa, 1, signals)


def lyapunov_exp(signals):
    """
    Compute the liapunov exponents/ quantifies the stability or instability of the signals.
    Non linear measure for dynamic systems
    Eckmann et al :
    lya_exp = lim(lim((1/t)*(log(norm(delta_yt)/norm(delta_y0))))) when t->infinity and norm(delta_yo)->0
    yt : state of system at time t
    y0 : state of system at time 0
    delta : euclidean distance
    :param signal: an array of signals
    :return maximal exponent of each signal
    """
    return numpy.apply_along_axis(nolds.lyap_r, 1, signals)

def mean_dvv(signals):
    return numpy.apply_along_axis(pydvv, 1, signals,m=2,Ntv=50,nd=3,Nsub=200)

def pydvv(X,m=4,Nsub=200,nd=2.0,Ntv=None,tau=1,mean_output=True):
    if sliding_window_view:
        if not Ntv:
            Ntv=25*nd

        y=numpy.zeros((int(Ntv),1))

        X_slided = sliding_window_view(X,m*tau-(tau-1))[:-1,::tau]
        N=X_slided.shape[0]

        ref_idx = numpy.empty((Nsub,m),dtype=int)
        ref_idx[:,0] = numpy.random.randint(N,size=Nsub)
        for col in range(1,m):
            ref_idx[:,col]=ref_idx[:,col-1]+tau

        Xrd=numpy.take(X,ref_idx)#
        d=ssp.distance.cdist(X_slided,Xrd)#
        acc=d.sum()
        count=numpy.count_nonzero(d)

        variance = numpy.sqrt(((d[d.nonzero()]-acc/count)**2).sum()/(count-1))

        # Calculates the range vector consisting of Ntv equally spaced regions
        rd = d.sum()/numpy.count_nonzero(d) - (nd * variance) + (((2 * nd) * variance) * numpy.arange(Ntv)) / (Ntv - 1)
        y[rd<=0] = numpy.nan

        for n in numpy.where(rd>0)[0]:
            tot = 0
            countt = 0
            for k in range(Nsub):
                IND = numpy.where(d[:, k - 1] <= rd[n])[0]+ (m * tau)

                IND = IND[IND != k]
                # sets have atleast 30 DVs
                if (IND.shape[0] >= 30):
                    tot = tot + numpy.var(X[IND])
                    countt = countt + 1

            if (countt<1):
                y[n] = numpy.nan

            else:
                y[n] = tot / (countt * numpy.var(X))
        if mean_output:
            return y[~numpy.isnan(y)].mean()
        else:
            return y[~numpy.isnan(y)]
    else:
        raise NotImplementedError("Your version of numpy is missing *sliding_window_view*, numpy >= 1.20")
