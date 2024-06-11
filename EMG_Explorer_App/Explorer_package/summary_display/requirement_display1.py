import plotly.express as px
import pandas as pd
import numpy as np

def array_to_df(array):
    return pd.DataFrame(array,columns=['y'],index=np.arange(len(array)))