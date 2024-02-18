from zutils.pdf     import dscb as zdscb
from model_analyzer import analyzer  as mana
import zfit

#------------------------------------------------------------
def get_dscb(obs, prefix=None, nent=100, custom=True):
    mu  = zfit.Parameter(f'mu_{prefix}', 2.4, -1, 5)
    sg  = zfit.Parameter(f'sg_{prefix}', 2.3,  1, 5)

    al  = zfit.Parameter(f'al_{prefix}',  1.0,  0,  3)
    nl  = zfit.Parameter(f'nl_{prefix}',  1.3,  0,  5)

    ar  = zfit.Parameter(f'ar_{prefix}', +1.0, +0, +3)
    nr  = zfit.Parameter(f'nr_{prefix}',  2.3,  1,  5)

    if custom:
        pdf = zdscb(obs=obs, mu=mu, sg=sg, al=al, nl=nl, ar=ar, nr=nr)
    else:
        pdf = zfit.pdf.DoubleCB(obs=obs, mu=mu, sigma=sg, alphal=al, nl=nl, alphar=ar, nr=nr)

    nev = zfit.Parameter(f'nev_{prefix}', nent,  0, 1e5)

    pdf = pdf.create_extended(nev, name=prefix)

    return pdf
#------------------------------------------------------------
def test_perf():
    obs= zfit.Space('x', limits=(-10, 10))
    pdf_1 = get_dscb(obs, prefix='perf_1')
    pdf_2 = get_dscb(obs, prefix='perf_2')
    pdf   = zfit.pdf.SumPDF([pdf_1, pdf_2])

    obj= mana(pdf=pdf)
    obj.sampling_speed()
#------------------------------------------------------------
def test_fit():
    obs= zfit.Space('x', limits=(-10, 10))
    pdf= get_dscb(obs, prefix='fit', nent=10000, custom=True)

    obj= mana(pdf=pdf)
    obj.out_dir = 'tests/zdscb/fit'
    obj.fit(nfit=400)
#------------------------------------------------------------
def test_simple():
    obs= zfit.Space('x', limits=(-10, 10))
    pdf= get_dscb(obs, prefix='simple')
#------------------------------------------------------------
def main():
    test_fit()
#------------------------------------------------------------
if __name__ == '__main__':
    main()

