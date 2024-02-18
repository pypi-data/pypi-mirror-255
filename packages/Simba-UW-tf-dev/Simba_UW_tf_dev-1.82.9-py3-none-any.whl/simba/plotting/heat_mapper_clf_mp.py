__author__ = "Simon Nilsson"

import pandas as pd
import numpy as np
import os
import cv2
from numba import jit, prange
import multiprocessing
import functools
import platform
from typing import Optional

import simba.mixins.plotting_mixin
from simba.utils.enums import Formats, TagNames, Defaults
from simba.mixins.config_reader import ConfigReader
from simba.mixins.geometry_mixin import GeometryMixin
from simba.mixins.plotting_mixin import PlottingMixin
from simba.utils.errors import NoSpecifiedOutputError
from simba.utils.printing import stdout_success, SimbaTimer, log_event
from simba.utils.read_write import get_fn_ext, remove_a_folder, concatenate_videos_in_folder, read_df

def _heatmap_multiprocessor(data: np.array,
                            video_setting: bool,
                            frame_setting: bool,
                            video_temp_dir: str,
                            video_name: str,
                            frame_dir: str,
                            fps: int,
                            style_attr: dict,
                            max_scale: float,
                            clf_name:str,
                            aspect_ratio: float,
                            size: tuple,
                            make_clf_heatmap_plot: simba.mixins.plotting_mixin.PlottingMixin.make_location_heatmap_plot):

    video_writer, group = None, int(data[0][0][1])
    for img_cnt, i in enumerate(range(data.shape[0])):
        frame_id = int(data[i, 0, 0])
        frm_data = data[i, :, 2:]
        img = make_clf_heatmap_plot(frm_data=frm_data,
                                    max_scale=max_scale,
                                    palette=style_attr['palette'],
                                    aspect_ratio=aspect_ratio,
                                    shading=style_attr['shading'],
                                    clf_name=clf_name,
                                    img_size=size,
                                    final_img=False)
        print('Heatmap frame created: {}, Video: {}, Processing core: {}'.format(str(frame_id+1), video_name, str(group+1)))
        if img_cnt == 0 and video_setting:
            fourcc = cv2.VideoWriter_fourcc(*Formats.MP4_CODEC.value)
            video_save_path = os.path.join(video_temp_dir, '{}.mp4'.format(str(group)))
            video_writer = cv2.VideoWriter(video_save_path, fourcc, fps, (int(img.shape[1]), int(img.shape[0])))

        if video_setting:
            video_writer.write(img)

        if frame_setting:
            file_path = os.path.join(frame_dir, '{}.png'.format(frame_id))
            cv2.imwrite(file_path, img)

    if video_setting:
        video_writer.release()

    return group

class HeatMapperClfMultiprocess(ConfigReader, PlottingMixin):

    """
    Create heatmaps representing the locations of the classified behavior.

    .. note::
       `GitHub visualizations tutorial <https://github.com/sgoldenlab/simba/blob/master/docs/tutorial.md#step-11-visualizations>`__.

        .. image:: _static/img/heatmap.png
           :width: 300
           :align: center

    :param str config_path: path to SimBA project config file in Configparser format
    :param bool final_img_setting: If True, then create a single image representing the last frame of the input video
    :param bool video_setting: If True, then create a video of heatmaps.
    :param bool frame_setting: If True, then create individual heatmap frames.
    :param str bodypart: The name of the body-part used to infer the location of the classified behavior
    :param str clf_name: The name of the classified behavior.
    :param int core_cnt: Number of cores to use.
    :param dict style_attr: Dictionary holding hearmap attributes. E.g., {'palette': 'jet', 'shading': 'gouraud', 'bin_size': 75, 'max_scale': 'auto'}
                            - max_scale: The max value in the heatmap in seconds. E.g., with a value of `10`, if the classified behavior has occured >= 10 within a rectangular bins, it will be filled with the same color.
                            - pallette. Eg. 'jet', 'magma', 'inferno','plasma', 'viridis', 'gnuplot2'
                            - bin_size: The rectangular size of each heatmap location in millimeters. For example, `50` will divide the video into 5 centimeter rectangular spatial bins.
                            - shading: 'gouraud' vs. 'flat'.

    :examples:
    >>> heat_mapper_clf = HeatMapperClfMultiprocess(config_path='MyConfigPath', final_img_setting=False, video_setting=True, frame_setting=False, bin_size=50, palette='jet', bodypart='Nose_1', clf_name='Attack', max_scale=20)
    >>> heat_mapper_clf.run()
    """

    def __init__(self,
                 config_path: str,
                 final_img_setting: bool,
                 video_setting: bool,
                 frame_setting: bool,
                 bodypart: str,
                 clf_name: str,
                 files_found: list,
                 style_attr: dict,
                 core_cnt: int
                 ):

        ConfigReader.__init__(self, config_path=config_path, create_logger=False)
        PlottingMixin.__init__(self)
        log_event(logger_name=str(__class__.__name__), log_type=TagNames.CLASS_INIT.value, msg=self.create_log_msg_from_init_args(locals=locals()))
        if platform.system() == "Darwin":
            multiprocessing.set_start_method('spawn', force=True)
        if (not frame_setting) and (not video_setting) and (not final_img_setting):
            raise NoSpecifiedOutputError(msg='Please choose to select either heatmap videos, frames, and/or final image.', source=self.__class__.__name__)
        self.frame_setting, self.video_setting = frame_setting, video_setting
        self.final_img_setting, self.bp = final_img_setting, bodypart
        self.style_attr = style_attr
        self.bin_size, self.max_scale, self.palette, self.shading, self.core_cnt = style_attr['bin_size'], style_attr['max_scale'], style_attr['palette'], style_attr['shading'], core_cnt
        self.clf_name, self.files_found = clf_name, files_found
        if not os.path.exists(self.heatmap_clf_location_dir): os.makedirs(self.heatmap_clf_location_dir)
        self.bp_lst = [self.bp + '_x', self.bp + '_y']
        print('Processing {} video(s)...'.format(str(len(self.files_found))))

    @staticmethod
    @jit(nopython=True)
    def __insert_group_idx_column(data: np.array,
                                  group: int,
                                  last_frm_idx: int):


        results = np.full((data.shape[0], data.shape[1], data.shape[2]+2), np.nan)
        group_col = np.full((data.shape[1], 1), group)
        for frm_idx in prange(data.shape[0]):
            h_stack = np.hstack((group_col, data[frm_idx]))
            frm_col = np.full((h_stack.shape[0], 1), frm_idx+last_frm_idx)
            results[frm_idx] = np.hstack((frm_col, h_stack))

        return results

    def run(self):
        for file_cnt, file_path in enumerate(self.files_found):
            video_timer = SimbaTimer()
            video_timer.start_timer()
            _, self.video_name, _ = get_fn_ext(file_path)
            self.video_info, self.px_per_mm, self.fps = self.read_video_info(video_name=self.video_name)
            self.width, self.height = int(self.video_info['Resolution_width'].values[0]), int(self.video_info['Resolution_height'].values[0])
            self.save_frame_folder_dir = os.path.join(self.heatmap_clf_location_dir, self.video_name + '_' + self.clf_name)
            self.video_folder = os.path.join(self.heatmap_clf_location_dir, self.video_name + '_' + self.clf_name)
            self.temp_folder = os.path.join(self.heatmap_clf_location_dir, self.video_name + '_' + self.clf_name, 'temp')
            if self.frame_setting:
                if os.path.exists(self.save_frame_folder_dir):
                    remove_a_folder(folder_dir=self.save_frame_folder_dir)
                if not os.path.exists(self.save_frame_folder_dir): os.makedirs(self.save_frame_folder_dir)
            if self.video_setting:
                if os.path.exists(self.temp_folder):
                    remove_a_folder(folder_dir=self.temp_folder)
                    remove_a_folder(folder_dir=self.video_folder)
                os.makedirs(self.temp_folder)
                self.save_video_path = os.path.join(self.heatmap_clf_location_dir, '{}_{}.mp4'.format(self.video_name, self.clf_name))

            self.data_df = read_df(file_path=file_path, file_type=self.file_type, usecols=self.bp_lst + [self.clf_name])
            geometry_array, aspect_ratio = GeometryMixin().bucket_img_into_grid_square(bucket_size_mm=self.bin_size, img_size=(self.width, self.height), px_per_mm=self.px_per_mm)
            clf_array = GeometryMixin().cumsum_bool_geometries(data=self.data_df[self.bp_lst].values, geometries=geometry_array, bool_data=self.data_df[self.clf_name].values)

            #print(clf_array)
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
                frame_arrays = np.array_split(clf_array, self.core_cnt)
                last_frm_idx = 0
                for frm_group in range(len(frame_arrays)):
                    split_arr = frame_arrays[frm_group]
                    frame_arrays[frm_group] = self.__insert_group_idx_column(data=split_arr, group=frm_group, last_frm_idx=last_frm_idx)
                    last_frm_idx = np.max(frame_arrays[frm_group].reshape((frame_arrays[frm_group].shape[0], -1)))
                frm_per_core = frame_arrays[0].shape[0]
                print(f'Creating heatmaps, multiprocessing (chunksize: {self.multiprocess_chunksize}, cores: {(self.core_cnt)})...')
                with multiprocessing.Pool(self.core_cnt, maxtasksperchild=Defaults.LARGE_MAX_TASK_PER_CHILD.value) as pool:
                    constants = functools.partial(_heatmap_multiprocessor,
                                                  video_setting=self.video_setting,
                                                  frame_setting=self.frame_setting,
                                                  style_attr=self.style_attr,
                                                  fps=self.fps,
                                                  video_temp_dir=self.temp_folder,
                                                  frame_dir=self.save_frame_folder_dir,
                                                  max_scale=self.max_scale,
                                                  aspect_ratio=aspect_ratio,
                                                  clf_name=self.clf_name,
                                                  size=(self.width, self.height),
                                                  video_name=self.video_name,
                                                  make_clf_heatmap_plot=PlottingMixin.make_clf_heatmap_plot)
        #
                    for cnt, result in enumerate(pool.imap(constants, frame_arrays, chunksize=self.multiprocess_chunksize)):
                        print(f'Image {frm_per_core * (result+1)}/{len(self.data_df)}, Video {file_cnt + 1}/{len(self.files_found)}...')
                    pool.join()
                    pool.terminate()

                if self.video_setting:
                    print('Joining {} multiprocessed video...'.format(self.video_name))
                    concatenate_videos_in_folder(in_folder=self.temp_folder, save_path=self.save_video_path)

                video_timer.stop_timer()
                print('Heatmap video {} complete (elapsed time: {}s) ...'.format(self.video_name, video_timer.elapsed_time_str))

        self.timer.stop_timer()
        stdout_success(msg=f'Heatmap visualization(s) for {len(self.files_found)} videos created in {self.heatmap_clf_location_dir} directory', elapsed_time=self.timer.elapsed_time_str, source=self.__class__.__name__)

# test = HeatMapperClfMultiprocess(config_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini',
#                                  style_attr = {'palette': 'magma', 'shading': 'gouraud', 'bin_size': 100, 'max_scale': 'auto'},
#                                  final_img_setting=False,
#                                  video_setting=True,
#                                  frame_setting=False,
#                                  bodypart='Nose_1',
#                                  clf_name='Attack',
#                                  core_cnt=5,
#                                  files_found=['/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/csv/machine_results/Together_1.csv'])
# test.run()

