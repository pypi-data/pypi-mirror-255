from simba.mixins.pop_up_mixin import PopUpMixin
from simba.ui.tkinter_functions import CreateLabelFrameWithIcon, FileSelect
from simba.utils.enums import Links, Keys
from simba.utils.checks import check_file_exist_and_readable
from simba.labelling.get_project_annotation_counts import get_project_annotation_counts
from tkinter import *

class AnnotationCountPopUp(PopUpMixin):
    def __init__(self):
        PopUpMixin.__init__(self, title='PROJECT ANNOTATION COUNTS')
        settings_frm = CreateLabelFrameWithIcon(parent=self.main_frm, header='SELECT PROJECT CONFIG', icon_name=Keys.DOCUMENTATION.value, icon_link=Links.COUNT_ANNOTATIONS_OUTSIDE_PROJECT.value)
        self.project_config_file_select = FileSelect(settings_frm, "PROJECT CONFIG PATH: " ,title='SELECT A PROJECT CONFIG .INI FILE', lblwidth=25, file_types=[('SIMBA PROJECT CONFIG (.INI)', '.ini')])

        settings_frm.grid(row=0, column=0, sticky=NW)
        self.project_config_file_select.grid(row=0, column=0, sticky=NW)
        self.create_run_frm(self.run)
        #self.main_frm.mainloop()

    def run(self):
        project_config_path = self.project_config_file_select.file_path
        check_file_exist_and_readable(file_path=project_config_path)
        _ = get_project_annotation_counts(config_path=project_config_path)
        self.root.destroy()

#AnnotationCountPopUp()



