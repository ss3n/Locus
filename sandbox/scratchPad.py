import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
from numpy.random import uniform
from matplotlib import pyplot as plt

p = uniform(0, 5, (20,2))
vor = Voronoi(p)
voronoi_plot_2d(vor); plt.axes().set_aspect('equal'); plt.show()