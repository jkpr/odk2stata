import os.path
import threading

import wx

from ..dofile.do_file_collection import DoFileCollection


EVT_COMPLETE_ID = wx.NewId()


def evt_complete(win, func):
    win.Connect(-1, -1, EVT_COMPLETE_ID, func)


class CompleteEvent(wx.PyEvent):

    def __init__(self, message, success):

        super().__init__()
        self.SetEventType(EVT_COMPLETE_ID)
        self.message = message
        self.success = success


class Worker(threading.Thread):

    def __init__(self, panel, xlsform_path, settings_path, output_dir):
        super().__init__()

        self.panel = panel
        self.xlsform_path = xlsform_path
        self.settings_path = settings_path
        self.filename = os.path.splitext(os.path.basename(xlsform_path))[0] + '.do'
        self.output_path = os.path.join(output_dir, self.filename)

    def run(self):
        do_files = DoFileCollection.from_file(self.xlsform_path,
                                              settings_path=self.settings_path)
        do_files.write_out(self.output_path)
        message = f'Do file saved to "{self.output_path}"\n'
        wx.PostEvent(self.panel, CompleteEvent(message, True))
