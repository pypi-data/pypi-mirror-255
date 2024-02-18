import os
import numpy as np
from typing import Union, Optional
from simba.mixins.geometry_mixin import GeometryMixin
from simba.mixins.image_mixin import ImageMixin
from simba.utils.enums import Defaults
from simba.utils.read_write import find_core_cnt, read_frm_of_video
import pandas as pd
try:
    from typing import Literal
except:
    from typing_extensions import Literal
import multiprocessing
import functools
import cv2
import platform



def _multifrm_geometry_histocomparison_helper(frm_index: np.ndarray,
                                              data: np.ndarray,
                                              video_path: cv2.VideoCapture,
                                              shape_type: Literal['rectangle', 'circle'],
                                              pixels_per_mm: int,
                                              parallel_offset: int):

    cap = cv2.VideoCapture(video_path)
    results = []
    for frm_range_idx in range(frm_index.shape[0]):
        frm_range = frm_index[frm_range_idx]
        print(f'Analyzing frame {frm_range[1]}...')
        img_1 = read_frm_of_video(video_path=cap, frame_index=frm_range[0])
        img_2 = read_frm_of_video(video_path=cap, frame_index=frm_range[1])
        loc = data[frm_range[0]:frm_range[1], :]
        if shape_type == 'circle':
            shape_1 = GeometryMixin().bodyparts_to_circle(data=loc[0], pixels_per_mm=pixels_per_mm, parallel_offset=parallel_offset)
            shape_2 = GeometryMixin().bodyparts_to_circle(data=loc[1], pixels_per_mm=pixels_per_mm, parallel_offset=parallel_offset)
        else:
            loc = loc.reshape(2, int(loc.shape[1] / 2), 2)
            shape_1 = GeometryMixin().bodyparts_to_polygon(data=loc[0], parallel_offset=parallel_offset, pixels_per_mm=pixels_per_mm)
            shape_2 = GeometryMixin().bodyparts_to_polygon(data=loc[1], parallel_offset=parallel_offset, pixels_per_mm=pixels_per_mm)
        intersection_shape = shape_1.intersection(shape_2)
        img_1 = ImageMixin().slice_shapes_in_img(img=img_1, geometries=[intersection_shape])[0].astype(np.uint8)
        img_2 = ImageMixin().slice_shapes_in_img(img=img_2, geometries=[intersection_shape])[0].astype(np.uint8)
        results.append(ImageMixin().get_contourmatch(img_1=img_1, img_2=img_2, canny=True))

    return results

def multifrm_geometry_histocomparison(video_path: Union[str, os.PathLike],
                                      data: np.ndarray,
                                      shape_type: Literal['rectangle', 'circle'],
                                      lag: Optional[int] = 2,
                                      core_cnt: Optional[int] = -1,
                                      pixels_per_mm: int = 1,
                                      parallel_offset: int = 1) -> np.ndarray:
    """
    Perform geometry histocomparison on multiple video frames using multiprocessing.

    :param Union[str, os.PathLike] video_path: Path to the video file.
    :param np.ndarray data: Input data, typically containing coordinates of one or several body-parts.
    :param Literal['rectangle', 'circle'] shape_type: Type of shape for comparison.
    :param Optional[int] lag: Number of frames to lag between comparisons. Default is 2.
    :param Optional[int] core_cnt: Number of CPU cores to use for parallel processing. Default is -1 which is all available cores.
    :param Optional[int] pixels_per_mm: Pixels per millimeter for conversion. Default is 1.
    :param Optional[int] parallel_offset: Size of the geometry ROI in millimeters. Default 1.
    :returns np.ndarray: The difference between the successive geometry histograms.

    :example:
    >>> data = pd.read_csv('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv', nrows=2100, usecols=['Nose_x', 'Nose_y']).fillna(-1).values.astype(np.int64)
    >>> results = multifrm_geometry_histocomparison(video_path='/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1.mp4', data= data, shape_type='circle', pixels_per_mm=1, parallel_offset=100)
    >>> data = pd.read_csv('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_2.csv', nrows=2100, usecols=['Nose_x', 'Nose_y', 'Tail_base_x' , 'Tail_base_y', 'Center_x' , 'Center_y']).fillna(-1).values.astype(np.int64)
    >>> results = multifrm_geometry_histocomparison(video_path='/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1.mp4', data= data, shape_type='rectangle', pixels_per_mm=1, parallel_offset=1)
    """

    #if platform.system() == "Darwin": multiprocessing.set_start_method('spawn', force=True)
    split_frm_idx = np.full((data.shape[0]-(lag-1), 2), -1)
    for cnt, i in enumerate(range(lag, data.shape[0]+1, 1)): split_frm_idx[cnt] = [i-2, i]
    if core_cnt == -1: core_cnt = find_core_cnt()[0]
    chunk_size = len(split_frm_idx) // core_cnt
    remainder =  len(split_frm_idx) % core_cnt
    split_frm_idx = [split_frm_idx[i * chunk_size + min(i, remainder):(i + 1) * chunk_size + min(i + 1, remainder)] for i in range(core_cnt)]
    results = [[0] * lag]
    with multiprocessing.Pool(core_cnt, maxtasksperchild=Defaults.LARGE_MAX_TASK_PER_CHILD.value) as pool:
        constants = functools.partial(_multifrm_geometry_histocomparison_helper,
                                      video_path=video_path,
                                      data=data,
                                      shape_type=shape_type,
                                      pixels_per_mm=pixels_per_mm,
                                      parallel_offset=parallel_offset)
        for cnt, result in enumerate(pool.imap(constants, split_frm_idx, chunksize=1)):
            results.append(result)

    return [item for sublist in results for item in sublist]

data = pd.read_csv('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_2.csv', nrows=2100, usecols=['Nose_x', 'Nose_y', 'Tail_base_x' , 'Tail_base_y', 'Center_x' , 'Center_y']).fillna(-1).values.astype(np.int64)
results = multifrm_geometry_histocomparison(video_path='/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1.mp4', data= data, shape_type='rectangle', pixels_per_mm=1, parallel_offset=1)
out = pd.DataFrame(results)
out.to_csv('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/logs/measures/contour-comparison.csv')
