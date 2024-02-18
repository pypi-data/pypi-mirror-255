import numpy as np
from scipy.stats import chi2


def _get_errors_poisson(data, a=0.317311):
    """
    Uses chi-squared info to get the poisson interval.
    """
    low, high = chi2.ppf(a / 2, 2 * data) / 2, chi2.ppf(1 - a / 2, 2 * data + 2) / 2
    return np.array(data - low), np.array(high - data)


def _get_errors_sW2(x, weights=None, range=None, bins=60):
    """
    Compute errors for weighted samples
    """
    if weights is not None:
        values = np.histogram(x, bins, range, weights=weights * weights)[0]
    else:
        values = np.histogram(x, bins, range)[0]
    return np.sqrt(values)


class Histogram:
    def __init__(
        self, data: np.ndarray, bins=10, weights=None, density=False, **kwargs
    ) -> None:
        """
        Wrap around NumPy histogram to compute the histogram of a dataset.

        Computes and saves counts, bin edges, bin centers, integral, errors on bins and errors on counts

        Parameters
        ----------
        data : array_like
            Input data
        bins : int or sequence of scalars or str, optional
            If `bins` is an int, it defines the number of equal-width
            bins in the given range (10, by default). If `bins` is a
            sequence, it defines a monotonically increasing array of bin edges,
            including the rightmost edge, allowing for non-uniform bin widths.

            If `bins` is a string, it defines the method used to calculate the
            optimal bin width, as defined by `histogram_bin_edges`.
        weights : array_like, optional
            An array of weights, of the same shape as `a`.  Each value in
            `a` only contributes its associated weight towards the bin count
            (instead of 1). If `density` is True, the weights are
            normalized, so that the integral of the density over the range
            remains 1.
        density : bool, optional
            If ``False``, the result will contain the number of samples in
            each bin. If ``True``, the result is the value of the
            probability *density* function at the bin, normalized such that
            the *integral* over the range is 1. Note that the sum of the
            histogram values will not be equal to 1 unless bins of unity
            width are chosen; it is not a probability *mass* function.
        """
        # create histogram and get counts and bin edges
        c, e = np.histogram(data, bins=bins, weights=weights, density=density, **kwargs)

        # compute bin centers, binwidth and integral
        b = 0.5 * (e[1:] + e[:-1])
        norm = np.sum(c * np.diff(e))

        # compute errors on x-axis
        x_errh = e[1:] - b
        x_errl = b - e[:-1]

        # compute 1-sigma errors on y-axis
        if weights is not None:
            y_errl, y_errh = _get_errors_poisson(c)
            y_errl = (
                y_errl**2
                + _get_errors_sW2(data, weights=weights, bins=bins, **kwargs) ** 2
            )
            y_errh = (
                y_errh**2
                + _get_errors_sW2(data, weights=weights, bins=bins, **kwargs) ** 2
            )
            y_errl = np.sqrt(y_errl)
            y_errh = np.sqrt(y_errh)
        else:
            y_errl, y_errh = _get_errors_poisson(c)

        if density:
            c /= norm
            y_errl /= norm
            y_errh /= norm

        # populate class attributes
        self.counts = c
        self.edges = e
        self.bins = b
        self.norm = norm
        self.xerr_l = x_errl
        self.xerr_h = x_errh
        self.yerr_l = y_errl
        self.yerr_h = y_errh


def make_hist(data, bins=10, weights=None, density=False, **kwargs) -> Histogram:
    return Histogram(data=data, bins=bins, weights=weights, density=density, **kwargs)


import unittest


class TestHistogram(unittest.TestCase):
    def test_create_histogram(self):
        mu, sigma, size = 0, 1, 1000
        x = np.random.normal(mu, sigma, size)
        hx = Histogram(x)

        c, e = np.histogram(x)

        self.assertTrue(np.allclose(c, hx.counts))
        self.assertTrue(np.allclose(e, hx.edges))

    def test_normalise_histogram(self):
        mu, sigma, size = 0, 1, 1000
        x = np.random.normal(mu, sigma, size)
        hx = Histogram(x, density=True)
        self.assertEqual(hx.norm, 1.0)

    def test_errors(self):
        """
        TODO
        """
        pass


if __name__ == "__main__":
    unittest.main()
