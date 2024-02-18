from typing import Tuple, List, Optional, Dict
import cv2
import numpy as np
from shapely.geometry import Point, Polygon, MultiPoint
from scipy.spatial import Voronoi, voronoi_plot_2d, Delaunay
import shapely.geometry
from shapely.ops import triangulate
import matplotlib.pyplot as plt

def bucket_img_into_grid_points(point_distance: int,
                                px_per_mm: float,
                                img_size: Tuple[int, int],
                                border_sites: Optional[bool] = True) -> Dict[Tuple[int, int], Point]:

    """
    Generate a grid of evenly spaced points within an image. Use for creating spatial markers within an arena.

    .. image:: _static/img/bucket_img_into_grid_points.png
       :width: 500
       :align: center

    :param int point_distance: Distance between adjacent points in millimeters.
    :param float px_per_mm: Pixels per millimeter conversion factor.
    :param Tuple[int, int] img_size: Size of the image in pixels (width, height).
    :param Optional[bool] border_sites: If True, includes points on the border of the image. Default is True.
    :returns Dict[Tuple[int, int], Point]: Dictionary where keys are (row, column) indices of the point, and values are Shapely Point objects.

    :example:
    >>> point_grid(point_distance=20, px_per_mm=4, img_size=img.shape, border_sites=False)
    """

    point_distance = int(point_distance * px_per_mm)
    v_bin_cnt, h_bin_cnt = divmod(img_size[0], point_distance), divmod(img_size[1], point_distance)
    if h_bin_cnt[1] != 0: h_bin_cnt = (h_bin_cnt[0] + 1, h_bin_cnt[1])
    if v_bin_cnt[1] != 0: v_bin_cnt = (v_bin_cnt[0] + 1, v_bin_cnt[1])

    points = {}
    for h_cnt, i in enumerate(range(h_bin_cnt[0]+1)):
        for v_cnt, j in enumerate(range(v_bin_cnt[0]+1)):
            x, y = i * point_distance, j * point_distance
            x, y = min(x, img_size[1]), min(y, img_size[0])
            if not border_sites and ((x == 0) or (y == 0) or (y == img_size[0]) or (x == img_size[1])):
                continue
            else:
                point = Point(x, y)
                if point not in points.values():
                    points[(h_cnt, v_cnt)] = Point(x, y)
    return points


def tesselate_grid(points: dict):
    point_array = np.full((len(list(points.values())), 2), np.nan)
    for k, v in enumerate(points.values()):
        point_array[k] = np.array(v)
    tri = triangulate(MultiPoint(point_array.astype(np.int64)))
    return tri

    # triangles = Delaunay(point_array, furthest_site=True, incremental=True)
    # for i in triangles.simplices:
    #     polygons.append(Polygon(point_array[i]))
    # return polygons
    # for i in triangles.simplices.shape[0]:




    #
    # print(tri.simplices)
    # # plt.triplot(points[:, 0], points[:, 1], tri.simplices)
    # # plt.plot(points[:, 0], points[:, 1], 'o')
    # # plt.show()





    # if not border_sites:
    #     start_pos_x, start_pos_y = point_distance, point_distance
    #     end_pos_x, end_pos_y = img_size[1] - point_distance, img_size[0] - point_distance
    # else:
    #     start_pos_x, start_pos_y = 0, 0
    #     end_pos_x, end_pos_y = img_size[1], img_size[0]

    # points = {}
    # for h_cnt, i in enumerate(range(start_pos_x, end_pos_x, point_distance)):
    #     for v_cnt, j in enumerate(range(start_pos_y, end_pos_y, point_distance)):
    #         points[v_cnt, h_cnt] = Point(i, j)
    # return points



img = cv2.imread('/Users/simon/Desktop/grd_ex_2.png')
point_grid = bucket_img_into_grid_points(point_distance=20, px_per_mm=4, img_size=img.shape, border_sites=False)
polygons = tesselate_grid(points=point_grid)



# #
hue_values = np.linspace(150, 220, len(list(point_grid.values())), dtype=np.uint8)
colors_rgb = np.stack([hue_values, np.full_like(hue_values, 254), np.full_like(hue_values, 254)], axis=-1).astype(np.int)
colors_bgr = colors_rgb[..., ::-1]


for cnt, i in enumerate(polygons):
    coords = np.array(i.exterior.coords).astype(np.int)
    b, g, r = np.random.randint(0, 255, (1))[0], np.random.randint(0, 255, (1))[0], np.random.randint(0, 255, (1))[0]
    cv2.polylines(img, [coords], True, (int(b), int(g), int(r)), 4)
#
# for cnt, i in enumerate(point_grid.values()):
#     b, g, r = np.random.randint(0, 255, (1))[0], np.random.randint(0, 255, (1))[0], np.random.randint(100, 255, (1))[0]
#     center = tuple(np.array(i).astype(int))
#     cv2.circle(img, center, 9, (int(b), int(g), int(r)), -1)
cv2.imshow('img', img)
cv2.waitKey()
