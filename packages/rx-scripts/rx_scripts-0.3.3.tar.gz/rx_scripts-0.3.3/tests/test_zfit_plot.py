import zutils.utils as zut
import numpy
import matplotlib.pyplot as plt


#-----------------------------
def test_simple():
    arr_val = numpy.random.normal(loc = 0, scale = 1, size = 1000)
    mu, sg  = zut.fit_pull(arr_val, fit_sig=2, plot=True)
    plt.show()
#-----------------------------
def main():
    test_simple()
#-----------------------------
if __name__ == '__main__':
    main()

