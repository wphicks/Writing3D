#!/usr/bin/env python
# Copyright (C) 2016 William Hicks
#
# This file is part of Writing3D.
#
# Writing3D is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""A GUI interface for development of artwork in 3D virtual environments

This application is designed to allow non-technical users to work painlessly in
a virtual environment and to allow technical users to develop art and
literature much more quickly than they might otherwise be able to. The goal is
to get the technical challenges out of the way without preventing users from
tinkering "under the hood" if they so desire."""

import sys
import os
sys.path.append(
    os.path.abspath(os.path.dirname(__file__))
)
import pyw3d
from pyw3d import project
import w3dui
import tkinter as tk
from tkinter import ttk
from tkinter import font

BLENDER_EXEC = "blender"  # BLENDEREXECSUBTAG
BLENDER_PLAY = "blenderplayer"  # BLENDERPLAYERSUBTAG


class W3DWriter(tk.Frame):
    """GUI interface to 3D virtual environments"""

    def get_stored_value(self):
        return self.project

    def get_input_value(self):
        return self.project

    def __init__(self, parent):
        super(W3DWriter, self).__init__(parent, background="white")
        self.parent = parent
        self.font = font.Font(family="Helvetica", size=12)
        self.project = project.W3DProject()
        self.project_path = pyw3d.path.ProjectPath(self.project)
        self.global_entries = []
        self.initUI()

    def generate_tabs(self):
        self.tabs = {}
        self.tabs["globals"] = tk.Frame(self.interface)
        for option in self.project.ui_order:
            self.global_entries.append(w3dui.widget_factories.widget_creator(
                input_parent=self, frame=self.tabs["globals"],
                option_name=option, project_path=self.project_path)
            )
            self.global_entries[-1].config(text=option)
            self.global_entries[-1].pack(side=tk.LEFT, anchor=tk.NW)
        for category in ["objects", "groups", "timelines", "trigger_events"]:
            self.tabs[category] = w3dui.widget_factories.widget_creator(
                input_parent=self, frame=self.interface, option_name=category,
                project_path=self.project_path)

    def initUI(self):
        self.parent.title("W3D Writer")
        self.pack(fill=tk.BOTH, expand=1)
        self.interface = ttk.Notebook(self)
        self.generate_tabs()
        self.interface.add(self.tabs["globals"], text="globals")
        for category in ["objects", "groups", "timelines", "trigger_events"]:
            self.interface.add(
                self.tabs[category], text=category)
        self.interface.pack(fill=tk.BOTH, expand=1)


def start_editor():
    root = tk.Tk()
    root.lift()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry("{}x{}".format(width, height))
    W3DWriter(root)
    root.mainloop()

if __name__ == "__main__":
    start_editor()
