import numpy as np
from numba import njit
from typing import List
from shapely.geometry import Polygon, LineString, GeometryCollection
from shapely.ops import split


#@njit('(int64[:,:], int64[:])')
def extend_line_to_bounding_box_edges(line_points: np.ndarray,
                                      bounding_box: np.ndarray) -> np.ndarray:
    x1, y1 = line_points[0]
    x2, y2 = line_points[1]
    min_x, min_y, max_x, max_y = bounding_box

    if x1 == x2:
        intersection_points = np.array([[x1, max(min_y, 0)], [x1, min(max_y, 50)]]).astype(np.float32)
    elif y1 == y2:
        intersection_points = np.array([[min_x, y1], [max_x, y1]]).astype(np.float32)
    else:
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1

        # Calculate intersection points with the bounding box boundaries
        x_min_intersection = (min_y - intercept) / slope
        x_max_intersection = (max_y - intercept) / slope

        # Clip the intersection points to ensure they are within the valid range
        #x_min_intersection = np.clip(x_min_intersection, min_x, max_x)
        #x_max_intersection = np.clip(x_max_intersection, min_x, max_x)

        intersection_points = np.array([[x_min_intersection, min_y],
                                        [x_max_intersection, max_y]]).astype(np.float32)

    return intersection_points


line_points = np.array([[25, 25], [35, 25]]).astype(np.int64)
bounding_box = np.array([0, 0, 1500, 1350]).astype(np.int64)

line_points = np.array([[25, 25], [35, 25]]).astype(np.int64)
bounding_box = np.array([0, 0, 50, 50]).astype(np.int64)

intersection_points = extend_line_to_bounding_box_edges(line_points, bounding_box)
print(intersection_points)
#line_split_bounding_box(intersections=intersection_points, bounding_box=bounding_box)

#print(intersection_points)
# print("Extended Line:", extended_line)
# print("Intersection Points:", intersection_points)
