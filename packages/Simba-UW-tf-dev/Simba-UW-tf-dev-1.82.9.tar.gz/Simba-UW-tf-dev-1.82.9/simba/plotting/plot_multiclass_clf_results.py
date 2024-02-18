__author__ = "Simon Nilsson"

import os, glob
from copy import deepcopy
import cv2
import numpy as np
from PIL import Image
from typing import Union, Dict, Optional, List

from simba.mixins.config_reader import ConfigReader
from simba.mixins.train_model_mixin import TrainModelMixin
from simba.mixins.plotting_mixin import PlottingMixin
from simba.utils.errors import NoSpecifiedOutputError
from simba.utils.printing import log_event
from simba.utils.enums import Formats, TagNames, TextOptions
from simba.utils.read_write import get_fn_ext, read_df, get_video_meta_data, create_directory
from simba.utils.checks import check_float, check_int
from simba.utils.data import create_color_palette
from simba.utils.warnings import FrameRangeWarning



class PlotMulticlassSklearnResultsSingleCore(ConfigReader, TrainModelMixin, PlottingMixin):

    def __init__(self,
                 config_path: str,
                 video_setting: bool,
                 frame_setting: bool,
                 text_settings: Optional[Union[Dict[str, float], bool]] = False,
                 video_names: List[Union[str, os.PathLike]] = None,
                 rotate: bool = False,
                 pose_threshold: Optional[float] = 0.0,
                 show_pose: bool = True,
                 show_animal_id: bool = True,
                 print_timers: bool = True):

        ConfigReader.__init__(self, config_path=config_path)
        TrainModelMixin.__init__(self)
        PlottingMixin.__init__(self)
        log_event(logger_name=str(__class__.__name__), log_type=TagNames.CLASS_INIT.value, msg=self.create_log_msg_from_init_args(locals=locals()))

        if (not video_setting) and (not frame_setting):
            raise NoSpecifiedOutputError(msg='Please choose to create a video and/or frames. SimBA found that you ticked neither video and/or frames', source=self.__class__.__name__)

        self.video_names, self.print_timers, self.text_settings = video_names, print_timers, text_settings
        self.video_setting, self.frame_setting, self.rotate = video_setting, frame_setting, rotate
        self.show_pose, self.show_animal_id, self.pose_threshold = show_pose, show_animal_id, pose_threshold
        create_directory(path=self.sklearn_plot_dir)
        self.fourcc = cv2.VideoWriter_fourcc(*Formats.MP4_CODEC.value)
        self.clr_lst = create_color_palette(pallete_name='Set1', increments=self.clf_cnt)
        self.model_dict = self.get_model_info(self.config, self.clf_cnt)

    def __get_print_settings(self):
        if self.text_settings is False:
            self.max_dim = max(self.video_meta_data['width'], self.video_meta_data['height'])
            self.circle_scale = int(TextOptions.RADIUS_SCALER.value / (TextOptions.RESOLUTION_SCALER.value / self.max_dim))
            self.font_size = float(TextOptions.FONT_SCALER.value / (TextOptions.RESOLUTION_SCALER.value / self.max_dim))
            self.spacing_scale = int(TextOptions.SPACE_SCALER.value / (TextOptions.RESOLUTION_SCALER.value / self.max_dim))
            self.text_thickness = TextOptions.TEXT_THICKNESS.value
        else:
            check_float(name='ERROR: TEXT SIZE', value=self.text_settings['font_size'])
            check_int(name='ERROR: SPACE SIZE', value=self.text_settings['space_size'])
            check_int(name='ERROR: TEXT THICKNESS', value=self.text_settings['text_thickness'])
            check_int(name='ERROR: CIRCLE SIZE', value=self.text_settings['circle_size'])
            self.font_size = float(self.text_settings['font_size'])
            self.spacing_scale = int(self.text_settings['space_size'])
            self.text_thickness = int(self.text_settings['text_thickness'])
            self.circle_scale = int(self.text_settings['circle_size'])

    def run(self):
        for video_cnt, video_name in enumerate(self.video_names):
            _, self.video_name, _ = get_fn_ext(video_name)
            self.data_path = os.path.join(self.machine_results_dir,f'{self.video_name}.{self.file_type}')
            self.video_settings, _, self.fps = self.read_video_info(video_name=self.video_name)
            self.data_df = read_df(self.data_path, self.file_type).reset_index(drop=True)
            self.video_path = self.find_video_of_file(self.video_dir, self.video_name, raise_error=True)
            self.cap = cv2.VideoCapture(self.video_path)
            self.save_path = os.path.join(self.sklearn_plot_dir, f'{self.video_name}.mp4')
            self.video_meta_data = get_video_meta_data(self.video_path)
            height, width = deepcopy(self.video_meta_data['height']), deepcopy(self.video_meta_data['width'])
            if self.frame_setting:
                self.video_frame_dir = os.path.join(self.sklearn_plot_dir, self.video_name)
                create_directory(path=self.video_frame_dir)
            if self.rotate:
                self.video_meta_data['height'], self.video_meta_data['width'] = width, height
            self.writer = cv2.VideoWriter(self.save_path, self.fourcc, self.fps, (self.video_meta_data['width'], self.video_meta_data['height']))
            self.__get_print_settings()
            if len(self.data_df) != self.video_meta_data['frame_count']:
                FrameRangeWarning(msg=f'The video {self.video_path} contains {self.video_meta_data["frame_count"]} frames, while the data {self.data_path} contains {len(self.data_df)} frames.')

            row_n = 0
            while (self.cap.isOpened()):
                ret, self.frame = self.cap.read()
                if row_n not in self.data_df.index:
                    FrameRangeWarning(msg=f'Video terminated early: no data for frame {row_n} found in file {self.data_path}')
                    break
                if self.show_pose:
                    for animal_name, animal_data in self.animal_bp_dict.items():
                        for bp_no in range(len(animal_data['X_bps'])):
                            bp_clr = animal_data['colors'][bp_no]
                            x_bp, y_bp, p_bp = animal_data['X_bps'][bp_no], animal_data['Y_bps'][bp_no], animal_data['P_bps'][bp_no]
                            bp_cords = self.data_df.loc[row_n, [x_bp, y_bp, p_bp]]
                            if bp_cords[p_bp] > self.pose_threshold:
                                cv2.circle(self.frame, (int(bp_cords[x_bp]), int(bp_cords[y_bp])), 0, bp_clr, self.circle_scale)

                if self.show_animal_id:
                    for animal_name, animal_data in self.animal_bp_dict.items():
                        bp_clr = animal_data['colors'][0]
                        x_bp, y_bp, p_bp = animal_data['X_bps'][0], animal_data['Y_bps'][0], animal_data['P_bps'][0]
                        bp_cords = self.data_df.loc[row_n, [x_bp, y_bp, p_bp]]
                        if bp_cords[p_bp] > self.pose_threshold:
                            cv2.circle(self.frame, (int(bp_cords[x_bp]), int(bp_cords[y_bp])), 0, bp_clr, self.circle_scale)

                if self.rotate:
                    self.frame = PlottingMixin().rotate_img(img=self.frame)

                self.spacer = TextOptions.FIRST_LINE_SPACING.value
                for model_no, model_info in self.model_dict.items():
                    for clf_name in model_info['classifier_map'].values():
                        clf_value = round(float(self.data_df.loc[row_n, [f'Probability_{clf_name}']].values[0]), 2)
                        cv2.putText(self.frame, f'{clf_name}: {round(clf_value, 2)}', (10, (self.video_meta_data['height'] - self.video_meta_data['height']) + self.spacing_scale * self.spacer), self.font, self.font_size, (255, 0, 0), self.text_thickness)
                        self.spacer += 1

                if self.video_setting:
                    self.writer.write(self.frame)

                if self.frame_setting:
                    frame_save_name = os.path.join(self.video_frame_dir, f'{row_n}.png')
                    cv2.imwrite(frame_save_name, self.frame)
                row_n += 1
                print(f'Frame: {row_n} / {self.video_meta_data["frame_count"]}. Video: {self.video_name} ({video_cnt + 1}/{len(self.video_names)})')

            self.cap.release()
            self.writer.release()

# test = PlotMulticlassSklearnResultsSingleCore(config_path='/Users/simon/Desktop/envs/troubleshooting/multilabel/project_folder/project_config.ini',
#                                               frame_setting=False,
#                                               video_setting=True,
#                                               video_names=['01.YC015YC016phase45-sample.csv'],
#                                               rotate=True)
# test.run()
