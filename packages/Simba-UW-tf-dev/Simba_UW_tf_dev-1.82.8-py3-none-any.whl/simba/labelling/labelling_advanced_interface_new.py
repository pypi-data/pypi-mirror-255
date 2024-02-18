__author__ = "Simon Nilsson"

import simba
from typing import Optional, Union
from simba.utils.enums import Options, Labelling
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from subprocess import Popen, PIPE
import os
from tabulate import tabulate
import cv2
import pandas as pd

from simba.utils.checks import check_int, check_file_exist_and_readable, check_that_column_exist
from simba.utils.read_write import (read_config_entry,
                                    get_video_meta_data,
                                    get_fn_ext,
                                    read_df,
                                    write_df,
                                    get_all_clf_names)
from simba.utils.enums import Formats, TagNames
from simba.utils.errors import FrameRangeError, AdvancedLabellingError
from simba.utils.printing import stdout_success, log_event
from simba.mixins.config_reader import ConfigReader
from simba.mixins.annotator_mixin import AnnotatorMixin

class AdvancedLabellingInterface(AnnotatorMixin, ConfigReader):
    """
    Launch advanced labelling (annotation) interface in SimBA.

    .. note::
       `Advanced annotation tutorial <https://github.com/sgoldenlab/simba/blob/master/docs/advanced_labelling.md>`__.

    .. image:: _static/img/adv_annotator.png
       :width: 800
       :align: center

    :parameter str config_path: path to SimBA project config file in Configparser format
    :parameter str file_path: Path to video that is to be annotated
    :parameter bool continuing: If True, user is continuing the annotations of a video with started but incomplete annotations.

    Examples
    ----------
    >>> select_labelling_video_advanced(config_path='MyProjectConfig', file_path='MyVideoFilePath', continuing=True)
    """

    def __init__(self,
                 config_path: Union[str, os.PathLike],
                 video_path: Union[str, os.PathLike],
                 continuing: Optional[bool] = False):

        ConfigReader.__init__(self, config_path=config_path)
        log_event(logger_name=str(self.__class__.__name__), log_type=TagNames.CLASS_INIT.value, msg=self.create_log_msg_from_init_args(locals=locals()))
        _, self.video_name, _ = get_fn_ext(filepath=video_path)

        if continuing:
            self.data_path = os.path.join(self.targets_folder, f'{self.video_name}.{self.file_type}')
            check_file_exist_and_readable(file_path=self.data_path)
            self.data_df = read_df(file_path=self.data_path, file_type=self.file_type, usecols=self.clf_names).astype(int)
            for target in self.clf_names:
                check_that_column_exist(df=self.data_df, column_name=target, file_name=self.data_path)
            try:
                self.frm_no = read_config_entry(self.config, 'Last annotated frames', self.video_name.lower(), data_type='int')
            except ValueError:
                pass
        else:
            self.data_path = os.path.join(self.features_dir, f'{self.video_name}.{self.file_type}')
            check_file_exist_and_readable(file_path=self.data_path)
            self.data_df = read_df(file_path=self.data_path, file_type=self.file_type)
            for target in self.clf_names:
                self.data_df[target] = 2
        AnnotatorMixin.__init__(self, config_path=config_path, video_path=video_path, data_path=self.data_path, frame_size=Labelling.VIDEO_FRAME_SIZE.value, title=f'SIMBA ANNOTATION INTERFACE (ADVANCED ANNOTATION) - VIDEO {self.video_name}')
        self.continuing, self.frm_no = continuing, self.min_frm_no
        self.video_frm_label(frm_number=self.min_frm_no)
        self.h_nav_bar(parent=self.main_frm, update_funcs=[self.update_clf_radiobtns], store_funcs=[self.store_annotation], previous_next_clf=True)
        self.advanced_labelling_pane(parent=self.main_frm, data=self.data_df[self.clf_names].to_dict())


        self.main_frm.mainloop()
# #
#
#
#         self.check_frame = Frame(self.main_window, bd=2, width=300, height=500)
#         self.check_frame.grid(row=0, column=1)
#         self.check_behavior_lbl = Label(self.check_frame, text="Check Behavior:")
#         self.check_behavior_lbl.config(font=("Calibri", 16))
#         self.check_behavior_lbl.grid(row=0, column=0, sticky=N)
#         self.behavior_absent_lbl = Label(self.check_frame, text="ABSENT")
#         self.behavior_present_lbl = Label(self.check_frame, text="PRESENT")
#         self.behavior_present_lbl.grid(row=1, column=1, sticky=N)
#         self.behavior_absent_lbl.grid(row=1, column=2, sticky=N)
#
#
#         self.check_present_vars, self.check_present_checkbox = {}, {}
#         self.check_absent_vars, self.check_absent_checkbox = {}, {}
#         for target_cnt, target in enumerate(self.target_lst):
#             self.check_present_vars[target], self.check_absent_vars[target] = IntVar(), IntVar()
#             self.behavior_name_lbl = Label(self.check_frame, text=target)
#             self.check_present_checkbox[target] = Checkbutton(self.check_frame, variable=self.check_present_vars[target], command=lambda: self.save_behavior_in_frm(selection='present'))
#             self.check_absent_checkbox[target] = Checkbutton(self.check_frame, variable=self.check_absent_vars[target], command=lambda: self.save_behavior_in_frm(selection='absent'))
#             self.behavior_name_lbl.grid(row=target_cnt + 2, column=0, sticky=W)
#             self.check_present_checkbox[target].grid(row=target_cnt + 2, column=1, sticky=W)
#             self.check_absent_checkbox[target].grid(row=target_cnt + 2, column=2, sticky=W)
#             if self.data_df_targets[target].iloc[self.current_frm_n.get()] == 1:
#                 self.check_present_vars[target].set(value=1)
#             elif self.data_df_targets[target].iloc[self.current_frm_n.get()] == 0:
#                 self.check_absent_vars[target].set(value=1)
#
#         self.range_on = IntVar(value=0)
#         self.range_frames = Frame(self.main_window)
#         self.range_frames.grid(row=1, column=1, sticky=S)
#         self.select_range = Checkbutton(self.range_frames, text='Frame range', variable=self.range_on)
#         self.select_range.grid(row=0, column=0, sticky=W)
#         self.first_frame = Entry(self.range_frames, width=7)
#         self.first_frame.grid(row=0, column=1, sticky=E)
#         self.to_label = Label(self.range_frames, text=" to ")
#         self.to_label.grid(row=0, column=2, sticky=E)
#         self.last_frame = Entry(self.range_frames, width=7)
#         self.last_frame.grid(row=0, column=3, sticky=E)
#
#         save = Button(self.main_window, text="Save Range", command=lambda: self.save_behavior_in_range())
#         save.grid(row=2, column=1, sticky=N)
#
#         self.generate = Button(self.main_window, text="Save Annotations", command=lambda: self.save_results(), fg='blue')
#         self.generate.config(font=("Calibri", 16))
#         self.generate.grid(row=10, column=1, sticky=N)
#
#         self.video_player_frm = Frame(self.main_window, width=100, height=100)
#         self.video_player_frm.grid(row=0, column=2, sticky=N)
#         self.play_video_btn = Button(self.video_player_frm, text='Open Video', command=self.play_video)
#         self.play_video_btn.grid(sticky=N, pady=10)
#         self.video_key_lbls = Label(self.video_player_frm, text='\n\n  Keyboard shortcuts for video navigation: \n p = Pause/Play'
#                                              '\n\n After pressing pause:'
#                                              '\n o = +2 frames \n e = +10 frames \n w = +1 second'
#                                              '\n\n t = -2 frames \n s = -10 frames \n x = -1 second'
#                                              '\n\n q = Close video window \n\n')
#         self.video_key_lbls.grid(sticky=W)
#         self.update_img_from_video = Button(self.video_player_frm, text='Show current video frame', command=self.update_frame_from_video)
#         self.update_img_from_video.grid(sticky=N)
#         self.bind_shortcut_keys()
#         self.key_presses_lbl = Label(self.video_player_frm,
#                             text='\n\n Keyboard shortcuts for frame navigation: \n Right Arrow = +1 frame'
#                                  '\n Left Arrow = -1 frame'
#                                  '\n Ctrl + s = Save annotations file'
#                                  '\n Ctrl + a = +1 frame and keep choices'
#                                  '\n Ctrl + p = Show annotation statistics'
#                                  '\n Ctrl + l = Last frame'
#                                  '\n Ctrl + o = First frame')
#         self.key_presses_lbl.grid(sticky=S)
#         self.read_frm(frm_number=0)
#         self.main_window.mainloop()
#
#     def bind_shortcut_keys(self):
#         self.main_window.bind('<Control-s>', lambda x: self.save_results())
#         self.main_window.bind('<Control-a>', lambda x: self.advance_frame(new_frm_number= int(self.current_frm_n.get() + 1), keep_prior_img_cb_status=True))
#         self.main_window.bind('<Control-p>', lambda x: self.__print_annotation_statistics())
#         self.main_window.bind('<Right>', lambda x: self.advance_frame(new_frm_number= int(self.current_frm_n.get() + 1)))
#         self.main_window.bind('<Left>', lambda x: self.advance_frame(new_frm_number= int(self.current_frm_n.get() - 1)))
#         self.main_window.bind('<Control-l>', lambda x: self.advance_frame(new_frm_number = self.max_frm_no))
#         self.main_window.bind('<Control-o>', lambda x: self.advance_frame(0))
#
#
#     def find_last_next_annotation(self, forwards: bool, present: bool):
#         if forwards:
#             sliced = self.data_df_targets.loc[self.current_frm_n.get()+1:,].sum(axis=1)
#             if present:
#                 frms = list(sliced.index[sliced >= 1])
#             else:
#                 frms = list(sliced.index[sliced == 0])
#             if len(frms) > 0:
#                 frm = frms[0]
#             else:
#                 raise FrameRangeError('No forwards frames with annotation detected', source=self.__class__.__name__)
#         else:
#             sliced = self.data_df_targets.loc[0:self.current_frm_n.get()-1 , ].sum(axis=1)
#             if present:
#                 frms = list(sliced.index[sliced >= 1])
#             else:
#                 frms = list(sliced.index[sliced == 0])
#             if len(frms) > 0:
#                 frm = frms[-1]
#             else:
#                 raise FrameRangeError('No backwards frames with annotation detected', source=self.__class__.__name__)
#
#         self.advance_frame(new_frm_number=frm, keep_prior_img_cb_status=False)
#
#     def __print_annotation_statistics(self):
#         table_view = [["Video name", self.video_name], ['Video frames', self.video_meta_data['frame_count']]]
#         for target in self.target_lst:
#             present = sum(self.data_df_targets[target][self.data_df_targets[target] == 1])
#             absent = sum(self.data_df_targets[target][self.data_df_targets[target] == 0])
#             table_view.append([target + ' present labels', present])
#             table_view.append([target + ' absent labels', absent])
#             table_view.append([target + ' % present', present / self.video_meta_data['frame_count']])
#             table_view.append([target + ' % absent', absent / self.video_meta_data['frame_count']])
#         headers = ["VARIABLE", "VALUE"]
#         print(tabulate(table_view, headers, tablefmt="github"))
#
#     def play_video(self):
#         p = Popen('python {}'.format(self.play_video_script_path), stdin=PIPE, stdout=PIPE, shell=True)
#         main_project_dir = os.path.dirname(self.config_path)
#         p.stdin.write(bytes(self.video_path, 'utf-8'))
#         p.stdin.close()
#         temp_file = os.path.join(main_project_dir, 'subprocess.txt')
#         with open(temp_file, "w") as text_file: text_file.write(str(p.pid))
#
#     def update_frame_from_video(self):
#         f = open(os.path.join(os.path.dirname(self.config_path), 'labelling_info.txt'), 'r+')
#         os.fsync(f.fileno())
#         vid_frame_no = int(f.readline())
#         self.advance_frame(new_frm_number=vid_frame_no)
#         f.close()
#
#     def read_frm(self, frm_number: int):
#         self.cap.set(1, frm_number)
#         _, self.current_frm_npy = self.cap.read()
#         self.current_frm_npy = cv2.cvtColor(self.current_frm_npy, cv2.COLOR_RGB2BGR)
#         self.current_frm_pil = Image.fromarray(self.current_frm_npy)
#         self.current_frm_pil.thumbnail(self.max_frm_size, Image.ANTIALIAS)
#         self.current_frm_pil = ImageTk.PhotoImage(master=self.main_window, image=self.current_frm_pil)
#         self.video_frame = Label(self.main_window, image=self.current_frm_pil)
#         self.video_frame.image = self.current_frm_pil
#         self.video_frame.grid(row=0, column=0)
#
#
#     def advance_frame(self,
#                       new_frm_number: int,
#                       save_behavior_in_previous_frm: bool=True,
#                       keep_prior_img_cb_status: bool = False):
#         self.check_integrity_of_multiple_classifiers()
#         if new_frm_number > self.max_frm_no:
#             print("FRAME {} CANNOT BE SHOWN - YOU ARE VIEWING THE FINAL FRAME OF THE VIDEO (FRAME NUMBER {})".format(str(new_frm_number), str(self.max_frm_no)))
#             self.current_frm_n = IntVar(value=self.max_frm_no)
#             self.change_frm_box.delete(0, END)
#             self.change_frm_box.insert(0, self.current_frm_n.get())
#         elif new_frm_number < 0:
#             print("FRAME {} CANNOT BE SHOWN - YOU ARE VIEWING THE FIRST FRAME OF THE VIDEO (FRAME NUMBER {})".format(str(new_frm_number), str(self.max_frm_no)))
#             self.current_frm_n = IntVar(value=0)
#             self.change_frm_box.delete(0, END)
#             self.change_frm_box.insert(0, self.current_frm_n.get())
#         elif (new_frm_number != self.current_frm_n.get()) and (not keep_prior_img_cb_status):
#             if save_behavior_in_previous_frm:
#                 self.save_behavior_in_frm()
#             self.create_print_statements()
#             self.current_frm_n = IntVar(value=new_frm_number)
#             for target in self.target_lst:
#                 new_frame_annotation = self.data_df_targets[target].loc[int(self.current_frm_n.get())]
#                 if new_frame_annotation == 0:
#                     self.check_absent_vars[target].set(value=1)
#                     self.check_present_vars[target].set(value=0)
#                 elif new_frame_annotation == 1:
#                     self.check_present_vars[target].set(value=1)
#                     self.check_absent_vars[target].set(value=0)
#                 else:
#                     self.check_present_vars[target].set(value=0)
#                     self.check_absent_vars[target].set(value=0)
#             self.change_frm_box.delete(0, END)
#             self.change_frm_box.insert(0, new_frm_number)
#             self.read_frm(frm_number=int(new_frm_number))
#
#         elif (new_frm_number != self.current_frm_n.get()) and (keep_prior_img_cb_status):
#             self.create_print_statements()
#             if save_behavior_in_previous_frm:
#                 self.save_behavior_in_frm()
#             self.current_frm_n = IntVar(value=new_frm_number)
#             for target in self.target_lst:
#                 new_frame_annotation = self.data_df_targets[target].loc[int(self.current_frm_n.get() -1)]
#                 if new_frame_annotation == 0:
#                     self.check_absent_vars[target].set(value=1)
#                 elif new_frame_annotation == 1:
#                     self.check_present_vars[target].set(value=1)
#             self.change_frm_box.delete(0, END)
#             self.change_frm_box.insert(0, new_frm_number)
#             self.read_frm(frm_number=int(new_frm_number))
#
#     def save_behavior_in_frm(self, selection: str=None):
#         for target in self.target_lst:
#             target_absent_choice, target_present_choice = self.check_absent_vars[target].get(), self.check_present_vars[target].get()
#             if (target_present_choice == 1) & (selection=='present'):
#                 self.data_df_targets[target].loc[int(self.current_frm_n.get())] = 1
#                 self.check_absent_vars[target].set(value=0)
#             elif (target_absent_choice == 1) & (selection=='absent'):
#                 self.data_df_targets[target].loc[int(self.current_frm_n.get())] = 0
#                 self.check_present_vars[target].set(value=0)
#             elif (target_absent_choice == 0) & (target_present_choice == 0):
#                 self.data_df_targets[target].loc[int(self.current_frm_n.get())] = None
#             elif (target_present_choice == 1):
#                 self.data_df_targets[target].loc[int(self.current_frm_n.get())] = 1
#             elif (target_absent_choice == 1):
#                 self.data_df_targets[target].loc[int(self.current_frm_n.get())] = 0
#
#     def save_behavior_in_range(self):
#         self.check_integrity_of_multiple_classifiers()
#         start_frm, end_frm = int(self.first_frame.get()), int(self.last_frame.get())
#         check_int('START FRAME', int(start_frm), max_value=self.max_frm_no, min_value=0)
#         check_int('END FRAME', int(end_frm), max_value=self.max_frm_no, min_value=0)
#         if not self.range_on.get():
#             raise FrameRangeError(msg='TO SAVE RANGE OF FRAMES, TICK THE `Frame range` checkbox before clicking `Save Range`', source=self.__class__.__name__)
#         elif start_frm < 0:
#             raise FrameRangeError(msg="FRAME RANGE ERROR: START FRAME {} IS LESS THAN ZERO AND CANNOT BE SHOWN".format(str(start_frm)), source=self.__class__.__name__)
#         elif end_frm > self.max_frm_no:
#             raise FrameRangeError(msg="FRAME RANGE ERROR: END FRAME {} IS MORE THAN THE MAX VIDEO FRAME ({}) AND CANNOT BE SHOWN".format(str(end_frm), str(self.max_frm_no)), source=self.__class__.__name__)
#         elif start_frm == end_frm:
#             raise FrameRangeError(msg="FRAME RANGE ERROR: START FRAME AND END FRAME IS SET TO THE SAME VALUE ({}) AND DOES NOT REPRESENT A RANGE".format(str(end_frm)), source=self.__class__.__name__)
#         elif start_frm > end_frm:
#             raise FrameRangeError(msg="FRAME RANGE ERROR: START FRAME ({}) IS LARGER THAB THE END FRAME ({}). PLEASE SPECIFY A RANGE OF FRAMES WHERE THE START FRAME PRECEDE THE END FRAME".format(str(start_frm), str(end_frm)), source=self.__class__.__name__)
#         else:
#             for frm_no in range(int(start_frm), int(end_frm) + 1):
#                 for target in self.target_lst:
#                     target_absent_choice, target_present_choice = self.check_absent_vars[target].get(), self.check_present_vars[target].get()
#                     if target_present_choice == 1:
#                         self.data_df_targets[target].loc[frm_no] = 1
#                     if target_absent_choice == 1:
#                         self.data_df_targets[target].loc[frm_no] = 0
#                     if (target_absent_choice == 0) & (target_present_choice == 0):
#                         self.data_df_targets[target].loc[frm_no] = None
#             self.read_frm(frm_number=int(end_frm))
#             self.change_frm_box.delete(0, END)
#             self.change_frm_box.insert(0, end_frm)
#             self.create_print_statements(frame_range=True, start_frame=start_frm, end_frame=end_frm)
#
#     def save_results(self):
#         self.save_df = read_df(self.features_extracted_file_path, self.file_type)
#         self.save_df = pd.concat([self.save_df, self.data_df_targets], axis=1)
#         self.save_df = self.save_df.dropna(subset=self.target_lst)
#         try:
#             if self.file_type == Formats.CSV.value:
#                 self.save_df.to_csv(self.targets_inserted_file_path)
#             if self.file_type == Formats.PARQUET.value:
#                 self.save_df.to_parquet(self.targets_inserted_file_path)
#         except Exception as e:
#             print(e, 'SIMBA ERROR: File for video {} could not be saved.')
#             raise FileExistsError
#         stdout_success(msg=f'SAVED: Annotation file for video {self.video_name} saved within the project_folder/csv/targets_inserted directory.', source=self.__class__.__name__)
#         if not self.config.has_section('Last annotated frames'):
#             self.config.add_section('Last annotated frames')
#         self.config.set('Last annotated frames', str(self.video_name), str(self.current_frm_n.get()))
#         with open(self.config_path, 'w') as configfile: self.config.write(configfile)
#
#     def check_integrity_of_multiple_classifiers(self):
#         none_target_lst, labelled_target_lst = [], []
#         for target in self.target_lst:
#             target_absent_choice, target_present_choice = self.check_absent_vars[target].get(), self.check_present_vars[target].get()
#             if (target_absent_choice == 0) and (target_present_choice == 0):
#                 none_target_lst.append(target)
#             else:
#                 labelled_target_lst.append(target)
#         if (len(none_target_lst) > 0) & (len(labelled_target_lst) > 0):
#             raise AdvancedLabellingError(frame=str(self.current_frm_n.get()), lbl_lst=labelled_target_lst, unlabel_lst=none_target_lst, source=self.__class__.__name__)
#
#     def create_print_statements(self, frame_range: bool=None, start_frame: int=None, end_frame: int=None):
#         print('USER FRAME SELECTION(S):')
#         if not frame_range:
#             for target in self.target_lst:
#                 target_absent_choice, target_present_choice = self.check_absent_vars[target].get(), self.check_present_vars[target].get()
#                 if (target_absent_choice == 1) & (target_present_choice == 0):
#                     print('{} ABSENT IN FRAME {}'.format(target, self.current_frm_n.get()))
#                 if (target_present_choice == 1) & (target_absent_choice == 0):
#                     print('{} PRESENT IN FRAME {}'.format(target, self.current_frm_n.get()))
#                 if (target_present_choice == 0) & (target_absent_choice == 0):
#                     print('{} UN-ANNOTATED IN FRAME {}'.format(target, self.current_frm_n.get()))
#
#         if frame_range:
#             for target in self.target_lst:
#                 target_absent_choice, target_present_choice = self.check_absent_vars[target].get(), self.check_present_vars[target].get()
#                 if (target_present_choice == 1) & (target_absent_choice == 0):
#                     print('{} PRESENT IN FRAMES {} to {}'.format(target, str(start_frame), str(end_frame)))
#                 elif (target_absent_choice == 1) & (target_present_choice == 0):
#                     print('{} ABSENT IN FRAMES {} to {}'.format(target, str(start_frame), str(end_frame)))
#                 elif (target_absent_choice == 0) & (target_present_choice == 0):
#                     print('{} UN-ANNOTATED IN FRAMES {} to {}'.format(target, str(start_frame), str(end_frame)))
#
#
# def select_labelling_video_advanced(config_path: Union[str, os.PathLike],
#                                     continuing: Optional[bool] = False):
#     videos_dir = os.path.join(os.path.dirname(config_path), 'videos')
#     if not os.path.isdir(videos_dir):
#         videos_dir = None
#     video_file_path = filedialog.askopenfilename(filetypes=[("Video files", Options.ALL_VIDEO_FORMAT_STR_OPTIONS.value)], initialdir=videos_dir)
#     check_file_exist_and_readable(video_file_path)
#     video_meta = get_video_meta_data(video_file_path)
#     _, video_name, _ = get_fn_ext(video_file_path)
#     print(f'ANNOTATING VIDEO {video_name} \n VIDEO INFO: {video_meta}')
#     _ = AdvancedLabellingInterface(config_path=config_path, file_path=video_file_path, continuing=continuing)

# test = select_labelling_video_advanced(config_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini',
#                           continuing=False)

test = AdvancedLabellingInterface(config_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini',
                                  video_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/videos/Together_1.avi',
                                  continuing=False)
