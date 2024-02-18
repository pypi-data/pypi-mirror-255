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
        # do not normalise yet, as errors must first be assessed
        c, e = np.histogram(data, bins=bins, weights=weights, density=False, **kwargs)

        # compute bin centers and integral
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
            c = c / norm
            y_errl = y_errl / norm
            y_errh = y_errh / norm
            norm = np.sum(c * np.diff(e))

        # populate class attributes
        self.data = data
        self.weights = weights
        self.counts = c
        self.density = density
        self.edges = e
        self.bins = b
        self.norm = norm
        self.xerr = [x_errl, x_errh]
        self.yerr = [y_errl, y_errh]

    def __add__(self, other):
        if not isinstance(other, Histogram):
            raise TypeError("You must provide an instance of Histogram to add")

        if not np.allclose(self.bins, other.bins):
            raise ValueError("Histograms must have the same bin configuration")

        # Handle data
        combined_data = np.concatenate([self.data, other.data])

        # Handle weights
        if self.weights is None and other.weights is None:
            combined_weights = None
        elif self.weights is None:
            combined_weights = np.concatenate([np.ones_like(self.data), other.weights])
        elif other.weights is None:
            combined_weights = np.concatenate([self.weights, np.ones_like(other.data)])
        else:
            combined_weights = np.concatenate([self.weights, other.weights])

        # Handle density
        if (self.density and not other.density) or (not self.density and other.density):
            raise AttributeError("Histograms must have the same density configuration")

        return Histogram(
            combined_data,
            bins=self.edges,
            weights=combined_weights,
            density=self.density,
        )

    def __mul__(self, factor):
        if not isinstance(factor, (int, float)):
            raise ValueError("Multiplication factor must be a scalar (int or float)")

        weights = (
            np.ones_like(self.data) if (self.weights is None) else self.weights.copy()
        )

        weights *= factor

        return Histogram(
            self.data,
            bins=self.edges,
            weights=weights,
            density=self.density,
        )

    def __rmul__(self, factor):
        return self.__mul__(factor)


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
        np.testing.assert_almost_equal(hx.norm, 1.0)

    def test_add_unweighted_unnormalised_histogram(self):
        mu, sigma, size = 0, 1, 1000
        x1 = np.random.normal(mu, sigma, size)
        x2 = np.random.normal(mu, sigma, size)
        bins = np.arange(-3, +4, 1)

        h1 = Histogram(x1, bins=bins)
        h2 = Histogram(x2, bins=bins)
        h = h1 + h2

        c, _ = np.histogram(np.concatenate([x1, x2]), bins=bins)
        self.assertTrue(np.allclose(c, h.counts))

    def test_add_unweighted_normalised_histogram(self):
        mu, sigma, size = 0, 1, 1000
        x1 = np.random.normal(mu, sigma, size)
        x2 = np.random.normal(mu, sigma, size)
        bins = np.arange(-3, +4, 1)

        h1 = Histogram(x1, bins=bins, density=True)
        h2 = Histogram(x2, bins=bins, density=True)
        h = h1 + h2

        c, _ = np.histogram(np.concatenate([x1, x2]), bins=bins, density=True)
        try:
            self.assertTrue(np.allclose(c, h.counts))
        except AssertionError:
            print("c: ", c)
            print("h.counts: ", h.counts)
        np.testing.assert_almost_equal(h.norm, 1.0)

    def test_add_weighted_unnormalised_histogram(self):
        from scipy.stats import norm, expon

        mu, sigma, size = 0, 1, 1000
        x1 = np.linspace(-4.0, 4.0, size)
        x2 = np.linspace(-5.0, 2.0, size)
        weights1 = norm.pdf(x1)
        weights2 = expon.pdf(x2)
        bins = np.arange(-3, +4, 1)

        h1 = Histogram(x1, weights=weights1, bins=bins)
        h2 = Histogram(x2, weights=weights2, bins=bins)
        h = h1 + h2

        c, _ = np.histogram(
            np.concatenate([x1, x2]),
            bins=bins,
            weights=np.concatenate([weights1, weights2]),
        )
        try:
            self.assertTrue(np.allclose(c, h.counts))
        except AssertionError:
            print("c: ", c)
            print("h.counts: ", h.counts)
            self.assertTrue(False)

    def test_add_weighted_normalised_histogram(self):
        from scipy.stats import norm, expon

        size = 1000
        x1 = np.linspace(-4.0, 4.0, size)
        x2 = np.linspace(-5.0, 2.0, size)
        weights1 = norm.pdf(x1)
        weights2 = expon.pdf(x2)
        bins = np.arange(-3, +4, 1)

        h1 = Histogram(x1, weights=weights1, bins=bins, density=True)
        h2 = Histogram(x2, weights=weights2, bins=bins, density=True)
        h = h1 + h2

        c, _ = np.histogram(
            np.concatenate([x1, x2]),
            bins=bins,
            weights=np.concatenate(
                [weights1, weights2],
            ),
            density=True,
        )
        self.assertTrue(np.allclose(c, h.counts))

    def test_mul_unweighted_unnormalised_histogram(self):
        mu, sigma, size = 0, 1, 1000
        x = np.random.normal(mu, sigma, size)
        bins = np.arange(-3, +4, 1)

        factor = 3.0

        # try all multiplications
        h = Histogram(x, bins=bins)
        init_norm = h.norm
        h = factor * h
        h = h * factor
        h *= factor

        c, _ = np.histogram(x, bins=bins)
        self.assertTrue(np.allclose(factor**3 * c, h.counts))
        np.testing.assert_almost_equal(h.norm, init_norm * factor**3)

    def test_mul_unweighted_normalised_histogram(self):
        """
        Scaling does not affect to normalised histograms
        """
        mu, sigma, size = 0, 1, 1000
        x = np.random.normal(mu, sigma, size)
        bins = np.arange(-3, +4, 1)

        factor = 3.0

        # try all multiplications
        h = Histogram(x, bins=bins, density=True)
        h = factor * h
        h = h * factor
        h *= factor

        c, _ = np.histogram(x, bins=bins, density=True)
        try:
            self.assertTrue(np.allclose(c, h.counts))
        except AssertionError:
            print("left: ", c)
            print("right: ", h.counts)
        np.testing.assert_almost_equal(h.norm, 1.0)

    def test_mul_weighted_unnormalised_histogram(self):
        from scipy.stats import norm

        size = 1000
        x = np.linspace(-3.0, 3.0, size)
        weights = norm.pdf(x)
        bins = np.arange(-3, +4, 1)

        factor = 3.0

        # try all multiplications
        h = Histogram(x, bins=bins, weights=weights, density=False)
        init_norm = h.norm
        h = factor * h
        h = h * factor
        h *= factor

        c, _ = np.histogram(x, bins=bins, weights=weights, density=False)
        try:
            self.assertTrue(np.allclose(factor**3 * c, h.counts))
        except AssertionError:
            print("left: ", factor**3 * c)
            print("right: ", h.counts)
        np.testing.assert_almost_equal(h.norm, init_norm * factor**3)

    def test_mul_weighted_normalised_histogram(self):
        """
        Scaling does not affect to normalised histograms
        """
        mu, sigma, size = 0, 1, 1000
        x = np.random.normal(mu, sigma, size)
        bins = np.arange(-3, +4, 1)

        factor = 3.0

        # try all multiplications
        h = Histogram(x, bins=bins, density=True)
        h = factor * h
        h = h * factor
        h *= factor

        c, _ = np.histogram(x, bins=bins, density=True)
        try:
            self.assertTrue(np.allclose(c, h.counts))
        except AssertionError:
            print("left: ", c)
            print("right: ", h.counts)
        np.testing.assert_almost_equal(h.norm, 1.0)

    def test_errors(self):
        """
        TODO
        """
        pass


if __name__ == "__main__":
    unittest.main()
