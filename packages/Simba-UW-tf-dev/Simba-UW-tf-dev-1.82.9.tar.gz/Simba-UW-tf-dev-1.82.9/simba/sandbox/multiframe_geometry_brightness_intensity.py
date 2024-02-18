import os
from typing import Union, List
from shapely.geometry import MultiPolygon, Polygon
import numpy as np
import pandas as pd
from simba.mixins.geometry_mixin import GeometryMixin
from simba.utils.read_write import get_fn_ext, get_video_meta_data, find_core_cnt
import multiprocessing
from simba.utils.enums import Defaults
import functools


def multiframe_geometry_brightness_intensity(video_path: Union[str, os.PathLike],
                                             shapes: List[Union[MultiPolygon, Polygon]],
                                             core_cnt: int = -1):

    if core_cnt == -1: core_cnt = find_core_cnt()[0]
    video_meta_data = get_video_meta_data(video_path=video_path)
    frm_idx = np.array_split(np.arange(0, video_meta_data['frame_count']+1), core_cnt)
    results = []
    with multiprocessing.Pool(core_cnt, maxtasksperchild=Defaults.LARGE_MAX_TASK_PER_CHILD.value) as pool:
        constants = functools.partial(GeometryMixin.get_geometry_brightness_intensity(),
                                      parallel_offset=parallel_offset,
                                      pixels_per_mm=pixels_per_mm)
        for cnt, mp_return in enumerate(pool.imap(constants, data, chunksize=1)):





    pass



video_path = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1.mp4'
data_path = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv'

data = pd.read_csv(data_path, nrows=1, usecols=['Nose_x', 'Nose_y']).fillna(-1).values.astype(np.int64)
shapes = GeometryMixin().multiframe_bodyparts_to_circle(data, 100)

multiframe_geometry_brightness_intensity(video_path=video_path, shapes=shapes)



#for frm_data in data: polygons.append(GeometryMixin().bodyparts_to_circle(frm_data, 100))



# for file_path in sorted(glob.glob(frm_dir + '/*.png')): imgs.append(cv2.imread(file_path))


