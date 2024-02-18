import time
import numpy as np
import pandas as pd
import os
from simba.mixins.geometry_mixin import GeometryMixin
from simba.mixins.config_reader import ConfigReader
import cv2
from simba.utils.read_write import read_df
from simba.mixins.plotting_mixin import PlottingMixin
from simba.utils.read_write import read_frm_of_video


PROJECT_PATH = r'/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/project_config.ini'
VIDEO_PATH = r'/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/2022-06-20_NOB_DOT_4.mp4'
VIDEO_NAME = '2022-06-20_NOB_DOT_4'
GRID_SIZE = (20, 20)

config = ConfigReader(config_path=PROJECT_PATH, create_logger=False)
video_info, px_per_mm, fps = config.read_video_info(video_name=VIDEO_NAME)
width, height = int(video_info['Resolution_width'].values[0]), int(video_info['Resolution_height'].values[0])
data_path = os.path.join(config.outlier_corrected_dir, VIDEO_NAME + f'.{config.file_type}')

data = read_df(file_path=data_path, file_type=config.file_type)
bps = [x for x in config.bp_headers if not x.endswith('_p')]
bps = [x for x in bps if not 'Tail_end' in x]
data = data[bps].values.astype(int)

data = data.reshape(len(data), int(data.shape[1] / 2), 2)
shapes = GeometryMixin().multiframe_bodyparts_to_polygon(data=data, parallel_offset=100, pixels_per_mm=4)
img = read_frm_of_video(video_path=VIDEO_PATH, frame_index=4)

grid, aspect_ratio = GeometryMixin().bucket_img_into_grid_square(img_size=(width, height), bucket_grid_size=GRID_SIZE, px_per_mm=px_per_mm)
time_data = cumsum_animal_geometries_grid(data=shapes, grid=grid, fps=fps)



img = PlottingMixin().make_location_heatmap_plot(frm_data=time_data[-1],
                                                 max_scale=np.max(time_data[-1]),
                                                 palette='jet',
                                                 shading='flat',
                                                 img_size=(width, height),
                                                 aspect_ratio=aspect_ratio)

cv2.imshow('img', img)
cv2.waitKey(10000)




#
# def multiframe_bodyparts_to_polygon(self,
#                                     data: np.ndarray,
#                                     video_name: Optional[str] = None,
#                                     animal_name: Optional[str] = None,
#                                     verbose: Optional[bool] = False,
#                                     cap_style: Optional[Literal['round', 'square', 'flat']] = 'round',
#                                     parallel_offset: Optional[int] = 1,
#                                     pixels_per_mm: Optional[float] = None,
#                                     simplify_tolerance: Optional[float] = 2,
#                                     preserve_topology: bool = True,
#                                     core_cnt: int = -1) -> List[Polygon]:
#

