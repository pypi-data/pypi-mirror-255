import matplotlib.pyplot as plt
import numpy as np
import pandas as pnd

#---------------------------------------------------
def plot_pull(df, var=None, val=None, err=None):
    '''
    Function used to plot pulls

    Parameters:
    ----------------------
    df : Dataframe with data to plot
    var (str): Name of column storing variable names
    val (str): Name of column with pull mean 
    err (str): Name of column with pull RMS 
    '''
    df     = df.reset_index(drop=True)
    index  = df.index.tolist()
    sr_val = df[val] 
    sr_var = df[var] 
    sr_err = df[err] 

    arr_y  = [index[0] - 1] + index + [index[-1] + 1]
    
    plt.barh(y=sr_var, width=sr_val, xerr=sr_err, align='center', alpha=0.4, color='none')
    plt.plot(sr_val, sr_var, marker="o", linestyle="", alpha=0.8, color='b')
    plt.gca().set_xlim(-3, +3)
    plt.gca().fill_betweenx(arr_y, -2, -1, color='y', alpha=0.5)
    plt.gca().fill_betweenx(arr_y, -1, +1, color='g', alpha=0.5)
    plt.gca().fill_betweenx(arr_y, +1, +2, color='y', alpha=0.5)

    plt.yticks(index, sr_var)
#---------------------------------------------------

