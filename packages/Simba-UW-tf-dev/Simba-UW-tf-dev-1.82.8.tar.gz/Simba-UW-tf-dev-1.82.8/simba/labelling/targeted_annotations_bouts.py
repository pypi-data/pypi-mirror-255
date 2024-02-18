import os
from tkinter import *
from typing import Union, List
from tkinter import filedialog
from simba.mixins.config_reader import ConfigReader
from simba.mixins.annotator_mixin import AnnotatorMixin
from simba.utils.read_write import find_video_of_file, get_video_meta_data, get_fn_ext
from simba.utils.enums import Options
from simba.utils.checks import check_file_exist_and_readable

class TargetedAnnotatorBouts(AnnotatorMixin, ConfigReader):

    """
    Annotator interface that lets users annotate a bout as eithe behavior present of behavior absent.

    Each annotated bout is saved in its individual file in the ``targets_inserted`` directory. A video clip of the annotated bout is
    also saved in the SimBA project ``videos`` folder, and the bout video metadata is added to the ``project_folder/logs`` directory.

    .. note::
       As of 01/24, this annotator GUi cannot be called through the main GUI.

    """

    def __init__(self,
                 config_path: Union[str, os.PathLike],
                 video_path: Union[str, os.PathLike]):

        ConfigReader.__init__(self, config_path=config_path)
        _, video_name, _ = get_fn_ext(filepath=video_path)
        data_path = os.path.join(self.machine_results_dir, f'{video_name}.{self.file_type}')
        AnnotatorMixin.__init__(self, config_path=config_path, video_path=video_path, data_path=data_path, frame_size=(700, 500))

        self.video_frm_label(frm_number=self.min_frm_no)
        self.nav_bar = self.h_nav_bar(parent=self.main_frm)
        self.selection_pane = self.targeted_bouts_pane(parent=self.main_frm)
        self.play_video_frame = self.v_navigation_pane_targeted_clips_version(parent=self.main_frm)

        self.nav_bar.grid(row=1, column=0, sticky=NW)
        self.selection_pane.grid(row=0, column=1, sticky=NW)
        self.play_video_frame.grid(row=0, column=2, sticky=NW)
        self.main_frm.mainloop()

def select_labelling_video_targeted_clips(config_path: Union[str, os.PathLike]):
    videos_dir = os.path.join(os.path.dirname(config_path), 'videos')
    if not os.path.isdir(videos_dir):
        videos_dir = None
    video_file_path = filedialog.askopenfilename(filetypes=[("Video files", Options.ALL_VIDEO_FORMAT_STR_OPTIONS.value)], initialdir=videos_dir)
    check_file_exist_and_readable(video_file_path)
    video_meta = get_video_meta_data(video_file_path)
    _, video_name, _ = get_fn_ext(video_file_path)
    print(f'ANNOTATING VIDEO {video_name} \n  VIDEO INFO: {video_meta}')
    _ = TargetedAnnotatorBouts(config_path=config_path, video_path=video_file_path)

#test = TargetedAnnotatorWithClips(config_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini', video_name='Together_1')
