import matplotlib.pyplot as plt
import numpy as np
import plottergeist
import os


# Example usage:
# Generate some sample data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
fig, ax = plottergeist.make_plot(ndim=2, pull=False)

# Plot four subplots with residuals arranged as described
ax[0].plot(x, y1)
ax[1].plot(x, y2)

fig.savefig("caca.pdf")

os.system("open caca.pdf")
