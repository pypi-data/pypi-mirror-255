import numpy as np
from shapely.geometry import Polygon
from numba import jit


import numpy as np
@jit(nopython=True)
def intersection(vertices_a, vertices_b) -> bool:

    edges_a = np.roll(vertices_a - np.roll(vertices_a, 2), -2)
    edges_b = np.roll(vertices_b - np.roll(vertices_b, 2), -2)

    edges = np.append(edges_a, edges_b, 0)

    axes = edges[::-1].copy()
    axes[:, 1] = -axes[:, 1]

    # Manually normalize axes without using axis or keepdims
    axes_magnitude = np.sqrt(np.sum(axes ** 2, axis=-1))
    print(axes_magnitude)
    print(axes)
    # axes = axes / axes_magnitude[:, np.newaxis]
    #
    # proj_a = axes @ vertices_a.T
    # proj_b = axes @ vertices_b.T
    #
    # a_min = proj_a.min(axis=1)
    # a_max = proj_a.max(axis=1)
    # b_min = proj_b.min(axis=1)
    # b_max = proj_b.max(axis=1)
    #
    # return not (((b_min > a_min) | (a_min > b_max)) &
    #             ((b_min > a_max) | (a_max > b_max)) &
    #             ((a_min > b_min) | (b_min > a_max)) &
    #             ((a_min > b_max) | (b_max > a_max))).any()


a = Polygon(np.array([(0, 0),(10, 0),(10,10),(0,10)], dtype=float))
b = Polygon(np.array([(5, 5),(15, 5),(15,15),(5,15)], dtype=float))
c = Polygon(np.array([(5,15),(15,15),(15,25),(5,25)], dtype=float))

a = np.array(a.exterior.coords)
b = np.array(b.exterior.coords)
intersection(a, b)