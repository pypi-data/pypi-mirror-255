import scipy.optimize    as scy_opt
import scipy.stats       as stat
import matplotlib.pyplot as plt 
import numpy

#---------------------------------------------
def get_pval(arr_val, par, err):
    arr_dev = (arr_val - par) / err 
    chi2    = numpy.sum(arr_dev ** 2)
    ndof    = len(arr_val) - 1 

    pval = 1 - stat.chi2.cdf(chi2, ndof)

    return pval
#---------------------------------------------
def average(arr_y, arr_e):
    '''
    Used to average measurements with errors
    Takes: Array of measurements, array of errors
    Returns: Average value, uncertainty, p-value for null hypothesis: all values are compatible with eachother
    '''
    nval   = arr_y.size
    arr_x  = numpy.linspace(1, nval, nval)

    [avg], [[cov]] = scy_opt.curve_fit(lambda x, b: b, arr_x, arr_y, sigma=arr_e)
    pval           = get_pval(arr_y, avg, arr_e)

    err = numpy.sqrt(cov)

    return avg, err, pval
#---------------------------------------------

