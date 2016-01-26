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
from pycave import project
import tkinter as tk
from tkinter import ttk
from tkinter import font


class CaveWriter(tk.Frame):
    """GUI interface to 3D virtual environments"""

    def __init__(self, parent):
        super(CaveWriter, self).__init__(parent, background="white")
        self.parent = parent
        self.font = font.Font(family="Helvetica", size=12)
        self.project = project.CaveProject()
        self.initUI()

    def generate_tabs(self):
        self.tabs = {}
        self.tabs["project"] = project.ProjectOptions(
            self.interface, self.project)
        for category in ["objects", "groups", "timelines", "trigger_events"]:
            self.tabs[category] = project.CaveProject.argument_validators[
                category].ui(self.interface, category, self.project, category)

    def initUI(self):
        self.parent.title("Cave Writer")
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
    CaveWriter(root)
    root.mainloop()

if __name__ == "__main__":
    start_editor()
