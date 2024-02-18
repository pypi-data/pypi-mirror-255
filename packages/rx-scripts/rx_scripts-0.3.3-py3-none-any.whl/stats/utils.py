
from logzero import logger as log

#--------------------------------------------
def error_to_covariance(l_error):
    """
    Will transform a list of errors into a diagonal covariance matrix 

    Parameters
    ---------------------
    l_error (list): List of floats, symbolizing errors

    Returns
    ---------------------
    l_cov (list): List of lists with variannces in the diagonal
    """

    nerror = len(l_error)
    if nerror == 0:
        log.error(f'Introduced empty list')
        raise ValueError

    l_cov = []
    for i_err, err in enumerate(l_error):
        row = nerror * [0]
        row[i_err] = err ** 2
        l_cov.append(row)

    return l_cov
#--------------------------------------------

