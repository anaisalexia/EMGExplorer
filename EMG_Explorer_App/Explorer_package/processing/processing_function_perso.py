#######################
# PROCESSING FUNCTION #
#######################
import sys
sys.path.append('EMG_Explorer_App\Explorer_package\processing')

from requirement_processing_function_perso import *





# TIME DOMAIN-------------------------------------------------------


def mean_removal(emg):
    emg_output = emg - np.nanmean(emg)
    return emg_output


def full_wave(emg):
    return abs(emg)


def linear_detrend(emg):
    return signal.detrend(emg)


def normalization_peak(emg):
    peak = np.max(emg)
    return emg / peak * 100


def rolling_function(emg,win = 50,func=np.mean,unit='sec'):
    if unit == 'sec': win_frame = int(win*SAMPLING_RATE)
    else: win_frame = int(win)
    res = [np.NAN for i in range(win_frame//2)]

    for i in range(win_frame//2,len(emg) - win_frame//2):
        val = func(emg[i - win_frame//2:i + win_frame//2])
        res.append(val)

    res += [np.NAN for i in range(win_frame//2)]
    assert len(emg) == len(res),'emg and "rolled emg" not same length'
    return res


# def sample_entropy(emg,m = 2, r=0.15):
#     # implementation according to Liu et al., 2022 https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9027109/

#     n = len(emg)
#     N = n-m-1
#     X = np.array([emg[i:i+m-1 +1] for i in range(N)]) # +1 because the last index is excluded
#     Y = np.array( [emg[i:i+m +1] for i in range(N -1)]) # m += 1

#     Ai = [np.sum(np.amax(np.abs(xi - X), axis = 1) <= r) for xi in X]
#     A = np.sum(Ai) * 0.5

#     Bi = [np.sum(np.amax(np.abs(yi - Y), axis = 1) <= r) for yi in Y]
#     B = np.sum(Bi) * 0.5


#     return -np.log(B/A)



def hilbert_rectification(emg):
    return np.abs(hilbert(emg-np.mean(emg)))




# FILTER-----------------------------------------------------------------------------------------

def butterfilter(emg, order=2,c_f=10 ,type = 'lowpass', s_f = SAMPLING_RATE):
    sos = signal.butter(order,c_f,btype=type,analog=False, output='sos',fs=s_f)
    emg_filtered = signal.sosfilt(sos,emg)
    return emg_filtered
  


# def fir_filter(emg,c_f=10,nb_taps=5, type='lowpass', s_f = SAMPLING_RATE):
#     assert type in ['lowpass', 'highpass'], 'type of filter not valid'
#     filtered_emg = np.ones_like(emg)
#     b = signal.firwin(nb_taps, c_f, pass_zero=type, fs=s_f)
#     filtered_emg[:-nb_taps//2] = signal.lfilter(b,1, emg)[nb_taps//2:]
#     filtered_emg[-nb_taps//2+1 :] = np.mean(filtered_emg)
    
#     return filtered_emg
  


def butterfilter_bandpass(emg, order=2,c_f_low=5,c_f_high=300, s_f = SAMPLING_RATE):

    assert not empty_value_check(emg),'Empty values emg filter bandpass'
    sos = signal.butter(order,[c_f_low,c_f_high],btype='bandpass',analog=False, output='sos',fs=s_f)
    emg_filtered = signal.sosfilt(sos,emg)

    return emg_filtered



def notch_filter(emg,  f0 = 50 , fl = 49 , fh = 51):
    q = 50
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





def hampel_filter(emg, win_= 1, n_sigmas=10,show=False):
    """_summary_

    Args:
        emg (_type_): _description_
        win_ (int, optional): sliding windows in sec. Defaults to 1.
        n_sigmas (int, optional):threshold, higher values = less exclusions. Defaults to 10.
        show (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    win = int(SAMPLING_RATE * win_)
    n = len(emg)
    emg_output = emg.copy()
    k = 1.4826 # scale factor for Gaussian distribution
 
    
    indices = []
    
    if show:
        S0_list = np.zeros_like(emg)

    for i in range((win),(n - win)):
        median_win = np.median(emg[(i - win):(i + win)])
        S0 = k * np.median(np.abs(emg[(i - win):(i + win)] - median_win))

        if (np.abs(emg[i] - median_win) > n_sigmas * S0):
            emg_output[i] = median_win
            indices.append(i)

        if show:
            S0_list[(i - win):(i + win)] =  n_sigmas * S0

    if show:
        return emg_output, indices,S0_list
    return emg_output








#THRESHOLD----------------------------------------------------------------------------------------

# def double_threshold(emg_,win = 2, time_win = 1,number_mean= 1, number_std = 1,baseline = [],show=False,sr=SAMPLING_RATE,th_amp_giv=0): 
#     """double threshold method to detect the activation of the muscle

#     Args:
#         emg_ (1D array/list): 
#         win (int, optional): size of the windows in seconde to compute the baseline.
#         time_win (int, optional): number of second the amplitude must be above/under the threshold so that an onset/offset is detected Defaults to 1.
#         number_mean (int, optional):  threshold_amp = number_mean * baseline_mean + number_std * baseline_std . Defaults to 1.
#         number_std (int, optional): threshold_amp = number_mean * baseline_mean + number_std * baseline_std . Defaults to 1.
#         baseline (list, optional): the baseline if already extracted and processed. Defaults to [].

#     Returns:
#         output: dictionnary, keys = time of the event ( frame ), values = the corresponding event ( 1 for onset, 0 for offset )
#         state_contraction: array, same length as emg, for each frame, 0 when the muscle is not contracted 1 otherwise
#         threshold_amp: amplitude of the threshold
#         number_onset_offset: array, same length as emg, the number of the repetition of the contraction for each frame 
#     """

#     assert not empty_value_check(emg_)
#     emg = emg_.copy() 

#     # Threshold computations
#     sample = int(sr * win)

#     if len(baseline) == 0 :
#         baseline = emg[:sample]
#     baseline_mean = np.mean(baseline)
#     baseline_std = np.std(baseline)

#     if th_amp_giv ==0:
#         threshold_amp = number_mean * baseline_mean + number_std * baseline_std
#     else:
#         threshold_amp = th_amp_giv

#     threshold_time = int(round(sr * time_win))

#     if show:
#         print(  threshold_amp,  threshold_time)

#     # Initialization of the variables
#     event = [0]
#     time = [0]   

#     onset_detected = False              # True when the muscle is truly, according to the double threshold method, contracted, False otherwise
#     onset,offset = False, False         # True when the threshold amplitude is exceeded (resp not exceeded), False otherwise (resp True). 
#     onset_time,offset_time = 0,0        
#     duration_on,duration_off = 0,0      # Count the number of frame where there the amplitude threshold is exceeded (resp not exceeded) 

#     for e,t in zip(emg,np.arange(0,len(emg))):

#         if e >= threshold_amp:
            
#             if not onset: #muscle was not contracted, an onset could be detected
#                 duration_on = 1
#                 onset_time = t
#                 onset = True
#                 offset = False
                
#             else: #muscle was already contracted
                
#                 duration_on += 1
                            
#                 if duration_on > threshold_time and onset_detected == False: # if the muscle has been contracted longer than the time threshold and if the onset wasn't already detected
#                     time.append(onset_time)
#                     event.append(1)
#                     onset_detected = True
#                     offset = False #an offset is not possible


#         else: 
#             if not offset: # an offset could be detected
#                 duration_off = 1
#                 offset = True
#                 onset = False
#                 offset_time = t
#             else:
#                 duration_off += 1
            

#                 if duration_off >= threshold_time and onset_detected:
#                     time.append(offset_time)
#                     event.append(0)
#                     onset_detected = False
#                     onset = False
                  

#     number = 1
#     state_contraction = np.zeros_like(emg)
#     number_onset_offset = np.zeros_like(emg)

#     #computation of state_contraction
#     for t in range(len(time)-1):

#         if event[t] == 1:
#             state_contraction[time[t-1]:time[t]] = 0
#             state_contraction[time[t]:time[t+1]] = 1
#             number_onset_offset[time[t-1]:time[t+1]] = number
#             number += 1
    
#     if event[-1] == 1:
#         state_contraction[time[-2]:time[-1]] = 0
#         state_contraction[time[-1]:] = 1
#         number_onset_offset[time[-2]:] = number
#     else:
#         state_contraction[time[-1]:] = 0
#         number_onset_offset[time[-1]:] = number 

#     output = dict(zip(time,event))

#     return output, state_contraction, threshold_amp, number_onset_offset














# FREQUENCY DOMAIN-------------------------------------------------------




# def median_frequency(emg,type = 'welch'): # checked unit test
    
#     assert not empty_value_check(emg), 'Empty value emg median frequency'
#     if type == 'welch':
#         freq,amp= signal.welch(emg,fs=SAMPLING_RATE)

#     elif type == 'periodogram':
#         freq,amp = signal.periodogram(emg,fs=SAMPLING_RATE)

#     # return np.median(freq)
#     amp_cumsum = np.cumsum(amp)
#     median = freq[np.where(amp_cumsum>np.max(amp_cumsum)/2)[0][0]]
#     return median


# def mean_power_frequency(emg,type = 'welch'):# checked unit test

#     assert not empty_value_check(emg), 'mean_power_frequency: empty value emg'
#     if type == 'welch':
#         freq,amp = signal.welch(emg,fs=SAMPLING_RATE)
#     elif type == 'periodogram':
#         freq,amp = signal.periodogram(emg,fs=SAMPLING_RATE)

#     output = np.sum(freq*amp)/np.sum(amp)
#     # return freq,amp,output
#     return output




# def sliding_mean_power_frequency(emg, win = 1):# checked unit test
#     # used for Du
   
#     if type(emg) != pd.core.series.Series:
#         emg = pd.Series(emg)

#     emg_rolling = emg.rolling(win*SAMPLING_RATE, min_periods = 1,center = True,closed = 'both',step = (win*SAMPLING_RATE)//2).apply(mean_power_frequency)
#     output = emg_rolling.mean()
#     return output










