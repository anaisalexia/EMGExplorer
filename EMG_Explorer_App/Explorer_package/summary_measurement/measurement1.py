import sys
sys.path.append('EMG_Explorer_App/Explorer_package/summary_measurement')

from requirement_measurement1 import *

def mean(array):
    return np.nanmean(array)

def noChange(array):
    return array

