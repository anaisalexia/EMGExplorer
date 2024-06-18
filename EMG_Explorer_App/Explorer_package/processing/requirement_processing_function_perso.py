import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal,interpolate
from scipy.signal import hilbert

FIG_SIZE = (15,3)
SAMPLING_RATE = 1000

def empty_value_check(emg):
    if type(emg) != pd.core.series.Series:
        emg = pd.Series(emg)
    out = emg.isnull().values.any() 
    return out
