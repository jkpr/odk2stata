#!/usr/bin/env python3
import datetime
import os.path
import webbrowser

import wx

from .worker import Worker, evt_complete


TITLE = 'odk2stata'
APP_QUIT = 1
APP_ABOUT = 2
MAIN_WINDOW_WIDTH = 550
MAIN_WINDOW_HEIGHT = 525
MAX_PATH_LENGTH = 45


class MainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.xlsform_path = ''
        self.settings_path = ''
        self.output_path = ''
        self.messages = ''

        self.init_ui()
        self.init_menu()
        self.Center()

        self.Bind(wx.EVT_CLOSE, self.on_quit)

    def init_ui(self):

        panel = wx.Panel(self)

        grid = wx.GridBagSizer(5, 5)

        grid.Add((-1,1), pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM,
                  border=15)

        xlsform_st = wx.StaticText(panel, label="XLS Form")
        grid.Add(xlsform_st, pos=(1, 0), flag=wx.LEFT, border=10)

        self.xlsform_file_tc = wx.TextCtrl(panel)
        self.xlsform_file_tc.SetEditable(False)
        grid.Add(self.xlsform_file_tc, pos=(1, 1), span=(1, 3),
                  flag=wx.EXPAND)

        self.xlsform_btn = wx.Button(panel, label="Browse...")
        grid.Add(self.xlsform_btn, pos=(1, 4), flag=wx.RIGHT, border=10)
        self.xlsform_btn.Bind(wx.EVT_BUTTON, self.on_xlsform_btn)

        settings_st = wx.StaticText(panel, label="Settings")
        grid.Add(settings_st, pos=(2, 0), flag=wx.LEFT, border=10)

        self.settings_file_tc = wx.TextCtrl(panel)
        self.settings_file_tc.SetEditable(False)
        grid.Add(self.settings_file_tc, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)
        self.settings_file_tc.SetLabel('(use program defaults)')

        self.settings_btn = wx.Button(panel, label="Browse...")
        grid.Add(self.settings_btn, pos=(2, 4), flag=wx.RIGHT, border=10)
        self.settings_btn.Bind(wx.EVT_BUTTON, self.on_settings_btn)

        line = wx.StaticLine(panel)
        grid.Add(line, pos=(3, 0), span=(1, 5),
                 flag=wx.EXPAND | wx.BOTTOM, border=10)

        output_st = wx.StaticText(panel, label="Output")
        grid.Add(output_st, pos=(4, 0), flag=wx.LEFT, border=10)

        self.output_file_tc = wx.TextCtrl(panel)
        self.output_file_tc.SetEditable(False)
        grid.Add(self.output_file_tc, pos=(4, 1), span=(1, 3), flag=wx.EXPAND)

        self.output_btn = wx.Button(panel, label="Browse...")
        grid.Add(self.output_btn, pos=(4, 4), flag=wx.RIGHT, border=10)
        self.output_btn.Bind(wx.EVT_BUTTON, self.on_output_btn)

        messages_sb = wx.StaticBox(panel, label="Messages")

        boxsizer = wx.StaticBoxSizer(messages_sb, wx.VERTICAL)
        self.messages_tc = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, 250))
        self.messages_tc.SetEditable(False)
        self.messages_tc.SetValue(self.messages)
        boxsizer.Add(self.messages_tc, proportion=1, flag=wx.EXPAND)

        grid.Add(boxsizer, pos=(5, 0), span=(2, 5),
                  flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=10)

        self.help_btn = wx.Button(panel, label='Help')
        grid.Add(self.help_btn, pos=(7, 0), flag=wx.LEFT, border=10)
        self.help_btn.Bind(wx.EVT_BUTTON, self.on_help_btn)

        self.run_btn = wx.Button(panel, label="Run")
        grid.Add(self.run_btn, pos=(7, 4), flag=wx.BOTTOM | wx.RIGHT, border=10)
        self.run_btn.Bind(wx.EVT_BUTTON, self.on_run_btn)
        self.run_btn.Disable()

        grid.AddGrowableCol(2)

        panel.SetSizer(grid)
        # grid.Fit(self)

        evt_complete(self, self.on_worker_complete)

    def on_xlsform_btn(self, e):
        dlg = wx.FileDialog(
            self, message='Choose a file',
            defaultFile='',
            wildcard='XLSForm files (*.xls,*.xlsx)|*.xls;*.xlsx',
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        )
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.xlsform_path = dlg.GetPath()
            self.xlsform_file_tc.SetLabel(
                self.shorten_string(self.xlsform_path, MAX_PATH_LENGTH))
            self.output_path = os.path.dirname(self.xlsform_path)
            self.output_file_tc.SetLabel(
                self.shorten_string(self.output_path, MAX_PATH_LENGTH))
            if self.xlsform_path and self.output_path:
                self.run_btn.Enable()
            else:
                self.run_btn.Disable()
        dlg.Destroy()

    def on_settings_btn(self, e):
        dlg = wx.FileDialog(
            self, message='Choose a file',
            defaultFile='',
            wildcard='Settings file (*.ini,*.cfg)|*.ini;*.cfg',
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        )
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.settings_path = dlg.GetPath()
            self.settings_file_tc.SetLabel(
                self.shorten_string(self.settings_path, MAX_PATH_LENGTH))
        dlg.Destroy()

    def on_output_btn(self, e):
        dlg = wx.DirDialog(
            self, message='Choose a location',
            defaultPath=self.output_path,
            style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR)
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.output_path = dlg.GetPath()
            self.output_file_tc.SetLabel(
                self.shorten_string(self.output_path, MAX_PATH_LENGTH))
            if self.xlsform_path and self.output_path:
                self.run_btn.Enable()
            else:
                self.run_btn.Disable()
        dlg.Destroy()

    def on_run_btn(self, e):
        self.enable_ui(False)
        dt_now = datetime.datetime.now()
        now = dt_now.strftime("%H:%M:%S")
        start_msg = f'[Begin conversion at {now}]\n'
        xlsform_msg = f'XLS Form: {os.path.basename(self.xlsform_path)}\n'
        settings_basename = os.path.basename(
            self.settings_path) if self.settings_path else 'Using default settings'
        settings_msg = 'Settings: {}\n'.format(settings_basename)

        self.messages_tc.AppendText(start_msg)
        self.messages_tc.AppendText(xlsform_msg)
        self.messages_tc.AppendText(settings_msg)

        result_thread = Worker(self, self.xlsform_path, self.settings_path, self.output_path)
        result_thread.start()

    def on_help_btn(self, e):
        webbrowser.open("https://www.github.com/jkpr/odk2stata")

    def on_worker_complete(self, event):
        if event.success:
            self.messages_tc.AppendText('\nSUCCESS!\n')
        else:
            self.messages_tc.AppendText('\nSomething went wrong\n')
        self.messages_tc.AppendText(event.message)
        self.messages_tc.AppendText('- - - - - - - - - - - - - - - - - - -\n')
        self.enable_ui(True)

    def init_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        help_menu = wx.Menu()

        quit_menu_item = wx.MenuItem(file_menu, APP_QUIT,
                                          '&Quit\tCtrl+Q')
        about_menu_item = wx.MenuItem(help_menu, APP_ABOUT,
                                           '&About ' + TITLE)

        file_menu.Append(quit_menu_item)
        help_menu.Append(about_menu_item)

        menu_bar.Append(file_menu, '&File')
        menu_bar.Append(help_menu, '&About')

        self.Bind(wx.EVT_MENU, self.on_quit, id=APP_QUIT)
        self.Bind(wx.EVT_MENU, self.on_help_btn, id=APP_ABOUT)
        self.SetMenuBar(menu_bar)

    def on_quit(self, e):
        self.Destroy()

    def enable_ui(self, enable):
        """Turn UI elements on and off."""
        self.xlsform_btn.Enable(enable)
        self.settings_btn.Enable(enable)
        self.output_btn.Enable(enable)
        self.help_btn.Enable(enable)
        self.run_btn.Enable(enable)

    @staticmethod
    def shorten_string(string, max_length):
        if len(string) >= max_length:
            return '...' + string[len(string) - max_length:len(string)]
        else:
            return string


def create_app():
    app = wx.App()
    app.SetAppName(TITLE)
    ex = MainWindow(None, size=(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT),
                    title=TITLE)
    ex.Show()
    app.MainLoop()
