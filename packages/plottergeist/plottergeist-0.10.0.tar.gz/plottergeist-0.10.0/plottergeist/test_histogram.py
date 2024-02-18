from histogram import make_hist
from fig_creator import make_plot
from scipy.stats import norm, genlogistic
import style
from os import system
import numpy as np

fig, ax = make_plot(ndim=1, pull=False)

ll = -3.0
ul = 3.0

size1 = 50000
size2 = 100000
size = size1 + size2
frac1 = size1 / size
frac2 = 1.0 - frac1
binedges = np.linspace(ll, ul, 50)


x1 = []
while len(x1) != size1:
    data = norm.rvs(size=size1 - len(x1))
    x1.extend(data[(ll <= data) & (data <= ul)])
x1 = np.array(x1)

x2 = []
while len(x2) != size2:
    data = genlogistic.rvs(c=0.412, size=size2 - len(x2))
    x2.extend(data[(ll <= data) & (data <= ul)])
x2 = np.array(x2)

print("Len1: {} Len2: {}".format(len(x1), len(x2)))

data = np.concatenate([x1, x2])
hdata = make_hist(data, bins=binedges)


x1 = np.linspace(ll, ul, 100000)
x2 = np.linspace(ll, ul, 200000)
pdf1 = norm.pdf(x1)
pdf2 = genlogistic.pdf(x2, c=0.412)
# pdf = frac1 * pdf1 / pdf1.sum() + frac2 * pdf2 / pdf2.sum()
# pdf /= pdf.sum()

h1 = make_hist(x1, weights=pdf1, bins=binedges, density=True)
h2 = make_hist(x2, weights=pdf2, bins=binedges, density=True)
h = size * (frac1 * h1 + frac2 * h2)
# h = make_hist(x, weights=pdf, bins=binedges, density=False)

ax.errorbar(
    hdata.bins,
    hdata.counts,
    # xerr=hdata.xerr,
    yerr=hdata.yerr,
    fmt=".",
    color="black",
    label="Data",
)

# ax.hist(
#     x,
#     weights=pdf * hdata.norm / h.norm,
#     bins=binedges,
#     histtype="step",
#     label="Total PDF",
# )
ax.hist(
    x1,
    weights=pdf1 * frac1 * hdata.norm / h.norm,
    bins=binedges,
    histtype="step",
    label="Gauss PDF",
)
ax.hist(
    x2,
    weights=pdf2 * frac2 * hdata.norm / h.norm,
    bins=binedges,
    histtype="step",
    label="GenLog PDF",
)


ax.legend(loc="best")


fig.savefig("test.pdf")
system("open test.pdf")
