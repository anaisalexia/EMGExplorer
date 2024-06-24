import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal,interpolate
from scipy.signal import hilbert
import functools
import inspect

FIG_SIZE = (15,3)
SAMPLING_RATE = 1000



def DecoratorGlobal(function):
    """Apply a function, usually a "global processing function", to all the channel of a path

    Args:
        function (function): function to apply to a set of data

    Returns:
        _type_: _description_
    """
    # @functools.wraps(function)
    @functools.wraps(function)
    def wrapper(**arg):
        loader = arg['loader']
        path = arg['path']
        del arg['path']
        del arg['loader']

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

    # wrapper.__signature__ = inspect.signature(function)   
    # wrapper.__name__ = function.__name__   

    return wrapper



def empty_value_check(emg):
    """Check empty values, returns a bool

    Args:
        emg (ndarray / pd.Series): _description_

    Returns:
        bool: True if there is at least one empty value
    """
    if type(emg) != pd.core.series.Series:
        emg = pd.Series(emg)
    out = emg.isnull().values.any() #is null detects missing values for an array-like object, values takes the values of the pandas series and any detects if there is any True
    return out
