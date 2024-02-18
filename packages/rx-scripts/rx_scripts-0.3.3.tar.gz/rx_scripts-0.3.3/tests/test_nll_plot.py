import os
import zfit
import matplotlib.pyplot as plt

from stats.nll_plot import plotter as nll_plt

#-------------------------------------------------------------------
def get_nll():
    obs          = zfit.Space('x', limits=(-10, 10))
    mu           = zfit.Parameter("mu", 0, -1, 5)
    sg           = zfit.Parameter("sg", 1,  0, 5)
    gauss        = zfit.pdf.Gauss(obs=obs, mu=mu, sigma=sg)
    nev          = zfit.Parameter("ne", 300,  0, 10000)
    pdf          = gauss.create_extended(nev)
    sampler      = pdf.create_sampler(n=1000)

    nll          = zfit.loss.ExtendedUnbinnedNLL(model=pdf, data=sampler)

    return nll
#---------------------------------
def test_simple():
    nll= get_nll()
    obj= nll_plt(nll=nll)
    obj.make_mncontour(x='mu', y='sg', cl=[0.65, 0.95, 0.98])

    plot_dir  = 'tests/test_nll_plot'
    os.makedirs(plot_dir, exist_ok=True)
    plot_path = f'{plot_dir}/simple.png' 

    plt.savefig(plot_path)
    plt.close('all')
#---------------------------------
def main():
    test_simple()
#---------------------------------
if __name__ == '__main__':
    main()

