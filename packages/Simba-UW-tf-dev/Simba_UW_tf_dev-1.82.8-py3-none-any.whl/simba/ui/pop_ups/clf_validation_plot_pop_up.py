__author__ = "Simon Nilsson"

from tkinter import *
import threading
import os

from simba.mixins.pop_up_mixin import PopUpMixin
from simba.mixins.config_reader import ConfigReader
from simba.utils.enums import Keys, Links, Formats, Options
from simba.ui.tkinter_functions import DropDownMenu, CreateLabelFrameWithIcon, Entry_Box, FileSelect
from simba.utils.read_write import get_file_name_info_in_directory, get_fn_ext
from simba.utils.checks import check_int
from simba.utils.errors import NoFilesFoundError
from simba.plotting.clf_validator import ClassifierValidationClips
from simba.plotting.clf_validator_mp import ClassifierValidationClipsMultiprocess


class ClassifierValidationPopUp(PopUpMixin, ConfigReader):
    def __init__(self,
                 config_path: str):


        ConfigReader.__init__(self, config_path=config_path)
        self.files_found_dict = get_file_name_info_in_directory(directory=self.machine_results_dir, file_type=self.file_type)
        if len(list(self.files_found_dict.keys())) == 0:
            raise NoFilesFoundError(msg=f'No data files found in {self.machine_results_dir} directory', source=self.__class__.__name__)
        PopUpMixin.__init__(self, title='SIMBA CLASSIFIER VALIDATION CLIPS')
        color_names = list(self.colors_dict.keys())
        self.one_vid_per_bout_var = BooleanVar(value=False)
        self.one_vid_per_video_var = BooleanVar(value=True)
        self.settings_frm = CreateLabelFrameWithIcon(parent=self.main_frm, header='SETTINGS', icon_name=Keys.DOCUMENTATION.value, icon_link=Links.CLF_VALIDATION.value)
        self.seconds_entry = Entry_Box(self.settings_frm, 'SECONDS PADDING: ', '20', validation='numeric')
        self.clf_dropdown = DropDownMenu(self.settings_frm, 'CLASSIFIER: ', self.clf_names, '20')
        self.clr_dropdown = DropDownMenu(self.settings_frm, 'TEXT COLOR: ', color_names, '20')
        self.highlight_clr_dropdown = DropDownMenu(self.settings_frm, 'HIGHLIGHT TEXT COLOR: ', ['None'] + color_names, '20')
        self.video_speed_dropdown = DropDownMenu(self.settings_frm, 'VIDEO SPEED: ', Options.SPEED_OPTIONS.value, '20')
        self.clf_dropdown.setChoices(self.clf_names[0])
        self.clr_dropdown.setChoices('Cyan')
        self.seconds_entry.entry_set(val=2)
        self.highlight_clr_dropdown.setChoices('None')
        self.video_speed_dropdown.setChoices(1.0)
        self.individual_bout_clips_cb = Checkbutton(self.settings_frm, text='CREATE ONE CLIP PER BOUT', variable=self.one_vid_per_bout_var)
        self.individual_clip_per_video_cb = Checkbutton(self.settings_frm, text='CREATE ONE CLIP PER VIDEO', variable=self.one_vid_per_video_var)

        self.run_frm = LabelFrame(self.main_frm, text='RUN', font=Formats.LABELFRAME_HEADER_FORMAT.value, pady=5, padx=5, fg='black')
        self.run_single_video_frm = LabelFrame(self.run_frm, text='SINGLE VIDEO', font=Formats.LABELFRAME_HEADER_FORMAT.value, pady=5, padx=5, fg='black')
        self.run_single_video_btn = Button(self.run_single_video_frm, text='Create single video', fg='blue', command=lambda: self.run(multiple_videos=False))
        self.single_video_dropdown = DropDownMenu(self.run_single_video_frm, 'Video:', list(self.files_found_dict.keys()), '12', com= lambda x: self.update_file_select_box_from_dropdown(filename=x, fileselectbox=self.select_video_fileselect))
        self.single_video_dropdown.setChoices(list(self.files_found_dict.keys())[0])
        self.select_video_fileselect = FileSelect(self.run_single_video_frm, 'Machine results path:', dropdown=self.single_video_dropdown, file_types=[('SIMBA DATA FILE', Options.WORKFLOW_FILE_TYPE_STR_OPTIONS.value)], initialdir=self.machine_results_dir)
        self.select_video_fileselect.filePath.set(value=list(self.files_found_dict.keys())[0])
        self.run_multiple_videos = LabelFrame(self.run_frm, text='MULTIPLE VIDEO', font=Formats.LABELFRAME_HEADER_FORMAT.value, pady=5, padx=5, fg='black')
        self.run_multiple_video_btn = Button(self.run_multiple_videos, text='Create multiple videos ({} video(s) found)'.format(str(len(list(self.files_found_dict.keys())))), fg='blue', command=lambda: self.run(multiple_videos=True))
        self.settings_frm.grid(row=0,sticky=NW)
        self.seconds_entry.grid(row=0, sticky=NW)
        self.clf_dropdown.grid(row=1, sticky=NW)
        self.clr_dropdown.grid(row=2, sticky=NW)
        self.highlight_clr_dropdown.grid(row=3, sticky=NW)
        self.video_speed_dropdown.grid(row=4, sticky=NW)
        self.individual_bout_clips_cb.grid(row=5, column=0, sticky=NW)
        self.individual_clip_per_video_cb.grid(row=6, column=0, sticky=NW)
        self.create_multiprocess_choice(parent=self.settings_frm)


        self.run_frm.grid(row=1, column=0, sticky=NW)
        self.run_single_video_frm.grid(row=0, column=0, sticky=NW)
        self.run_single_video_btn.grid(row=0, column=0, sticky=NW)
        self.single_video_dropdown.grid(row=0, column=1, sticky=NW)
        self.select_video_fileselect.grid(row=0, column=2, sticky=NW)
        self.run_multiple_videos.grid(row=1, column=0, sticky=NW)
        self.run_multiple_video_btn.grid(row=0, column=0, sticky=NW)

        self.main_frm.mainloop()

    def run(self, multiple_videos: bool):
        check_int(name='CLIP SECONDS', value=self.seconds_entry.entry_get)
        if self.highlight_clr_dropdown.getChoices() == 'None':
            highlight_clr = None
        else:
            highlight_clr = self.colors_dict[self.highlight_clr_dropdown.getChoices()]
        if multiple_videos:
            data_paths = list(self.files_found_dict.values())
        else:
            if '.' in self.single_video_dropdown.getChoices():
                file_name = get_fn_ext(self.single_video_dropdown.getChoices())[1]
            else:
                file_name = self.single_video_dropdown.getChoices()
            file_path = os.path.join(self.machine_results_dir, f'{file_name}.{self.file_type}')
            if not os.path.isfile(file_path):
                raise NoFilesFoundError(msg=f'The file {file_name} does not exist in the {self.machine_results_dir} directory', source=self.__class__.__name__)
            data_paths = [file_path]

        if not self.multiprocess_var.get():
            clf_validator = ClassifierValidationClips(config_path=self.config_path,
                                                      window=int(self.seconds_entry.entry_get),
                                                      clf_name=self.clf_dropdown.getChoices(),
                                                      clips=self.one_vid_per_bout_var.get(),
                                                      text_clr=self.colors_dict[self.clr_dropdown.getChoices()],
                                                      highlight_clr=highlight_clr,
                                                      video_speed=float(self.video_speed_dropdown.getChoices()),
                                                      concat_video=self.one_vid_per_video_var.get(),
                                                      data_paths=data_paths)

        else:
            clf_validator = ClassifierValidationClipsMultiprocess(config_path=self.config_path,
                                                                  window=int(self.seconds_entry.entry_get),
                                                                  clf_name=self.clf_dropdown.getChoices(),
                                                                  clips=self.one_vid_per_bout_var.get(),
                                                                  text_clr=self.colors_dict[self.clr_dropdown.getChoices()],
                                                                  highlight_clr=highlight_clr,
                                                                  video_speed=float(self.video_speed_dropdown.getChoices()),
                                                                  concat_video=self.one_vid_per_video_var.get(),
                                                                  data_paths=data_paths,
                                                                  core_cnt=int(self.multiprocess_dropdown.getChoices()))


        threading.Thread(target=clf_validator.run()).start()


#_ = ClassifierValidationPopUp(config_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini')
