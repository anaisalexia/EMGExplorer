#######################
# PROCESSING FUNCTION #
#######################
import sys
sys.path.append('EMG_Explorer_App\Explorer_package\global_processing')
from requirement_processing_perso_global import *







# TIME DOMAIN-------------------------------------------------------

@DecoratorGlobal
def mean_removal(emg,*arg,**kargs):
    print('MEAN REMOVAL')
    emg_output = emg - np.nanmean(emg)
    return emg_output

@DecoratorGlobal
def full_wave(emg,*arg,**kargs):
    return abs(emg)

@DecoratorGlobal
def linear_detrend(emg,*arg,**kargs):
    return signal.detrend(emg)

@DecoratorGlobal
def normalization_peak(emg):
    peak = np.max(emg)
    return emg / peak * 100


@DecoratorGlobal
def hilbert_rectification(emg):
    return np.abs(hilbert(emg-np.mean(emg)))




# FILTER-----------------------------------------------------------------------------------------
@DecoratorGlobal
def butterfilter_dual(emg, order=2,c_f =10,type = 'lowpass', s_f = SAMPLING_RATE,*arg,**kargs):
    
    assert not empty_value_check(emg),'Empty values emg filter'
    assert type in ['lowpass', 'highpass'], 'type of filter not valid'
    [b,a] = signal.butter(order,c_f,btype=type,analog=False, output='ba',fs=s_f)
    emg_filtered = signal.filtfilt(b,a,emg)
    print('MEAN REMOVAL')


    return emg_filtered
  
  

@DecoratorGlobal
def butterfilter_bandpass_dual(emg, order=2,c_f_low=5,c_f_high=300, s_f = SAMPLING_RATE,*arg,**kargs):

    assert not empty_value_check(emg),'Empty values emg filter bandpass'
    [b,a] = signal.butter(order,[c_f_low,c_f_high],btype='bandpass',analog=False, output='ba',fs=s_f)
    emg_filtered = signal.filtfilt(b,a,emg)

    return emg_filtered




@DecoratorGlobal
def notch_filter(emg, f0 = 50 , fl = 49 , fh = 51):

    q = 50
    if  not f0:
        assert fl, 'missing value'
        assert fh, 'missing value'
        q = np.sqrt(fl*fh)/(fh-fl)
        f0 = fl + (fh-fl)/2
    else:
        q = 50.0 

    b, a = signal.iirnotch(f0, q, SAMPLING_RATE)
    output_emg = signal.filtfilt(b, a, emg)

    return output_emg




