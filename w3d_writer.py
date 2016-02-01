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
from pyw3d import project
import tkinter as tk
from tkinter import ttk
from tkinter import font


class W3DWriter(tk.Frame):
    """GUI interface to 3D virtual environments"""

    def __init__(self, parent):
        super(W3DWriter, self).__init__(parent, background="white")
        self.parent = parent
        self.font = font.Font(family="Helvetica", size=12)
        self.project = project.W3DProject()
        self.initUI()

    def generate_tabs(self):
        self.tabs = {}
        self.tabs["project"] = project.ProjectOptions(
            self.interface, self.project)
        for category in ["objects", "groups", "timelines", "trigger_events"]:
            self.tabs[category] = project.W3DProject.argument_validators[
                category].ui(self.interface, category, self.project, category)

    def initUI(self):
        self.parent.title("W3D Writer")
        self.pack(fill=tk.BOTH, expand=1)
        self.interface = ttk.Notebook(self)
        self.generate_tabs()
        self.interface.add(
            self.tabs["project"], text=self.tabs["project"].title_string)
        for category in ["objects", "groups", "timelines", "trigger_events"]:
            self.interface.add(
                self.tabs[category], text=self.tabs[category].title_string)
        self.interface.pack(fill=tk.BOTH, expand=1)


def start_editor():
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry("{}x{}".format(width, height))
    W3DWriter(root)
    root.mainloop()

if __name__ == "__main__":
    start_editor()
