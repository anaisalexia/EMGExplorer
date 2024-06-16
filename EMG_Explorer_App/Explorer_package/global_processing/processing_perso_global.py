#######################
# PROCESSING FUNCTION #
#######################
import sys
sys.path.append('EMG_Explorer_App\Explorer_package\global_processing')
from requirement_processing_perso_global import *



def DecoratorGlobal(function):
    # @functools.wraps(function)
    @functools.wraps(function)
    def wrapper(**arg):
        loader = arg['loader']
        path = arg['path']
        del arg['path']
        del arg['loader']
        print("Decorator Global in")
        for k,v in arg.items():
            if v == None:
                del arg[k]
        for gr in path.keys():
            for var in path[gr].keys():
                for dim in path[gr][f'{var}'].keys():
                    for ch in path[gr][f'{var}'][dim]:
                        x = np.array(loader.getData(gr,var,dim,ch))
                        arg['x'] = x
                        y = function(x,**arg)

                        loader.setData(gr,f'{var}',dim,ch,y)
                        print('Dataset')

    # wrapper.__signature__ = inspect.signature(function)   
    # wrapper.__name__ = function.__name__   

    return wrapper



def empty_value_check(emg):
    if type(emg) != pd.core.series.Series:
        emg = pd.Series(emg)
    out = emg.isnull().values.any() #is null detects missing values for an array-like object, values takes the values of the pandas series and any detects if there is any True
    return out





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
def fir_filter(emg,c_f=10,nb_taps=5, type='lowpass', s_f = SAMPLING_RATE,*arg,**kargs):
    assert not empty_value_check(emg),'Empty values emg filter'
    assert type in ['lowpass', 'highpass'], 'type of filter not valid'
    filtered_emg = np.ones_like(emg)
    b = signal.firwin(nb_taps, c_f, pass_zero=type, fs=s_f)
    filtered_emg[:-nb_taps//2] = signal.lfilter(b,1, emg)[nb_taps//2:]
    filtered_emg[-nb_taps//2:] = np.mean(filtered_emg)
    
    return filtered_emg
  

@DecoratorGlobal
def butterfilter_bandpass_dual(emg, order=2,c_f_low=10,c_f_high=5, s_f = SAMPLING_RATE,*arg,**kargs):

    assert not empty_value_check(emg),'Empty values emg filter bandpass'
    [b,a] = signal.butter(order,[c_f_low,c_f_high],btype='bandpass',analog=False, output='ba',fs=s_f)
    emg_filtered = signal.filtfilt(b,a,emg)

    return emg_filtered




@DecoratorGlobal
def notch_filter(emg, f0 = None , fl = None , fh = None):

    if  not f0:
        assert fl, 'missing value'
        assert fh, 'missing value'
        q = np.sqrt(fl*fh)/(fh-fl)
        f0 = fl + (fh-fl)/2
    else:
        q = 50.0 # how to choose the value ?

    b, a = signal.iirnotch(f0, q, SAMPLING_RATE)
    output_emg = signal.filtfilt(b, a, emg)

    return output_emg




@DecoratorGlobal
def comb_filter(emg,f0,ft,fs=SAMPLING_RATE,q=100.0):

    output_emg = emg.copy()
    for i in range(1,ft//f0 +1):
        b, a = signal.iirnotch(f0*i, q, fs=fs)
        output_emg = signal.filtfilt(b, a, output_emg)

    return output_emg

