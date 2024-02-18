import numpy as np
import os
import cv2
from simba.mixins.geometry_mixin import GeometryMixin
from simba.mixins.config_reader import ConfigReader
from simba.utils.read_write import read_df, read_frm_of_video
from simba.mixins.plotting_mixin import PlottingMixin
from simba.mixins.image_mixin import ImageMixin


PROJECT_PATH = r'/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/project_config.ini'
VIDEO_NAME = '2022-06-20_NOB_DOT_4'
BP = 'Nose'
GRID_SIZE = (10, 10)

config = ConfigReader(config_path=PROJECT_PATH, create_logger=False)
video_info, px_per_mm, fps = config.read_video_info(video_name=VIDEO_NAME)
width, height = int(video_info['Resolution_width'].values[0]), int(video_info['Resolution_height'].values[0])
bp = [f'{BP}_x', f'{BP}_y']

data_path = os.path.join(config.outlier_corrected_dir, VIDEO_NAME + f'.{config.file_type}')
data = read_df(file_path=data_path, usecols=bp, file_type=config.file_type)

grid, aspect_ratio = GeometryMixin().bucket_img_into_grid_square(img_size=(width, height), bucket_grid_size=GRID_SIZE, px_per_mm=px_per_mm)

grid = list(grid.values())

video_path = r'/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/2022-06-20_NOB_DOT_4.mp4'
video_frm = read_frm_of_video(video_path=video_path, frame_index=0, opacity=20)
img = GeometryMixin().view_shapes(shapes=grid, bg_img=video_frm)

cv2.imshow('img', img)
cv2.waitKey(0)



#
# time_data = GeometryMixin().cumsum_coord_geometries(data=data.values, geometries=grid, fps=fps)
#
img = PlottingMixin().make_location_heatmap_plot(frm_data=time_data[-1],
                                                 max_scale=np.max(time_data[-1]),
                                                 palette='jet',
                                                 shading='gouraud',
                                                 img_size=(width, height),
                                                 aspect_ratio=aspect_ratio)
#
# cv2.imwrite('img', '')