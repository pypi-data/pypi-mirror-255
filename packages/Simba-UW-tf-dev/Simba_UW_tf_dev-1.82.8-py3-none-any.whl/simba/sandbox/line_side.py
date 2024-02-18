import numpy as np
from numba import prange, njit

@njit('(float32[:,:,:], float32[:, :])')
def point_lineside(lines: np.ndarray,
                   points: np.ndarray) -> np.ndarray:
    """
    Determine the relative position of a point (left vs right) with respect to a lines in each frame.

    :param numpy.ndarray lines: An array of shape (N, 2, 2) representing N lines, where each line is defined by two points. The first point that denotes the beginning of the line, the second point denotes the end of the line.
    :param numpy.ndarray point: An array of shape (N, 2) representing N points.
    :return np.ndarray: An array of length N containing the results for each line. 2 if the point is on the right side of the line. 1 if the point is on the left side of the line. 0 if the point is on the line.

    :example:
    >>> lines = np.array([[[25, 25], [25, 20]], [[15, 25], [15, 20]], [[15, 25], [50, 20]]]).astype(np.float32)
    >>> points = np.array([[20, 0], [15, 20], [90, 0]]).astype(np.float32)
    >>> point_lineside(lines=lines, points=points)
    """
    results = np.full((lines.shape[0]), np.nan)
    threshhold = 1e-9
    for i in prange(lines.shape[0]):
        line, point = lines[i], points[i]
        v = ((line[1][0] - line[0][0]) * (point[1] - line[0][1]) - (line[1][1] - line[0][1]) * (point[0] - line[0][0]))
        if v >= threshhold:
            results[i] = 2
        elif v <= -threshhold:
            results[i] = 1
        else:
            results[i] = 0
    return results

lines = np.array([[[25, 25], [25, 20]], [[15, 25], [15, 20]], [[15, 25], [50, 20]]]).astype(np.float32)
points = np.array([[20, 0], [15, 20], [90, 0]]).astype(np.float32)
point_lineside(lines=lines, points=points)