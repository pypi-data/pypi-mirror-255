__author__ = "Simon Nilsson"

import numpy as np
import os
import cv2
from typing import List

from simba.utils.enums import Formats, TagNames
from simba.utils.printing import stdout_success, SimbaTimer, log_event
from simba.mixins.config_reader import ConfigReader
from simba.mixins.plotting_mixin import PlottingMixin
from simba.mixins.geometry_mixin import GeometryMixin
from simba.utils.read_write import get_fn_ext, read_df, remove_a_folder
from simba.utils.errors import NoSpecifiedOutputError

class HeatMapperClfSingleCore(ConfigReader, PlottingMixin):
    """
    Create heatmaps representing the locations of the classified behavior.

    .. note::
       `GitHub visualizations tutorial <https://github.com/sgoldenlab/simba/blob/master/docs/tutorial.md#step-11-visualizations>`__.
       For improved run-time, see :meth:`simba.heat_mapper_clf_mp.HeatMapperClfMultiprocess` for multiprocess class.

    .. image:: _static/img/heatmap.png
       :width: 300
       :align: center

    :param str config_path: path to SimBA project config file in Configparser format
    :param bool final_img_setting: If True, then create a single image representing the last frame of the input video
    :param bool video_setting: If True, then create a video of heatmaps.
    :param bool frame_setting: If True, then create individual heatmap frames.
    :param str bodypart: The name of the body-part used to infer the location of the classified behavior
    :param str clf_name: The name of the classified behavior.
    :param dict style_attr: Dictionary holding hearmap attributes. E.g., {'palette': 'jet', 'shading': 'gouraud', 'bin_size': 75, 'max_scale': 'auto'}
                            - max_scale: The max value in the heatmap in seconds. E.g., with a value of `10`, if the classified behavior has occured >= 10 within a rectangular bins, it will be filled with the same color.
                            - pallette. Eg. 'jet', 'magma', 'inferno','plasma', 'viridis', 'gnuplot2'
                            - bin_size: The rectangular size of each heatmap location in millimeters. For example, `50` will divide the video into 5 centimeter rectangular spatial bins.
                            - shading: 'gouraud' vs. 'flat'.

    :example:
    >>> heat_mapper_clf = HeatMapperClfSingleCore(config_path='MyConfigPath', final_img_setting=False, video_setting=True, frame_setting=False, bin_size=50, palette='jet', bodypart='Nose_1', clf_name='Attack', max_scale=20)
    >>> heat_mapper_clf.run()
    """

    def __init__(self,
                 config_path: str,
                 final_img_setting: bool,
                 video_setting: bool,
                 frame_setting: bool,
                 bodypart: str,
                 clf_name: str,
                 files_found: List[str],
                 style_attr: dict
                 ):

        ConfigReader.__init__(self, config_path=config_path)
        PlottingMixin.__init__(self)
        log_event(logger_name=str(__class__.__name__), log_type=TagNames.CLASS_INIT.value, msg=self.create_log_msg_from_init_args(locals=locals()))
        if (not frame_setting) and (not video_setting) and (not final_img_setting):
            raise NoSpecifiedOutputError(msg='Please choose to select either heatmap videos, frames, and/or final image.', source=self.__class__.__name__)
        self.frame_setting, self.video_setting = frame_setting, video_setting
        self.final_img_setting, self.bp = final_img_setting, bodypart
        self.bin_size, self.max_scale, self.palette, self.shading = style_attr['bin_size'], style_attr['max_scale'], style_attr['palette'], style_attr['shading']
        self.clf_name, self.files_found = clf_name, files_found
        if not os.path.exists(self.heatmap_clf_location_dir): os.makedirs(self.heatmap_clf_location_dir)
        self.bp_lst = [f'{self.bp}_x', f'{self.bp}_y']
        print(f'Processing {len(self.files_found)} video(s)...')

    def run(self):
        for file_cnt, file_path in enumerate(self.files_found):
            video_timer = SimbaTimer(start=True)
            _, self.video_name, _ = get_fn_ext(file_path)
            self.video_info, self.px_per_mm, self.fps = self.read_video_info(video_name=self.video_name)
            self.width, self.height = int(self.video_info['Resolution_width'].values[0]), int(self.video_info['Resolution_height'].values[0])
            if self.frame_setting:
                self.save_video_folder = os.path.join(self.heatmap_clf_location_dir, self.video_name)
                if os.path.exists(self.save_video_folder):
                    remove_a_folder(folder_dir=self.save_video_folder)
                if not os.path.exists(self.save_video_folder):
                    os.makedirs(self.save_video_folder)
            if self.video_setting:
                self.video_save_path = os.path.join(self.heatmap_clf_location_dir, f'{self.video_name}.mp4')
                fourcc = cv2.VideoWriter_fourcc(*Formats.MP4_CODEC.value)
                self.writer = cv2.VideoWriter(self.video_save_path, fourcc, int(self.fps), (int(self.width), int(self.height)))

            self.data_df = read_df(file_path=file_path, file_type=self.file_type, usecols=self.bp_lst + [self.clf_name])
            geometry_array, aspect_ratio = GeometryMixin.bucket_img_into_grid_square(bucket_size_mm=self.bin_size, img_size=(self.height, self.width), px_per_mm=self.px_per_mm)
            clf_array = GeometryMixin().cumsum_bool_geometries(data=self.data_df[self.bp_lst].values, geometries=geometry_array, bool_data=self.data_df[self.clf_name].values)
            if self.max_scale == 'auto':
                self.max_scale = np.round(np.max(np.max(clf_array[-1], axis=0)), 3)
                if self.max_scale == 0: self.max_scale = 1
            if self.final_img_setting:
                self.make_clf_heatmap_plot(frm_data=clf_array[-1, :, :],
                                           max_scale=self.max_scale,
                                           palette=self.palette,
                                           aspect_ratio=aspect_ratio,
                                           file_name=os.path.join(self.heatmap_clf_location_dir, self.video_name + '_final_frm.png'),
                                           shading=self.shading,
                                           clf_name=self.clf_name,
                                           img_size=(self.width, self.height),
                                           final_img=True)

            if self.video_setting or self.frame_setting:
                for frm_cnt, cumulative_frm_idx in enumerate(range(clf_array.shape[0])):
                    frm_data = clf_array[cumulative_frm_idx,:,:]
                    heatmap = self.make_clf_heatmap_plot(frm_data=frm_data,
                                                         max_scale=self.max_scale,
                                                         palette=self.palette,
                                                         aspect_ratio=aspect_ratio,
                                                         file_name=None,
                                                         shading=self.shading,
                                                         clf_name=self.clf_name,
                                                         img_size=(self.width, self.height),
                                                         final_img=False)
                    if self.video_setting:
                        self.writer.write(heatmap)
                    if self.frame_setting:
                        frame_save_path = os.path.join(self.save_video_folder, f'{frm_cnt}.png')
                        cv2.imwrite(frame_save_path, heatmap)
                    print(f'Created heatmap frame: {frm_cnt + 1} / {len(self.data_df)}. Video: {self.video_name} ({file_cnt + 1}/{len(self.files_found)})')
                if self.video_setting:
                    self.writer.release()
                video_timer.stop_timer()
                print(f'Heatmap plot for video {self.video_name} saved (elapsed time: {video_timer.elapsed_time_str}s)... ')
        self.timer.stop_timer()
        stdout_success(msg='All heatmap visualizations created in project_folder/frames/output/heatmaps_classifier_locations directory', elapsed_time=self.timer.elapsed_time_str, source=self.__class__.__name__)

# test = HeatMapperClfSingleCore(config_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini',
#                      style_attr = {'palette': 'jet', 'shading': 'gouraud', 'bin_size': 100, 'max_scale': 'auto'},
#                      final_img_setting=True,
#                      video_setting=True,
#                      frame_setting=False,
#                      bodypart='Nose_1',
#                      clf_name='Attack',
#                      files_found=['/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/csv/machine_results/Together_1.csv'])
# test.run()

