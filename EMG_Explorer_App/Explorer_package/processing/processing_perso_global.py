#######################
# PROCESSING FUNCTION #
#######################
import sys
sys.path.append('EMG_Explorer_App\Explorer_package\processing')
import functools

# from functions.requirements import *
# from functions.c3d_function import extract_channels_c3d, read_c3d
# from functions.plot_function import *




def Try_decorator(function):
    print('in deco')
    def wrapper(*arg):
        try:
            function(*arg)
        except Exception as e:
            print(function.__name__)
            print(e)

    return wrapper


def DecoratorGlobal(function):
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
                        x = function(x,**arg)

                        loader.setData(gr,f'{var}',dim,ch,x)
                        print('Dataset')
        
    return wrapper



from requirement_processing_function_perso import *

def empty_value_check(emg):
    if type(emg) != pd.core.series.Series:
        emg = pd.Series(emg)
    out = emg.isnull().values.any() #is null detects missing values for an array-like object, values takes the values of the pandas series and any detects if there is any True
    return out



def emply_value_evaluate(emg,show = False, print = False):
    """gives a first idea of the distribution of empty values

    Args:
        emg: vector
        show (bool, optional): if True: shows the distribution of empty values over time

    Returns:
        index: the index of the empty values
        number_empty: the number of empty values
    """
    if type(emg) != pd.core.series.Series:
        emg = pd.Series(emg)
        
    emg_empty = emg.isnull()
    index = emg_empty.loc[emg_empty == True].index
    number_empty = len(emg_empty.loc[emg_empty == True])
    if print:
        print(f" number of empty values : {number_empty}," , " %.4f percent of the signals" %((number_empty/len(emg))*100)) 
    
    if show:
        fig,ax = plt.subplots(figsize = FIG_SIZE)
        ax.plot(np.arange(0,len(emg_empty)), [1 if e else 0 for e in emg_empty])
        ax.set(xlabel = 'sample', ylabel = '1 = empty', title = 'Empty values')
        fig.tight_layout()
        plt.show()

    return np.array(index), number_empty
    



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


def normalization(emg,norm):
    assert norm != 0
    return emg / norm * 100



def time_nomalization(emg):

    n = len(emg)  
    x = np.arange(n)
    x_new = np.linspace(0,n,500)
    cs = interpolate.CubicSpline(x,emg)
    return cs(x_new)


def kinematic_interpolate(kin,emg):
    assert not empty_value_check(kin), 'time_normalization: empty values'
    n = len(kin)  
    n_emg = len(emg)
    x = np.linspace(0,n_emg,n)
    x_new = np.arange(0,n_emg)
    cs = interpolate.interp1d(x,kin,kind='linear')
    return cs(x_new)


def normalization_peak(emg):
    peak = np.max(emg)
    return emg / peak * 100



def rms(emg):
    return np.sqrt(np.mean(emg**2))



def mean_signal(emg):
    assert not empty_value_check(emg), 'Empty values emg mean'
    return np.mean(emg)



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


def sample_entropy(emg,m = 2, r=0.15):
    # implementation according to Liu et al., 2022 https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9027109/

    n = len(emg)
    N = n-m-1
    X = np.array([emg[i:i+m-1 +1] for i in range(N)]) # +1 because the last index is excluded
    Y = np.array( [emg[i:i+m +1] for i in range(N -1)]) # m += 1

    Ai = [np.sum(np.amax(np.abs(xi - X), axis = 1) <= r) for xi in X]
    A = np.sum(Ai) * 0.5

    Bi = [np.sum(np.amax(np.abs(yi - Y), axis = 1) <= r) for yi in Y]
    B = np.sum(Bi) * 0.5


    return -np.log(B/A)




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
def butterfilter(emg, order=2,c_f=10 ,type = 'lowpass', s_f = SAMPLING_RATE,*arg,**kargs):
    sos = signal.butter(order,c_f,btype=type,analog=False, output='sos',fs=s_f)
    emg_filtered = signal.sosfilt(sos,emg)
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



def butterfilter_bandpass(emg, order=2,c_f_low=60,c_f_high=5, s_f = SAMPLING_RATE):

    assert not empty_value_check(emg),'Empty values emg filter bandpass'
    sos = signal.butter(order,[c_f_low,c_f_high],btype='bandpass',analog=False, output='sos',fs=s_f)
    emg_filtered = signal.sosfilt(sos,emg)

    return emg_filtered



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





def comb_filter(emg,f0,ft,fs=SAMPLING_RATE,q=100.0):

    output_emg = emg.copy()
    for i in range(1,ft//f0 +1):
        b, a = signal.iirnotch(f0*i, q, fs=fs)
        output_emg = signal.filtfilt(b, a, output_emg)

    return output_emg





def tkeo(emg):

    assert not empty_value_check(emg), 'Empty data'
    if type(emg) == pd.core.series.Series:
        emg = np.array(emg)

    output = [emg[0]**2]
    for i in range(1,len(emg)-1):
        output.append(emg[i]**2 - emg[i+1]*emg[i-1])

    output += [emg[-1]**2]
    output = np.array(output)

    assert len(emg) == len(output)

    return output



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
    return emg_output, indices



def hampel_adaptative_bw(emg,cf=35):
    filtered_emg,_ = hampel_filter(mean_removal(emg),n_sigmas=10)
    filtered_emg = adaptive_butterfilter(emg,cf=cf,win_base=0.3,win_time=0.02,nb_mean=1, nb_std=0,show_spectro=False,show_th=False)
    return filtered_emg

def fas_filter(emg_, k=5, L=0.5,nq_min = 5,show = False ):

    def mtp_filter(emg,ecg):
        
        # take the index where the value are not np.Nan, ie values that do not belong to the ecg array
        index = list(emg[~np.isnan(emg)].index)
        emg_nan_list = []

        for id_index in range(0,len(index[:-2]),2): # iterate for the number of index with values that are not nan -2
            # selection of the index of the value
            i,i1,i2 = index[id_index],index[id_index+1],index[id_index+2]
            # selection of the corresponding emg value
            v,v1,v2 = emg[i],emg[i1],emg[i2]
            slope1 = v1 - v
            slope2 = v2 - v1
            if slope1 * slope2 < 0:
                # v2 is retain in ECG array
                ecg[i2] = v2
                emg_nan_list.append(i2) # index stored so that the value can be removed from emg signal afterwards

            elif slope1 * slope2 >= 0:
                # v1 is retain in ECG array
                ecg[i1] = v1
                emg_nan_list.append(i1) # index stored so that the value can be removed from emg signal afterwards

        emg[emg_nan_list] = np.NAN # the values that were retained in the ECF array are removed from the EMG array ie transform into Nan to keep the indexing
        return emg,ecg



    def qrs_detection(emg, ecg, L, nq_min):

        index = list(emg[~np.isnan(emg)].index) # index of the value of the emg that are not part of the ecg array, ie not nan
        length = len(index) 
        qrs_detected = False
        id_qrs = [] # will store the index of values that are part of a QRS complex
        id_index = 0 

        while id_index < length:
            i = index[id_index] # index of the values of emg that are not empty

            if emg[i] > L:

                while id_index < length and emg[i] > L: 
                    i = index[id_index]
                    id_qrs.append(i)
                    id_index += 1

                # The emg values are no longer above the threshold: either the EMG was above the signal long enough to be considered as part of ECG or if wasn't long enough
                if len(id_qrs) >= nq_min:
                    qrs_detected = True

                    # the QRS complex normally lasts 80 to 100 ms, Q wave: Duration up to 40 ms   
                    emg_before = emg.iloc[ np.max([0,id_qrs[0] - 40]): id_qrs[0]] # samples before R peak
                    emg_after = emg.iloc[id_qrs[-1] : np.min([len(emg),id_qrs[-1] + 40])] # samples after R peak
           
                    emg_before_values = emg_before.fillna(method='ffill').values
                    emg_after_values = emg_after.fillna(method='ffill').values
                    min_q = np.argrelmin(emg_before_values) # agrelmin returns a tupple of numpy array containing the index of the local minima, hence the double indexing (*)
                    
                    # Detection of Q wave
                    if len(min_q[0]) != 0:
                        min_q = min_q[0][-1] # takes the index of the closest local minima from the R peak (*)
                        id_qrs += index[id_qrs[0] - min_q : id_qrs[0]]

                    # Detection of S wave
                    min_s = np.argrelmin(emg_after_values)
                    if len(min_s[0]) != 0 :
                        min_s = min_s[0][0] # takes the index of the closest local minima from the R peak (*)
                        id_qrs += index[id_qrs[-1]+1 :id_qrs[-1]+ min_s +1]

                    ecg[id_qrs] = emg.iloc[id_qrs]
                    emg[id_qrs] = np.NAN

                
                id_qrs = []

            else:
                id_index += 1

        return emg,ecg,qrs_detected

    # just for plotting the signal in between steps
    def plot_signal(emg,ecg,title):
        fig,ax = plt.subplots(1,2,figsize = (9,2))
        ax[0].plot(list(emg[~np.isnan(emg)].index),emg[~np.isnan(emg)].values,alpha=0.8,label='emg wo nan')
        ax[0].plot(emg,color='orange',alpha=0.8,label='emg w nan')
        ax[0].legend()
        ecg_df = pd.DataFrame(ecg)
        ecg_val = ecg_df[~np.isnan(ecg_df)]
        ax[1].plot(list(ecg_val.index),ecg_val.values,label='emg wo nan',alpha=0.8)
        ax[1].plot(ecg,label='emg w nan',alpha=0.8)

        ax[0].set(title = title)
        fig.tight_layout()

    #reconstruction of the ecg signal with linear interpolation
    def reconstruct_ecg(ecg:pd.Series):
        length = len(ecg)
        x_new = np.arange(length)
        x_ecg = list(ecg[~np.isnan(ecg)].index) # retrieves the index of the values that were considered as part of the ECG array
        ecg_interp = np.interp(x_new, x_ecg, ecg[~np.isnan(ecg)].values)
        # ecg_smooth = signal.savgol_filter(ecg_interp, 51, 3)  # Smoothing with Savitzky-Golay filter
        return ecg_interp


    ecg = np.empty_like(emg_) 
    ecg[:] = np.NAN
    emg = pd.Series(emg_.copy()) # emg signal is copied in case of issues between copies and views on pandas
    ecg = pd.Series(ecg)

    if show: plot_signal(emg,ecg, 'original')
    emg,ecg = mtp_filter(emg,ecg)
    if show: plot_signal(emg,ecg,'after mtp')
    
    for _ in range(k-1):
        if show: print(len(emg[~np.isnan(emg)]),len(ecg[~np.isnan(ecg)])) # just for verification

        emg,ecg,qrs_detected = qrs_detection(emg, ecg, L, nq_min)

        if show: plot_signal(emg,ecg,f'after qrs detection {qrs_detected}') # just for verification

        if not qrs_detected:
            emg,ecg= mtp_filter(emg,ecg)
            if show: plot_signal(emg,ecg,'after mtp')
    
    ecg_inter = reconstruct_ecg(ecg)
    emg_rec = emg_ - ecg_inter

    # final plot
    if show:
        fig,ax = plt.subplots(1,2,figsize = (9,2))
        ax[0].plot(emg_rec)
        ax[1].plot(ecg_inter)
        ax[1].set(title = 'ecg')
        ax[0].set(title = 'emg')


    return emg_rec




# function [b,idx,outliers] = deleteoutliers(a,alpha,rep)
# % [B, IDX, OUTLIERS] = DELETEOUTLIERS(A, ALPHA, REP)
# %
# % For input vector A, returns a vector B with outliers (at the significance
# % level alpha) removed. Also, optional output argument idx returns the
# % indices in A of outlier values. Optional output argument outliers returns
# % the outlying values in A.
# %
# % ALPHA is the significance level for determination of outliers. If not
# % provided, alpha defaults to 0.05.
# %
# % REP is an optional argument that forces the replacement of removed
# % elements with NaNs to presereve the length of a. (Thanks for the
# % suggestion, Urs.)
# %
# % This is an iterative implementation of the Grubbs Test that tests one
# % value at a time. In any given iteration, the tested value is either the
# % highest value, or the lowest, and is the value that is furthest
# % from the sample mean. Infinite elements are discarded if rep is 0, or
# % replaced with NaNs if rep is 1 (thanks again, Urs).
# %
# % Appropriate application of the test requires that data can be reasonably
# % approximated by a normal distribution. For reference, see:
# % 1) "Procedures for Detecting Outlying Observations in Samples," by F.E.
# %    Grubbs; Technometrics, 11-1:1--21; Feb., 1969, and
# % 2) _Outliers in Statistical Data_, by V. Barnett and
# %    T. Lewis; Wiley Series in Probability and Mathematical Statistics;
# %    John Wiley & Sons; Chichester, 1994.
# % A good online discussion of the test is also given in NIST's Engineering
# % Statistics Handbook:
# % http://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm
# %
# % ex:
# % [B,idx,outliers] = deleteoutliers([1.1 1.3 0.9 1.2 -6.4 1.2 0.94 4.2 1.3 1.0 6.8 1.3 1.2], 0.05)
# %    returns:
# %    B = 1.1000    1.3000    0.9000    1.2000    1.2000    0.9400    1.3000    1.0000    1.3000    1.2000
# %    idx =  5     8    11
# %    outliers = -6.4000    4.2000    6.8000
# %
# % ex:
# % B = deleteoutliers([1.1 1.3 0.9 1.2 -6.4 1.2 0.94 4.2 1.3 1.0 6.8 1.3 1.2
# % Inf 1.2 -Inf 1.1], 0.05, 1)
# % returns:
# % B = 1.1000  1.3000  0.9000  1.2000  NaN  1.2000  0.9400  NaN  1.3000  1.0000  NaN  1.3000  1.2000  NaN  1.2000  NaN  1.1000
# % Written by Brett Shoelson, Ph.D.
# % shoelson@helix.nih.gov
# % 9/10/03
# % Modified 9/23/03 to address suggestions by Urs Schwartz.
# % Modified 10/08/03 to avoid errors caused by duplicate "maxvals."
# %    (Thanks to Valeri Makarov for modification suggestion.)

def deleteoutliers(a,alpha=0.05,rep=0,fact=1): # [b,idx,outliers] 

    def zcritical(alpha,n):
        # https://www.researchgate.net/post/Is_there_an_equivalent_function_for_finv_Matlab_function_in_python
        # https://stackoverflow.com/questions/19339305/python-function-to-get-the-t-statistic
        # https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h1.htm
        tcrit = stats.t.ppf(1-alpha/(2*n),n-2)
        zcrit = (n-1)/np.sqrt(n)*(np.sqrt(tcrit**2/(n-2+tcrit**2)))
        return zcrit


    idx_list = [False] * len(a)

    assert rep in [0,1], 'Please enter a 1 or a 0 for optional argument rep.' # 0 = False

    b = a.copy()
    outlier = 1

    while outlier:
        tmp = b[~np.isnan(b)]
   
        meanval = np.mean(tmp)
        ##maxval = tmp[ abs(tmp-meanval) == np.max(abs(tmp-meanval))] #values of tmp that are equals to the max why so complicate
        maxval = tmp[np.argmax(abs(tmp-meanval))] # demeaned
        sdval = np.std(tmp)
        tn = abs((maxval-meanval)/sdval)  # max val = tn * std
        critval = zcritical(alpha,len(tmp))
        outlier = tn > critval*fact # exclusion of max val if max val > zcritical * std

        if outlier:
            tmp = a==maxval
            b[tmp] = np.NAN 

    idx = np.isnan(b)
    outlier = a[idx]
    idx_list = idx_list | idx

    if ~rep: # if rep = 0 -> 1 then True then outliers(np.NAN) are removed
        b = b[~np.isnan(b)]

    emg_2 = a.copy()
    emg_2[idx] = np.mean(a)

    return idx,outlier, b,emg_2



# function zcrit = zcritical(alpha,n)
# %ZCRIT = ZCRITICAL(ALPHA,N)
# % Computes the critical z value for rejecting outliers (GRUBBS TEST)
# tcrit = tinv(alpha/(2*n),n-2);
# zcrit = (n-1)/sqrt(n)*(sqrt(tcrit^2/(n-2+tcrit^2)));







#THRESHOLD----------------------------------------------------------------------------------------

def double_threshold(emg_,win = 2, time_win = 1,number_mean= 1, number_std = 1,baseline = [],show=False,sr=SAMPLING_RATE,th_amp_giv=0): 
    """double threshold method to detect the activation of the muscle

    Args:
        emg_ (1D array/list): 
        win (int, optional): size of the windows in seconde to compute the baseline.
        time_win (int, optional): number of second the amplitude must be above/under the threshold so that an onset/offset is detected Defaults to 1.
        number_mean (int, optional):  threshold_amp = number_mean * baseline_mean + number_std * baseline_std . Defaults to 1.
        number_std (int, optional): threshold_amp = number_mean * baseline_mean + number_std * baseline_std . Defaults to 1.
        baseline (list, optional): the baseline if already extracted and processed. Defaults to [].

    Returns:
        output: dictionnary, keys = time of the event ( frame ), values = the corresponding event ( 1 for onset, 0 for offset )
        state_contraction: array, same length as emg, for each frame, 0 when the muscle is not contracted 1 otherwise
        threshold_amp: amplitude of the threshold
        number_onset_offset: array, same length as emg, the number of the repetition of the contraction for each frame 
    """

    assert not empty_value_check(emg_)
    emg = emg_.copy() 

    # Threshold computations
    sample = int(sr * win)

    if len(baseline) == 0 :
        baseline = emg[:sample]
    baseline_mean = np.mean(baseline)
    baseline_std = np.std(baseline)

    if th_amp_giv ==0:
        threshold_amp = number_mean * baseline_mean + number_std * baseline_std
    else:
        threshold_amp = th_amp_giv

    threshold_time = int(round(sr * time_win))

    if show:
        print(  threshold_amp,  threshold_time)

    # Initialization of the variables
    event = [0]
    time = [0]   

    onset_detected = False              # True when the muscle is truly, according to the double threshold method, contracted, False otherwise
    onset,offset = False, False         # True when the threshold amplitude is exceeded (resp not exceeded), False otherwise (resp True). 
    onset_time,offset_time = 0,0        
    duration_on,duration_off = 0,0      # Count the number of frame where there the amplitude threshold is exceeded (resp not exceeded) 

    for e,t in zip(emg,np.arange(0,len(emg))):

        if e >= threshold_amp:
            
            if not onset: #muscle was not contracted, an onset could be detected
                duration_on = 1
                onset_time = t
                onset = True
                offset = False
                
            else: #muscle was already contracted
                
                duration_on += 1
                            
                if duration_on > threshold_time and onset_detected == False: # if the muscle has been contracted longer than the time threshold and if the onset wasn't already detected
                    time.append(onset_time)
                    event.append(1)
                    onset_detected = True
                    offset = False #an offset is not possible


        else: 
            if not offset: # an offset could be detected
                duration_off = 1
                offset = True
                onset = False
                offset_time = t
            else:
                duration_off += 1
            

                if duration_off >= threshold_time and onset_detected:
                    time.append(offset_time)
                    event.append(0)
                    onset_detected = False
                    onset = False
                  

    number = 1
    state_contraction = np.zeros_like(emg)
    number_onset_offset = np.zeros_like(emg)

    #computation of state_contraction
    for t in range(len(time)-1):

        if event[t] == 1:
            state_contraction[time[t-1]:time[t]] = 0
            state_contraction[time[t]:time[t+1]] = 1
            number_onset_offset[time[t-1]:time[t+1]] = number
            number += 1
    
    if event[-1] == 1:
        state_contraction[time[-2]:time[-1]] = 0
        state_contraction[time[-1]:] = 1
        number_onset_offset[time[-2]:] = number
    else:
        state_contraction[time[-1]:] = 0
        number_onset_offset[time[-1]:] = number 

    output = dict(zip(time,event))

    return output, state_contraction, threshold_amp, number_onset_offset
























# EVENTS------------------------------------------------------------------------------

def extract_event(emg,event_,event_type ,endu=None,task_name=None,figs=FIG_SIZE,xl='time (s)',yl = 'Amplitude (V)',plot_title = 'EMG signal and its events',show=False): # Checked visually + unit test
    """number each frame according to the corresponding event, ie corresponding subphase of the task 
    (First system to be implemented to facilitate segmentation and be able to visualize easily the results)

    Args:
        emg (_type_): _description_
        event (DataFrame): _description_
        xl (str, optional): _description_. Defaults to 'time (s)'.
        yl (str, optional): _description_. Defaults to 'Amplitude (V)'.
        plot_title (str, optional): _description_. Defaults to 'EMG signal and its events'.
        event_type (str, optional): Gait, MVC, Endu, ''
        show (bool, optional): _description_. Defaults to False.

    Returns:
        event_line: ndarray
    """

    if event_type in ['Gait','']: 
        event = event_.copy(deep = True)
        event['time']= event.apply(lambda x: x.time_sec + 60* x.time_min, axis=1)
        event = event.sort_values(by = ['time']).reset_index(drop=True) 

    elif task_name == 'Endurance_Sorensen':
        event = event_.copy(deep = True)
        event = event.sort_values(by = ['time']).reset_index(drop=True) 

    event_line = -1* np.ones_like(emg) 

    start_mvc = 0
    stop_mvc = 0
    start_endu = 0
    stop_endu = 0
    
        
    # For Endurance Sorensens or Endurance Ito
    if event_type == 'Endu': # the signal is used from start to finish
        if task_name == 'Endurance_Sorensen':
            start_endu = event.loc[event['event'] == 'startEndurance']['time'].values[0] # in secondes
            stop_endu = event.loc[event['event'] == 'stopEndurance']['time'].values[0]
            event_line[int(start_endu*SAMPLING_RATE):int(stop_endu*SAMPLING_RATE)] = 1

        else: 
            event_line[int(3*SAMPLING_RATE):int(len(emg)*0.85)] = 1
            
        
    elif event_type == 'MVC': # only 3 secondes of the signal are used
        if task_name == 'Endurance_Sorensen':
            start_endu = event.loc[event['event'] == 'startEndurance']['time'].values[0] # in secondes
            event_line[int(start_endu*SAMPLING_RATE):int((start_endu+3)*SAMPLING_RATE)] = 1
        else: 
            event_line[int(5*SAMPLING_RATE):int(8*SAMPLING_RATE)] = 1
            


    # Other Tasks different from Gait
    elif event_type != 'Gait':
        current_event = 'stopMotion'
 
        for i in range(len(event['time'])-1): # the frames will have no labels from the first frame to the first event and from the last event to the last frame
            current_time = event['time'][i]
            future_time = event['time'][i+1]
            current_event = event['event'][i]
            event_line[int(current_time * SAMPLING_RATE): int(future_time*SAMPLING_RATE)] = 0 if current_event == 'stopMotion' else 1

    # Gait
    else:
        
        for i in range(1,len(event['time'])): # the frames will have no labels from the first frame to the first event and from the last event to the last frame
            following_time = event['time'][i]
            actual_time = event['time'][i-1]
            current_event = event['event'][i-1]
            event_line[int(actual_time * SAMPLING_RATE): int(following_time * SAMPLING_RATE)] = 0 if current_event == 'RHS' else 1 if current_event == 'RTO' else 2 if current_event == 'LHS' else 3

        # current_event = event['event'].iloc[-1]
        # event_line[int(event['time'].iloc[-1] * SAMPLING_RATE): ] = 0 if current_event == 'RHS' else 1 if current_event == 'RTO' else 2 if current_event == 'LHS' else 3



    if show:  
        fig,ax = plt.subplots(figsize= figs)

        #plotting the lines
        if event_type == 'Gait' or event_type == '' or task_name=='Endurance_Sorensen':

            for i in range(1,len(event['time'])):
                x,next_x,current_event = event['time'][i-1],event['time'][i], event['event'][i-1]
                p1 = plt.axvline(x=x,color='white')
                if event_type == 'Gait':
                    ax.axvspan(x, next_x, color='red' if current_event == 'RHS' else 'orange' if current_event == 'RTO' else 'yellow' if current_event == 'LHS' else 'green', alpha=0.3)
        
                elif event_type == '' or task_name=='Endurance_Sorensen':
                    
                    ax.axvspan(x, next_x, color= 'orange' if current_event == 'stopMotion' else 'yellow' , alpha=0.3)


        else:
            ax.axvspan(start_mvc, stop_mvc, color='cyan', alpha = 0.3,label =  'mvc' )
            ax.axvspan(start_endu, stop_endu, color='green', alpha = 0.3 ,label =  'endurance' )
            ax.legend()
            print(f'Start Endurance: {start_endu}, Start MVC: {start_mvc}, Stop MVC: {stop_mvc}, Stop Endurance: {stop_endu}')

        
        t = np.arange(0,len(emg))/SAMPLING_RATE
        ax.set(xlabel=xl, ylabel=yl, title = plot_title)
        ax.plot(t,emg)
   
        fig.tight_layout()

    return event_line











def time_emg_event_normalization(emg,event_,shift=0):  # Checked visually + unit test

    """Time normalizes each stride (500 data points and cubicspline interpolation) so that each emg values has a % of stride as index
    (Used for Lamoth, Van der Hulst and Arend Nielsen)
    (takes only the full and complete stride)

    Args:
        emg (ndarray): emg values
        event_ (Dataframe): columns: time sec, time min, event
        shift (int, optional): _description_. Defaults to 0.

    Returns:
        Dataframe: columns :emgs, frame, event, stride
            frame are the index of the value expressed as % of stride: they range from 0 to 100%
            event: RHS LHS LTO RTO or Nan
            stride: number of the stride
    """
    event = event_.copy(deep = True)

    # conversion from time in sec and min to frame
    event['frame'] = event.apply(lambda x: int(np.around((60 * x['time_min'] + x['time_sec'])*SAMPLING_RATE-shift, decimals=0)),axis=1)
    event = event.sort_values(by='frame').iloc[:-1,:] #the last event represent a subphase that is not complete

    # creation of a Dataframe with the emg values per frame and merged on 'frame' with the event DataFrame
    emg_df = pd.DataFrame({'frame':np.arange(len(emg)) +1, 'emg':emg})
    df = pd.merge(emg_df, event[['frame','event']], on='frame', how='left')

    # creation of an Itorator to give a number from one to n each time the first event of the Dataframe is encoutered (ie for each gait cycle)
    iter_ = iter(np.arange(event.shape[0]))
    next(iter_)
    df['stride'] = df['event'].apply(lambda x: next(iter_) if x == df['event'].loc[~df['event'].isnull()].iloc[0] else None)
    
    # df.head()
    # >>> index frame	emg	   event	stride
    # >>> 109	110	-0.037690	RHS	1.0
    # >>> 110	111	-0.037690	NaN	NaN

    # df['stride'].unique()
    # >>> array([nan,  1.,  2.,  3.])

    # filling of the empty values of the 'stride' column with the previous values so that each sample belonging to a stride has its corresponding number
    df['stride'] = df['stride'].fillna(method="ffill")
   
    # division of the Dataframe per stride
    df_stride_grouped = df.groupby('stride')

    # df_stride.get_group(3)['event'].value_counts()
    # >>> RHS    1
    # >>> LTO    1
    # >>> LHS    1
    # >>> RTO    1
    # Name: event, dtype: int64

    df_emg_event_norm = pd.DataFrame(data=None, columns=['emg','frame','event','stride'])

    ## For each stride
    for k in range(1,len(df_stride_grouped)+1):
        ## check if the stride is complete
        if len(df_stride_grouped.get_group(k)['event'].value_counts()) == 4 :

            ## time normalization emg
            # retrieves one stride
            df_stride = df_stride_grouped.get_group(k) 
            # resampling so that one stride = 500 samples, one stride = 100%
            emg_norm = time_nomalization(df_stride['emg'].values) 
            # replace frame by percent for index
            percent = np.linspace(0,100,len(emg_norm)) 
            df_emg_norm = pd.DataFrame({'emg': emg_norm, 'frame':percent })

            ## time normalized event
            # get the event of the stride
            df_stride_na = df_stride.dropna() 
            # conversion of the frame of the event from frame to percent (%  for 500 samples) and so that it begins with 0
            # df_stride['frame'].iloc[0] is the number of the frame where the stride start
            # x is positionned at the index (x - df_stride['frame'].iloc[0]) of the stride
            event_norm = df_stride_na['frame'].apply(lambda x:  percent[int((x - df_stride['frame'].iloc[0])*500/len(df_stride['emg']))])

            # event_norm = df_stride_na['frame'].apply(lambda x:  (x - df_stride['frame'].iloc[0]) * 500/len(df_stride['emg'] ))
            event_norm = list(event_norm.values)

            df_event_norm = pd.DataFrame( {'frame':event_norm, 'event':df_stride_na['event']}) 
            #    frame(%) event
            # 109      0   RHS
            # 239     57   LTO
            # 669    247   LHS
            # 799    305   RTO
            
            ## Merging of the time normalized event and emg
            df_emg_event_norm_k = pd.merge(df_emg_norm, df_event_norm , on='frame', how='left')
            df_emg_event_norm_k['stride'] = np.ones( df_emg_event_norm_k.shape[0])*k
            
            df_emg_event_norm = pd.concat([df_emg_event_norm, df_emg_event_norm_k],ignore_index=True)

    return df_emg_event_norm




def extract_event_stride(df_emg_event_norm ,xl='percent of stride (%)',yl = 'Amplitude (V)',plot_title = 'EMG signal and its events',show=False):
    """ LINK TO time_emg_event_normalization: label each frame of the time normalized signal according to the ongoing subphase and display the result
    (only used with Arend Nielsen to show the segmentation)

    Args:
        df (_type_): output from time_emg_event_normalization: 
        xl (str, optional): _description_. Defaults to 'percent of stride (%)'.
        yl (str, optional): _description_. Defaults to 'Amplitude (V)'.
        plot_title (str, optional): _description_. Defaults to 'EMG signal and its events'.
        endu (bool, optional): _description_. Defaults to False.
        show (bool, optional): _description_. Defaults to False.

    Returns:
        event_line: ndarray
    """

    event_line = -1* np.ones(len(df_emg_event_norm['emg'])) 
    df = df_emg_event_norm.dropna()

    for i in np.arange(1,len(df['event'])):
        current_time = df['frame'].iloc[i]
        past_time = df['frame'].iloc[i-1]
        current_event = df['event'].iloc[i-1]
        
        event_line[int(past_time): int(current_time)] = 0 if current_event == 'RHS' else 1 if current_event == 'RTO' else 2 if current_event == 'LHS' else 3
    current_event = df['event'].iloc[-1]
    event_line[int(df['frame'].iloc[-1] ): ] = 0 if current_event == 'RHS' else 1 if current_event == 'RTO' else 2 if current_event == 'LHS' else 3


    if show:  
        fig,ax = plt.subplots(figsize= FIG_SIZE)

        for i in range(1,len(df['event'])):
            x,next_x,current_event = df['frame'].iloc[i-1],df['frame'].iloc[i], df['event'].iloc[i-1]
            p1 = plt.axvline(x = x, color = 'white')
            ax.axvspan(x, next_x, color='red' if current_event == 'RHS' else 'orange' if current_event == 'RTO' else 'yellow' if current_event == 'LHS' else 'green', alpha=0.3)
        current_event = df['event'].iloc[-1]
        _ = plt.axvline(x = df['frame'].iloc[-1], color = 'white')
        ax.axvspan(df['frame'].iloc[-1], df_emg_event_norm['frame'].iloc[-1], color='red' if current_event == 'RHS' else 'orange' if current_event == 'RTO' else 'yellow' if current_event == 'LHS' else 'green', alpha=0.3)
        
        t =df_emg_event_norm['frame']
        ax.set(xlabel=xl, ylabel=yl, title = plot_title)
        ax.plot(t,df_emg_event_norm['emg'])
   
        fig.tight_layout()

    return event_line





def event_gait_segmentation(filtered_emg,event_line_emg): # Checked visually + unit test
    """ FROM THE OUTPUT OF EXTRACT EVENT : segments the signal in subphases (for complete gait cycle) and output each EMG segment with their number of repetition and subphase's name
    (Used only for Pakzad)

    Args:
        filtered_emg (_type_): _description_
        event_line_emg (_type_): " event time line" of the function extract_event
        show (bool, optional): _description_. Defaults to False.

    Returns:
        dataframe: (columns: emg, event, repetition ) each row comprises the emg segment of the corresponding subphase
    """
    
    assert not empty_value_check(filtered_emg), 'Empty values filtered EMG'

    event_key = []
    emg_subphase = []
    event_rep = []
    rep_cycle = { 'RHS':0, 'RTO':0, 'LHS':0,'LTO':0}
    last_index = 0

    dict_output = {'emg':[],'event':[],'rep':[]}

    # function to check if a gait cycle is complete
    def check_eq(rep_cycle):
        for val in rep_cycle.values():
            if val != list(rep_cycle.values())[0]:
                return False
        return True

    # For each subphase
    for k,g in groupby(event_line_emg):

        # if the first event is not define, initilize the name of the forst event of the cycle
        if k != -1: # -1 is the absence of event

            len_seg = len(list(g)) # length of the subphase
            rep_cycle[EVENT_GAIT[k]] += 1
            event_rep += [rep_cycle[EVENT_GAIT[k]]]
            event_key.append(EVENT_GAIT[k])
            # extract the emg corresponding to the subphase
            emg_subphase += [filtered_emg[last_index: last_index + len_seg]] 
            last_index += len_seg # pointer: end of current subphase

            # if the cycle is complete
            if check_eq(rep_cycle): 
                # add to the dict that will turn into the output dataframe the emg, event and number of the repetition 
                # corresponding to each subphases of the cycle
                dict_output['emg'] += emg_subphase
                dict_output['event'] += event_key
                dict_output['rep'] += event_rep
                event_key = []
                emg_subphase = []
                event_rep = []
        else:
            last_index = len(list(g))

    df_emg = pd.DataFrame(dict_output)
   
    return df_emg





def event_2_segmentation(filtered_emg,event,show = False,separation = 'sub'): # Checked visually + unit test
    """FROM THE OUTPUT OF EXTRACT EVENT: segments the signal in subphases 
    (Used for Lima, Larivier, Courbalay, Du, Ahern , Neblett)
    (From the EDA of events : no tasks where cut in half, there is always a 'return' with a 'bending')

    Args:
        filtered_emg (_type_): _description_
        event (_type_): " event time line" of the function extract_event
        show (bool, optional): _description_. Defaults to False.

    Returns:
        dataframe: (columns: emg, event, repetition ) each row comprises the emg segment of the corresponding subphase
    """
    

    event_key = []
    emg_subphase = []
    event_rep = []
    rep_cycle = { 'bending':0, 'return':0 }
    last_index = 0

    for k,g in groupby(event):
        if k != -1:
            len_seg = len(list(g))

            rep_cycle[EVENT_BEND[k]] += 1
            event_rep += [rep_cycle[EVENT_BEND[k]]]
            event_key.append(EVENT_BEND[k])
            emg_subphase += [filtered_emg[last_index: last_index + len_seg]]
            last_index += len_seg

    df_emg = [[a,b,c] for a,b,c in zip(emg_subphase,event_key,event_rep)]
    df_emg = pd.DataFrame(df_emg,columns=['emg','event','rep'])

   
    return df_emg






def event_segmentation_inbtw_subpart(emg,event_:pd.DataFrame,win = 1.5): # Checked visually + unit test
    """divide the signal into segments of signal according to the events so that standing and maximal voluntary flexion are extracted
    (Used for Neblett, Ahern)

    Args:
        emg (_type_): _description_
        event (pd.DataFrame): Dataframe with columns: event ['startMotion' or 'stopMotion'] time_sec time_min
        win (float, optional): _description_. Defaults to 1.5.

    Returns:
        Dataframe: Dataframe with columns: emg,event,rep. The event are 'stand' and 'flexion'
    """
    event = event_.copy(deep=True)
    event_key = [] # store for each event its name
    emg_subphase = [] # store for each event its corresponding signal
    event_rep = [] # store for each event the number of time it has been performed
    rep_cycle = { 'startMotion':0, 'stopMotion':0 } # will save the number of standing and mvf tasks that were performed

    if len(event.loc[event['event']=='startMotion'] ) > len(event.loc[event['event']=='stopMotion'] ): # True for every files
        event = event.sort_values('time_sec').iloc[:-1,:] # removal of the last event because it is not part of a new trial
        # the first trial is kept as a full trial eventhought the standing peiod is croped in half in comparison to the other trials
        # the standing period at the beginning of the signal has been used as the reference for the standing/bending trial 
        # (it could have been half of the time at the beginning, before bending, and half of the time at the end, after the flexion)

    for i,row in event.iterrows(): 
        
        current_event = row['event']
        rep_cycle[current_event] += 1   
        ti = row['time_sec'] + row['time_min']*60 # time of the event in sec

        event_rep += [rep_cycle[current_event]]
        event_key.append('stand' if current_event == 'startMotion' else 'flexion')
        # extract the signal from a 3sec window center around the event
        subpart = emg[np.max([0,int((ti - win)*SAMPLING_RATE)]): np.min([len(emg),int((ti + win)*SAMPLING_RATE)])] 
        emg_subphase += [subpart]

    
    
    df_emg = [[a,b,c] for a,b,c in zip(emg_subphase,event_key,event_rep)]
    df_emg = pd.DataFrame(df_emg,columns=['emg','event','rep'])

    # if rep_cycle['startMotion'] != rep_cycle['stopMotion']: ## replace by removing the last event at the beginning of the function
    #     df_emg = df_emg.drop(df_emg[(df_emg['event']== 'stand') & (df_emg['rep'] == rep_cycle['stopMotion']+1)].index)

   
    return df_emg




# def event_segmentation_flex_return(emg,event:pd.DataFrame,win = 1.5): # NOT TESTED YET #NOT USED
#     """divide the signal into segments of signal according to the events so that standing and maximal voluntary flexion are extracted

#     Args:
#         emg (_type_): _description_
#         event (pd.DataFrame): Dataframe with columns: event ['startMotion' or 'stopMotion'] time_sec time_min
#         win (float, optional): _description_. Defaults to 1.5.

#     Returns:
#         Dataframe: Dataframe with columns: emg,event,rep. The event are 'stand' and 'flexion'
#     """
#     event['time'] = event.apply(lambda x: x['time_sec'] + x['time_min']*60,axis=1)
#     event = event.sort_values(by = ['time']).reset_index(drop=True) 

#     emg_subphase = [] # store for each event its corresponding signal
#     rep = 0 
#     i=0
#     row = []
#     #add first standing

#     while i < len(list(event['time']))-1: 
#         current_event = event.iloc[i]['event']
#         next_event = event.iloc[i]['event']

#         t_current = event.iloc[i]['time']
#         t_next  = event.iloc[i]['time']
#         flexion_return = emg[int((t_current + win)*SAMPLING_RATE):int( (t_next- win)*SAMPLING_RATE)]
#         full_flexion_stand = emg[int( (t_next - win)*SAMPLING_RATE ) : int((t_next + win)*SAMPLING_RATE)]

#         if current_event == 'startMotion':
#             assert next_event == 'stopMotion','event_segmentation_flex_return stop motion missing'
#             row = [[ flexion_return, 'flexion', rep],[full_flexion_stand,'full_flexion',rep]]
#         else:
#             row = [[ flexion_return, 'return', rep],[full_flexion_stand,'stand',rep]]
               
#         emg_subphase += row
#         i += 1
        
#     df_emg = pd.DataFrame(emg_subphase,columns=['emg','event','rep'])

   
#     return df_emg




def event_extraction_flex_return(emg,event_:pd.DataFrame,win = 1.5): # Checked visually + unit test
    """compute the events start/stop flexion/standing to isolate the standing and MVF periods from flexion and return from the events start/stopMotion
    (Used for Dankaerts 2009)

    Args:
        emg (_type_): _description_
        event (pd.DataFrame): Dataframe with columns: event ['startMotion' or 'stopMotion'] time_sec time_min
        win (float, optional): _description_. Defaults to 1.5.

    Returns:
        Dataframe: Dataframe with columns:time,event. The event are 'start/stop_flexion/standing'. The time is in seconds
    """
    win = 1.5
    event = event_.copy(deep=True)
    event['time'] = event.apply(lambda x: x['time_sec'] + x['time_min']*60,axis=1)
    event = event.sort_values(by = ['time']).reset_index(drop=True) # all the event are kept so that the two last standing events can be computed

    i=0
    new_tstart,new_tstop = [],[]
    output = []

    # stop standing = beginning of flexion
    # start flexion = beginning of full flexion
    # stop flexion = beginning of return

    for i,row in event.iterrows():
        t = row['time']
        new_tstart = [ np.max([ 0,(t-win)]), f"start_{'standing' if row['event'] == 'startMotion' else 'flexion'}" ] #[ time , event ]
        new_tstop = [ np.min([ len(emg)/SAMPLING_RATE,(t+win)]), f"stop_{'standing' if row['event'] == 'startMotion' else 'flexion'}" ] #[ time , event ]

        output += [new_tstart,new_tstop]

    df_output = pd.DataFrame(output,columns=['time','event'])

   
    return df_output




def plot_event_extraction(emg,event:pd.DataFrame,figs = (6,3),xl='time',yl='Amplitude',plot_title='Emg and subphases',emg2=[]): # NOT USED, PLOT # Checked visually + unit test
    """FROM THE OUTPUT OF  event_extraction_flex_return function: plot a representation of the segmentation 

    Args:
        emg (_type_): _description_
        event (pd.DataFrame): _description_
        figs (tuple, optional): _description_. Defaults to (6,3).
        xl (str, optional): _description_. Defaults to 'time'.
        yl (str, optional): _description_. Defaults to 'Amplitude'.
        plot_title (str, optional): _description_. Defaults to 'Emg and subphases'.
    """

    al2 = 0.20
    fig,ax = plt.subplots(figsize = figs)
    event = event.sort_values(by = ['time']).reset_index(drop=True) 

    for i in range(1,len(event['time'])):
        previous_t,current_t,previous_event = event['time'][i-1],event['time'][i],event['event'][i-1]
        p = plt.axvline(x=previous_t,color='white')
        ax.axvspan(previous_t, current_t, color='red' if previous_event == 'start_flexion' else 'orange' if previous_event == 'stop_flexion' else 'yellow' if previous_event == 'stop_standing' else 'green', alpha=al2)

    t = np.arange(0,len(emg))/SAMPLING_RATE
    ax.set(xlabel=xl, ylabel=yl, title = plot_title)

    c_l =sns.color_palette("Set2")
    c_l2 = sns.color_palette()
    ax.plot(t,emg,color=c_l2[0])
    ax.plot(t,emg)
    if len(emg2) != 0:
        ax.plot(t,emg2,color=c_l2[-1],alpha=1,linewidth=2)

    fig.tight_layout()




def event_segmentation_from_df_time(emg,event_:pd.DataFrame): # Checked visually + unit test
    """ FROM THE OUTPUT of event_extraction_flex_return: segments the signal from the timestamps defined in the input event_
    (USED for Dankaerts 2009, Watson)

    Args:
        emg (np.ndarray): _description_
        event_ (pd.DataFrame): _description_

    Returns:
        DataFrame: columns: emg	event rep 
    """
    if type(emg) != np.ndarray:
        emg = np.array(emg)

    event = event_.copy(deep=True)
    event['time'] = event.apply(lambda x: int(x['time']*SAMPLING_RATE),axis=1)
    emg_subphases = []
    rep = 0
    event_1 = event.loc[0,'event']
    for i in range(event.shape[0]-1):
        if event_1 == event.loc[i,'event']:
            rep += 1
        new_row = [emg[event.loc[i,'time']:event.loc[i+1,'time']],event.loc[i,'event'],rep]
        emg_subphases += [new_row]

    df_emg_subphases = pd.DataFrame(emg_subphases, columns=['emg','event','rep'])
    return df_emg_subphases













# FREQUENCY DOMAIN-------------------------------------------------------



def fft_function(signal, freq_0 = True, show = False, ax = None): # checked unit test
    """https://docs.scipy.org/doc/scipy/tutorial/fft.html

    Args:
        signal (_type_): _description_
        freq_0 (bool, optional): _description_. Defaults to True.
        show (bool, optional): _description_. Defaults to False.

    Returns:
        array: positive frequencies and positive amplitudes
    """
    signal = np.array(signal)
    N = len(signal)
    normalize = 2/N
    fourier = fft(signal)
    frequency_axis = fftfreq(N, d=1.0/SAMPLING_RATE)
    norm_amplitude = np.abs(fourier)*normalize 

    if freq_0:
        positive_freq = frequency_axis>=0
    else:
        positive_freq = frequency_axis>0


    # Plot the results
    if show :
        if not ax:
            fig, ax = plt.subplots(figsize = (5,2))
        ax.plot(frequency_axis[positive_freq], norm_amplitude[positive_freq] )

        ax.set_title('Spectrum')
        ax.set(xlabel='Frequency[Hz]', ylabel='Amplitude')
    
    return frequency_axis[positive_freq], norm_amplitude[positive_freq] 





def median_frequency(emg,type = 'fft'): # checked unit test
    
    assert not empty_value_check(emg), 'Empty value emg median frequency'
    if type == 'welch':
        freq,amp= signal.welch(emg,fs=SAMPLING_RATE)
    elif type == 'fft':
        freq,amp = fft_function(emg,freq_0=False)
        amp = amp **2
    elif type == 'periodogram':
        freq,amp = signal.periodogram(emg,fs=SAMPLING_RATE)

    # return np.median(freq)
    amp_cumsum = np.cumsum(amp)
    median = freq[np.where(amp_cumsum>np.max(amp_cumsum)/2)[0][0]]
    return median


def mean_power_frequency(emg,type = 'fft'):# checked unit test

    assert not empty_value_check(emg), 'mean_power_frequency: empty value emg'
    if type == 'welch':
        freq,amp = signal.welch(emg,fs=SAMPLING_RATE)
    elif type == 'fft':
        freq,amp = fft_function(emg,freq_0=False)
        #without the 0 frequency the mean power frequency is similar to the one computed with welch or the periodogram
        amp = amp**2
    elif type == 'periodogram':
        freq,amp = signal.periodogram(emg,fs=SAMPLING_RATE)

    output = np.sum(freq*amp)/np.sum(amp)
    # return freq,amp,output
    return output




def sliding_mean_power_frequency(emg, win = 1):# checked unit test
    # used for Du
   
    if type(emg) != pd.core.series.Series:
        emg = pd.Series(emg)

    emg_rolling = emg.rolling(win*SAMPLING_RATE, min_periods = 1,center = True,closed = 'both',step = (win*SAMPLING_RATE)//2).apply(mean_power_frequency)
    output = emg_rolling.mean()
    return output





def rolling_fft(emg,win,median=False, unit='sec'): 
    # used in spectrogram_function
    if unit == 'sec': win_frame = int(win*SAMPLING_RATE)
    else: win_frame = int(win)
    freq = []
    amp = []
    med = []
    t = np.arange(win_frame//2,len(emg) - win_frame//2)

    for i in range(win_frame//2,len(emg) - win_frame//2):
        samples = emg[i - win_frame//2:i + win_frame//2]
        freq_per,amp_per= signal.periodogram(samples,fs=SAMPLING_RATE)
        freq += [freq_per]
        amp += [amp_per]
        if median:
            med.append(median_frequency(samples,type = 'periodogram'))

    if median:
        return t, freq, amp, med 
    else:
        return t, freq, amp
    


def spectrogram_function(emg,win=0.1,figs=(8,3),show = False,median=False):
    # used in adaptative_butterfilter
    if median:
        t,freq,amp,med = rolling_fft(emg,win,median)
    else:
        t,freq,amp = rolling_fft(emg,win,median)

    amp_t = np.transpose(amp)
    if show:
        fig,ax = plt.subplots(figsize = figs)
        ax.pcolormesh(t,freq[0],amp_t,shading='gouraud')
        ax1 = ax.twinx()
        ax1.plot(emg)
        ax1.set(ylabel = 'Amplitude V')
        ax.set(ylabel='frequence Hz', xlabel = 'frame')
        fig.tight_layout()
    if median and show:
    
        ax.plot(med, linestyle = '-.', color = 'yellow',alpha = 0.4)
    if median:
        return t,freq,amp,med

    else:
        return t,freq,amp
    


def adaptive_butterfilter(emg,cf=30,win_base=0.3,win_time=0.02,nb_mean=1, nb_std=0,show_th = False,show_spectro=False):
    emg = mean_removal(emg)
    t,freq,amp, med = spectrogram_function(emg, median = True,show = show_spectro)

    _, state_contraction, threshold_amp, _ = double_threshold(med,win=win_base,time_win=win_time,number_mean=nb_mean,number_std=nb_std)

    if show_th:
        plot_2_channel_emg(med,state_contraction*threshold_amp)

    emg_c = emg.copy(deep=True)
    emg_c = np.array(emg_c) 
    i = 0
    for k, g in groupby(state_contraction):
        samples = list(g)
        if k == 0:
            try: # if the number of sample isn't large enough for beeing filtered (ie <15)
                emg_c[i: i + len(samples)] = butterfilter_dual(emg_c[i: i + len(samples)],order=4, c_f=cf,type='highpass')
            except Exception as e:
                pass
        i += len(samples)

    return emg_c








