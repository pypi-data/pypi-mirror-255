import numpy
import zfit
import tqdm

from zutils.pdf  import shape
from zutils.plot import plot   as zfp

import matplotlib.pyplot as plt

#--------------------------------------
def delete_all_pars():
    d_par = zfit.Parameter._existing_params
    l_key = list(d_par.keys())

    for key in l_key:
        del(d_par[key])
#--------------------------------------
def get_model():
    obs  = zfit.Space('x', limits=(-10, 10))
    mu   = zfit.Parameter("mu", 2.4, -1, 5)
    sg   = zfit.Parameter("sg", 1.3,  0, 5) 
    gauss= zfit.pdf.Gauss(obs=obs, mu=mu, sigma=sg)

    return gauss, obs
#--------------------------------------
def test_simple():
    l_xorg = numpy.arange(-10, +10, 0.1).tolist()
    l_xorg.append(10)
    arr_xorg = numpy.array(l_xorg)
    pdf, obs = get_model()
    arr_yorg = [ pdf.pdf(x).numpy()[0] for x in arr_xorg]
    
    pdf      = shape(obs, arr_xorg, arr_yorg)
    arr_xnew = numpy.arange(-4.05, +8.01, 0.1)
    arr_ynew = [ pdf.pdf(x) for x in tqdm.tqdm(arr_xnew, ascii=' -')]
        
    plt.scatter(arr_xorg, arr_yorg, label='Original')
    plt.scatter(arr_xnew, arr_ynew, label='Interpolated')
    plt.legend()
    plt.show()

    delete_all_pars()
#--------------------------------------
def test_sampler():
    l_xorg = numpy.arange(-10, +10, 0.1).tolist()
    l_xorg.append(10)
    arr_xorg = numpy.array(l_xorg)
    pdf, obs = get_model()
    arr_yorg = [ pdf.pdf(x).numpy()[0] for x in arr_xorg]
    
    nev      = zfit.Parameter('nev', 1000, 0, 1e5)
    pdf      = shape(obs, arr_xorg, arr_yorg)
    pdf.set_yield(nev)
    sam      = pdf.create_sampler()

    obj = zfp(data=sam, model=pdf)
    obj.plot(nbins=50)

    plt.show()

    delete_all_pars()
#--------------------------------------
def main():
    test_simple()
    test_sampler()
#--------------------------------------
if __name__ == '__main__':
    main()

