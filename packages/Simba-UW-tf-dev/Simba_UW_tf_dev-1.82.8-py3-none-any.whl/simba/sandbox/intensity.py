import os

import numpy as np
import pandas as pd
import cv2
from simba.utils.enums import Keys
import ast
from simba.utils.checks import check_file_exist_and_readable
from shapely.geometry import Polygon
from typing import Union, List, Tuple, Optional
try:
    from typing import Literal
except:
    from typing_extensions import Literal
from simba.utils.checks import check_instance
from simba.mixins.image_mixin import ImageMixin
from simba.mixins.geometry_mixin import GeometryMixin

def get_geometry_brightness_intensity(img: Union[np.ndarray, Tuple[cv2.VideoCapture, int]],
                                      geometries: List[Union[np.ndarray, Polygon]],
                                      ignore_black: Optional[bool] = True) -> np.ndarray:
    """
    Calculate the average brightness intensity within a geometry region-of-interest of an image.

    E.g., can be used with hardcoded thresholds or model kmeans in `simba.mixins.statistics_mixin.Statistics.kmeans_1d` to detect if a light source is ON or OFF state.

    .. image:: _static/img/get_geometry_brightness_intensity.png
       :width: 500
       :align: center

    :param np.ndarray img: Either an image in numpy array format OR a tuple with cv2.VideoCapture object and the frame index.
    :param List[Union[Polygon, np.ndarray]] geometries: A list of shapes either as vertices in a numpy array, or as shapely Polygons.
    :param Optional[bool] ignore_black: If non-rectangular geometries, then pixels that don't belong to the geometry are masked in black. If True, then these pixels will be ignored when computing averages.

    :example:
    >>> img = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1_frames/1.png').astype(np.uint8)
    >>> data_path = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv'
    >>> data = pd.read_csv(data_path, usecols=['Nose_x', 'Nose_y']).sample(n=3).fillna(1).values.astype(np.int64)
    >>> geometries = []
    >>> for frm_data in data: geometries.append(GeometryMixin().bodyparts_to_circle(frm_data, 100))
    >>> get_geometry_brightness_intensity(img=img, geometries=geometries, ignore_black=False)
    >>> [125.0, 113.0, 118.0]
    """

    check_instance(source=f'{get_geometry_brightness_intensity.__name__} img', instance=img, accepted_types=(tuple, np.ndarray))
    check_instance(source=f'{get_geometry_brightness_intensity.__name__} geometries', instance=geometries, accepted_types=list)
    for geom_cnt, geometry in enumerate(geometries): check_instance(source=f'{get_geometry_brightness_intensity.__name__} geometry {geom_cnt}', instance=geometry, accepted_types=(Polygon, np.ndarray))
    sliced_imgs = ImageMixin().slice_shapes_in_img(img=img, geometries=geometries)
    return ImageMixin().brightness_intensity(imgs=sliced_imgs, ignore_black=ignore_black)

#
#
# img = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1_frames/1.png').astype(np.uint8)
# data_path = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv'
# #data = pd.read_csv(data_path, nrows=5, usecols=['Nose_x', 'Nose_y']).fillna(-1).values.astype(np.int64)
# data = pd.read_csv(data_path, usecols=['Nose_x', 'Nose_y']).sample(n=3).fillna(1).values.astype(np.int64)
#
# geometries = []
# for frm_data in data: geometries.append(GeometryMixin().bodyparts_to_circle(frm_data, 100))
# get_geometry_brightness_intensity(img=img, geometries=geometries, ignore_black=False)

#
# roi_df = pd.read_csv('/Users/simon/Desktop/envs/troubleshooting/khan/project_folder/logs/rectangles_20240108130230.csv', index_col=0)
# rectangle_vertices = roi_df[['topLeftX', 'topLeftY', 'Bottom_right_X', 'Bottom_right_Y']].values
# get_geometry_brightness_intensity(img=img, roi_vertices=rectangle_vertices, rois_type='rectangles')
# polygon_vertices = np.array([[[467 , 55],   [492, 177],   [797, 182],   [797, 50]],  [[35, 492],   [238, 502],   [253, 817],   [30, 812]],  [[1234, 497],   [1092, 497],   [1086, 812],   [1239, 827]],  [[452, 1249],   [467, 1046],   [772, 1066], [766, 1249]]])
# get_geometry_brightness_intensity(img=img, roi_vertices=polygon_vertices, rois_type='polygons')
#
#
# img = cv2.VideoCapture('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1.mp4')
#
# get_geometry_brightness_intensity(img)
#
#
#
#
#
#
