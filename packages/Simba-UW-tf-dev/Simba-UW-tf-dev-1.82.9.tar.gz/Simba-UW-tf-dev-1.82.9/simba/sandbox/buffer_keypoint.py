import time
import numpy as np
import pandas as pd
from simba.mixins.geometry_mixin import GeometryMixin
from simba.mixins.image_mixin import ImageMixin
from simba.mixins.config_reader import ConfigReader
import cv2
from typing import Dict, Optional, List, Union
from simba.utils.checks import check_instance, check_int, check_valid_lst, check_valid_array
import multiprocessing
import functools
from simba.utils.enums import Defaults
from simba.utils.read_write import find_core_cnt
from shapely.geometry import Polygon, MultiPolygon



# def sliding_img_emd(data: Union[Dict[int, np.ndarray], List[np.ndarray]],
#                     lag: Optional[int] = 1,
#                     core_cnt: Optional[int] = -1):
#
#     check_instance(source=sliding_img_emd.__name__, instance=data, accepted_types=(dict, list))
#     check_int(name=sliding_img_emd.__name__, value=lag, min_value=1)
#     check_int(name=f'{ImageMixin().slice_shapes_in_imgs.__name__} core count', value=core_cnt, min_value=-1)
#     if core_cnt == -1: core_cnt = find_core_cnt()[0]
#     transposed_list = []
#     for i in range(1, len(data)):
#         if i < lag:
#             transposed_list.append([data[i], data[i]])
#         else:
#             transposed_list.append([data[i], data[i-1]])
#     with multiprocessing.Pool(core_cnt, maxtasksperchild=Defaults.LARGE_MAX_TASK_PER_CHILD.value) as pool:
#         constants = functools.partial(ImageMixin.img_emd,
#                                       img_1=None,
#                                       img_2=None)
#         for cnt, result in enumerate(pool.imap(constants, transposed_list, chunksize=1)):
#             print('s')
#
# def get_intersection(shapes: List[Polygon]) -> Union[Polygon, MultiPolygon]:
#     check_instance(source=get_intersection.__name__, instance=shapes, accepted_types=(list, np.ndarray))
#     if isinstance(shapes, list):
#         check_valid_lst(data=shapes, source=get_intersection.__name__, valid_dtypes=(Polygon,), min_len=2)
#     else:
#         check_valid_array(data=shapes, accepted_shapes=[(2,)], source=get_intersection.__name__)
#     result_shape = shapes[0]
#     for i in range(1, len(shapes)):
#         result_shape = result_shape.intersection(shapes[i])
#
#     return result_shape
#
#
# def multiframe_get_intersection(shapes: List[Polygon],
#                                 core_cnt: Optional[int] = -1,
#                                 lag: Optional[int] = 1) -> Union[Polygon, MultiPolygon]:
#     check_instance(source=get_intersection.__name__, instance=shapes, accepted_types=(list,))
#     check_valid_lst(data=shapes, source=get_intersection.__name__, valid_dtypes=(Polygon,), min_len=2)
#     if core_cnt == -1: core_cnt = find_core_cnt()[0]
#     transposed_shapes, results = np.full((len(shapes), 2), None), []
#     for shape_idx in range(len(shapes)):
#         transposed_shapes[shape_idx][0] = shapes[shape_idx]
#         if shape_idx < lag: transposed_shapes[shape_idx][1] = shapes[shape_idx]
#         else: transposed_shapes[shape_idx][1] = shapes[shape_idx - lag]
#     with multiprocessing.Pool(core_cnt, maxtasksperchild=Defaults.LARGE_MAX_TASK_PER_CHILD.value) as pool:
#         for cnt, result in enumerate(pool.imap(get_intersection, transposed_shapes, chunksize=1)):
#             results.append(result)
#     pool.join(); pool.terminate()
#     return results
#
#

config = ConfigReader(config_path='/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/project_config.ini', create_logger=False)
video_info, px_per_mm, fps = config.read_video_info(video_name='Example_1_clipped')
video_path = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1_clipped.mp4'
DATA_PATH = r'/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1_clipped.csv'
LAG = 1



df = pd.read_csv(DATA_PATH, usecols=['Nose_x', 'Nose_y', 'Tail_base_x', 'Tail_base_y']).fillna(0).values.astype(int)
data = df.reshape(len(df), -1, int(df.shape[1]/2))
geometries, aspect_ratio = GeometryMixin().multiframe_bodyparts_to_line(data=data, buffer=30, px_per_mm=px_per_mm)
geometries = multiframe_get_intersection(shapes=geometries, lag=LAG)




imgs = ImageMixin().slice_shapes_in_imgs(imgs=video_path, shapes=geometries)

cv2.matchShapes(imgs[0], imgs[0], cv2.CONTOURS_MATCH_I1, 0.0)

# t = sliding_img_emd(data=imgs, lag=LAG)

results = GeometryMixin().multifrm_geometry_histocomparison(video_path=video_path, data=df, shape_type='line', lag=2, parallel_offset=10, pixels_per_mm=px_per_mm)



#get_intersection(shapes=geometries[0:2])







#results = GeometryMixin().multifrm_geometry_histocomparison(video_path=video_path, data=df, shape_type='line', lag=2, parallel_offset=10, pixels_per_mm=px_per_mm)


# cv2.imshow('imgs[0]', imgs[1])
# cv2.waitKey(5000)


#
#
# from simba.mixins.geometry_mixin import GeometryMixin
# from simba.mixins.config_reader import ConfigReader
# import cv2
#
# config = ConfigReader(config_path='/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/project_config.ini', create_logger=False)
# video_path = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1.mp4'
# video_info, px_per_mm, fps = config.read_video_info(video_name='Example_1')
# DATA_PATH = r'/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv'
# df = pd.read_csv(DATA_PATH, usecols=['Nose_x', 'Nose_y', 'Tail_base_x', 'Tail_base_y']).fillna(-1).values.astype(int)
# data = df.reshape(len(df), -1, int(df.shape[1]/2))
#
# geometries = GeometryMixin().multiframe_bodyparts_to_line(data=data, buffer=40, px_per_mm=px_per_mm)
# ImageMixin().slice_shapes_in_imgs(imgs=video_path, shapes=geometries)
#
#
#





# data = np.random.randint(0, 100, (10, 2))
# start = time.time()
# bodyparts_to_points(data=data, buffer=10, px_per_mm=4)
# print(time.time() - start)
# start = time.time()
# shapes = multiframe_bodypart_to_point(data=data, buffer=10, px_per_mm=4)
# print(time.time() - start)