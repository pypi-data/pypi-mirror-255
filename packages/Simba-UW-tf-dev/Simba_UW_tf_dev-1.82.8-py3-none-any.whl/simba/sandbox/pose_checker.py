import pandas as pd
import json
from collections import OrderedDict, defaultdict
import ast
import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.ops import split
import matplotlib.pyplot as plt

from numba import njit, prange

@njit('(float32[:,:,:], float64[:])')
def static_point_lineside(lines: np.ndarray,
                          point: np.ndarray) -> np.ndarray:

    """
    Determine the relative position of a static point with respect to multiple lines.

    :param numpy.ndarray lines: An array of shape (N, 2, 2) representing N lines, where each line is defined by two points.
    :param numpy.ndarray point: A 2-element array representing the coordinates of the static point.
    :return np.ndarray: An array of length N containing the results for each line. 2 if the point is on the right side of the line. 1 if the point is on the left side of the line. 0 if the point is on the line.

    :example:
    >>> line = np.array([[[25, 25], [25, 20]], [[15, 25], [15, 20]], [[15, 25], [50, 20]]]).astype(np.float32)
    >>> point = np.array([20, 0]).astype(np.float64)
    >>> static_point_lineside(lines=line, point=point)
    >>> [1. 2. 1.]
    """

    results = np.full((lines.shape[0]), np.nan)
    threshhold = 1e-9
    for i in prange(lines.shape[0]):
        v = ((lines[i][1][0] - lines[i][0][0]) * (point[1] - lines[i][0][1]) - (lines[i][1][1] - lines[i][0][1]) * (point[0] - lines[i][0][0]))
        if v >= threshhold:
            results[i] = 2
        elif v <= -threshhold:
            results[i] = 1
        else:
            results[i] = 0
    return results













    # val = ((line[1][0] - line[0][0]) * (point[1] - line[0][1]) - (line[1][1] - line[0][1]) * (point[0] - line[0][0]))
    # thresh = 1e-9
    # if val >= thresh:
    #     return "right"
    # elif val <= -thresh:
    #     return "left"
    # else:
    #     return "point is on the line"
    #
    #

# line = np.array([[[25, 25], [25, 20]],
#                  [[15, 25], [15, 20]],
#                  [[15, 25], [50, 20]]]).astype(np.float32)
# point = np.array([20, 0]).astype(np.float64)
#
# static_point_side_checker(lines=line, point=point)
#
# #
# #
#
#
#
#     tail_cords = df[[f'{point_2}_x', f'{point_2}_y']].values[0]
#     nose_cords = df[[f'{point_1}_x', f'{point_1}_y']].values[0]
#
#     slope = (tail_cords[1] - nose_cords[1]) / (tail_cords[0] - nose_cords[0])
#
#     slope = 0
#     x_values = np.linspace(-10, 10, 1000)
#     # intercept = nose_cords[1] - slope * nose_cords[0]
#     # print(intercept, slope)
#     # x_values = np.linspace(min(tail_cords[0], x2) - 2, max(x1, x2) + 2, 1000)
#     # extended_y = slope * extended_x + intercept
#     # print(extended_y)
#     y_values_line = slope * x_values
#
#     # Create a LineString representing the line
#     line = LineString(np.column_stack([x_values, y_values_line]))
#
#     # Create a bounding box around the line
#     bbox = line.envelope
#
#     # Split the bounding box with the line to get left and right polygons
#     polygons = split(bbox, line)
#
#     # Plot the line and polygons
#     fig, ax = plt.subplots()
#     ax.plot(x_values, y_values_line, label='Line', color='black')
#     ax.plot(*bbox.exterior.xy, label='Bounding Box', color='gray', linestyle='--')
#
#     for poly, color, label in zip(polygons, ['red', 'blue'], ['Left Region', 'Right Region']):
#         ax.plot(*poly.exterior.xy, color=color, alpha=0.3, label=label)
#
#     # Set labels and title
#     ax.set_xlabel('X-axis')
#     ax.set_ylabel('Y-axis')
#     ax.set_title('Polygons to the Left and Right of the Line')
#     ax.legend()
#     ax.grid(True)
#
#     plt.show()
#
#
#
#
#
# data_path = '/Users/simon/Downloads/Frank_103123.csv'
# annotations = pd.read_csv(data_path, delimiter=',').head(10)
# annotations = annotations.loc[:, ~annotations.columns.str.contains('^Unnamed')].drop(['index'], axis=1)
# body_parts = annotations.columns.tolist()[2:]
# data = pd.read_csv(data_path, index_col=0).reset_index(drop=True)
# index_video = data[['index', 'VIDEO', 'IMAGE']]
# data = data.drop(['index', 'VIDEO', 'IMAGE'], axis=1)
#
#
# results = defaultdict(list)
# for idx, row in data.iterrows():
#     for bp_name, bp_values in pd.DataFrame(row).iterrows():
#         bp_values = list(ast.literal_eval(bp_values.values[0]).values())
#         results[f'{bp_name}_x'].append(bp_values[0])
#         results[f'{bp_name}_y'].append(bp_values[1])
# sorted_df = pd.DataFrame(results)
#
# pose_direction_checker(df=sorted_df, point_1='NOSE', point_2='TAIL')
#

        #print(list(ast.literal_eval(bp_values).values()))
