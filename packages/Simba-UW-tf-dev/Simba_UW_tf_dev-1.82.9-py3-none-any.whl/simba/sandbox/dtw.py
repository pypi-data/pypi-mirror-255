from typing import Dict, Tuple
import math
from shapely.geometry import Polygon
from simba.utils.checks import check_int, check_float
import cv2
import numpy as np
from typing import Dict, Tuple
import math
from shapely.geometry import Polygon

def bucket_img_into_grid_hexagon(bucket_size_mm: float,
                                 img_size: Tuple[int, int],
                                  px_per_mm: float) -> Tuple[Dict[Tuple[int, int], Polygon], float]:
    """
    Bucketize an image into hexagons and return a dictionary of polygons representing the hexagon locations.

    .. image:: _static/img/bucket_img_into_grid_hexagon.png
       :width: 500
       :align: center

    :param float bucket_size_mm: The width/height of each hexagon bucket in millimeters.
    :param Tuple[int, int] img_size: Tuple representing the width and height of the image in pixels.
    :param float px_per_mm: Pixels per millimeter conversion factor.
    :return Tuple[Dict[Tuple[int, int], Polygon], float]: First value is a dictionary where keys are (row, column) indices of the bucket, and values are Shapely Polygon objects representing the corresponding hexagon buckets. Second value is the aspect ratio of the hexagonal grid.

    :example:
    >>> polygons, aspect_ratio = bucket_img_into_grid_hexagon(bucket_size_mm=10, img_size=(800, 600), px_per_mm=5.0, add_correction=True)
    """
    check_float(name=f'bucket_img_into_grid_hexagon bucket_size_mm', value=bucket_size_mm)
    check_int(name=f'bucket_img_into_grid_hexagon img_size height', value=img_size[0])
    check_int(name=f'bucket_img_into_grid_hexagon img_size width', value=img_size[1])
    check_float(name=f'bucket_img_into_grid_hexagon px_per_mm', value=px_per_mm)

    sqrt_3 = math.sqrt(3)
    hex_width = 3/2 * bucket_size_mm * px_per_mm
    hex_height = sqrt_3 * bucket_size_mm * px_per_mm

    h_hex_cnt, v_hex_cnt = divmod(img_size[0], int(hex_height)), divmod(img_size[1], int(hex_width))
    if h_hex_cnt[1] != 0: h_hex_cnt = (h_hex_cnt[0] + 1, h_hex_cnt[1])
    if v_hex_cnt[1] != 0: v_hex_cnt = (v_hex_cnt[0] + 1, v_hex_cnt[1])

    polygons = {}
    for i in range(h_hex_cnt[0]):
        for j in range(v_hex_cnt[0] + (i % 2) * 1):
            x = i * 3/2 * hex_width
            y = j * sqrt_3 * hex_height + (i % 2) * sqrt_3 * hex_height / 2
            vertices = []
            for k in range(6):
                angle = (math.pi / 3) * k
                vertices.append((x + hex_width * math.cos(angle), y + hex_height * math.sin(angle)))

            polygons[(i, j)] = Polygon(vertices)

    return polygons, round((v_hex_cnt[0] / h_hex_cnt[0]), 3)

img = cv2.imread('/Users/simon/Desktop/Screenshot 2024-01-21 at 10.15.55 AM.png')
polygons = bucket_img_into_grid_hexagon(bucket_size_mm=8, img_size=(img.shape[1], img.shape[0]) , px_per_mm=5.0)[0]
hue_values = np.linspace(0, 179, len(list(polygons.values())), dtype=np.uint8)
colors_rgb = np.stack([hue_values, np.full_like(hue_values, 254), np.full_like(hue_values, 254)], axis=-1).astype(np.int)
colors_bgr = colors_rgb[..., ::-1]
for cnt, i in enumerate(polygons.values()):
    coords = np.array(i.exterior.coords).astype(np.int)
    b, g, r = np.random.randint(0, 255, (1))[0], np.random.randint(0, 255, (1))[0], np.random.randint(0, 255, (1))[0]
    cv2.polylines(img, [coords], True, (int(b), int(g), int(r)), 4)
cv2.imshow('img', img)
cv2.waitKey()
