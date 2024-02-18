import hist
import numpy as np
import pandas as pd
import zfit
from fitter import zfitter


def show(data):
    data_hist = hist.Hist(hist.axis.Regular(bins=10, start=-5, stop=5))
    data_hist.fill(data)
    data_hist.show()


def do_test(data, suffix=""):
    obs = zfit.Space("obs", limits=(-5, 5))
    mu = zfit.Parameter("mu" + suffix, 0, -5, 5)
    sigma = zfit.Parameter("sigma" + suffix, 1, 0.1, 5)
    pdf = zfit.pdf.Gauss(mu=mu, sigma=sigma, obs=obs)
    n = zfit.Parameter("n" + suffix, 1000, 0, 1e6)
    pdf_extended = pdf.create_extended(n)
    fit = zfitter(pdf_extended, data)
    res = fit.fit()
    show(zfit.run(zfit.z.unstack_x(fit._data_zf)))
    print(res)
    print(res.gof)
    return n.value(), res.gof


def test_all():
    # numpy array
    data = np.random.normal(loc=0, scale=1, size=1000)
    n_np, gof_np = do_test(data, "np")

    # pandas DataFrame
    data_df = pd.DataFrame(data, columns=["obs"])
    n_df, gof_df = do_test(data_df, "df")

    assert n_np == n_df and gof_np == gof_df, "pandas.DataFrame failed"

    # zfit data
    obs = zfit.Space("obs", limits=(-5, 5))
    data_zf = zfit.Data.from_numpy(obs=obs, array=data)
    n_zf, gof_zf = do_test(data_zf, "zf")

    assert n_np == n_zf and gof_zf == gof_np, "zfit.Data failed"

    print("All tests passed!")


if __name__ == "__main__":
    test_all()

