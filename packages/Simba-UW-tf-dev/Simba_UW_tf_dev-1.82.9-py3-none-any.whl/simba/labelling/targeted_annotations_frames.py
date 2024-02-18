import os
from tkinter import *
from typing import Union
from tkinter import filedialog
from simba.mixins.config_reader import ConfigReader
from simba.mixins.annotator_mixin import AnnotatorMixin
from simba.utils.read_write import get_video_meta_data, get_fn_ext
from simba.utils.enums import Options, TagNames, Labelling
from simba.utils.printing import log_event
from simba.utils.checks import check_file_exist_and_readable


class TargetedAnnotatorFrames(AnnotatorMixin, ConfigReader):

    def __init__(self,
                 config_path: Union[str, os.PathLike],
                 video_path: Union[str, os.PathLike]):

        ConfigReader.__init__(self, config_path=config_path)
        log_event(logger_name=str(self.__class__.__name__), log_type=TagNames.CLASS_INIT.value, msg=self.create_log_msg_from_init_args(locals=locals()))
        _, video_name, _ = get_fn_ext(filepath=video_path)
        data_path = os.path.join(self.machine_results_dir, f'{video_name}.{self.file_type}')
        AnnotatorMixin.__init__(self, config_path=config_path, video_path=video_path, data_path=data_path, frame_size=Labelling.VIDEO_FRAME_SIZE.value, title=f'SIMBA CLIP FRAME ANNOTATOR - {video_name}')
        self.video_frm_label(frm_number=self.min_frm_no)
        self.h_nav_bar(parent=self.main_frm, update_funcs=[self.update_current_selected_frm_lbl, self.update_clf_radiobtns], store_funcs=[self.store_targeted_annotations_frames])
        self.targeted_frames_selection_pane(parent=self.main_frm)
        self.v_navigation_pane_targeted(parent=self.main_frm, update_funcs=[self.update_current_selected_frm_lbl], store_funcs=[self.store_targeted_annotations_frames], loc=(0, 2), save_func=self.targeted_annotations_frames_save)
        self.main_frm.mainloop()

def select_labelling_video_targeted_frames(config_path: Union[str, os.PathLike]):
    videos_path = os.path.join(os.path.dirname(config_path), 'videos')
    if not os.path.isdir(videos_path):
        videos_path = None
    video_file_path = filedialog.askopenfilename(filetypes=[("Video files", Options.ALL_VIDEO_FORMAT_STR_OPTIONS.value)], initialdir=videos_path)
    check_file_exist_and_readable(video_file_path)
    video_meta = get_video_meta_data(video_file_path)
    _, video_name, _ = get_fn_ext(video_file_path)
    print(f'ANNOTATING VIDEO {video_name} \n  VIDEO INFO: {video_meta}')
    _ = TargetedAnnotatorFrames(config_path=config_path, video_path=video_file_path)

#test = TargetedAnnotatorFrames(config_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini', video_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/videos/Together_1.avi')
#select_labelling_video_targeted_frames(config_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini')
