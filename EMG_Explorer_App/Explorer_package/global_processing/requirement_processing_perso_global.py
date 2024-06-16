import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal,interpolate
from scipy.signal import hilbert
import functools
import inspect

FIG_SIZE = (15,3)
SAMPLING_RATE = 1000