#!/usr/bin/env python3
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

"""A script to simplify installing Writing3D"""

import sys
import site
import platform
import os
import queue
import subprocess
import threading
import shutil
from setup import find_existing_pyw3d, find_subdirectory

CURRENT_OS = platform.system()
if CURRENT_OS in ['Darwin']:
    CURRENT_OS = "Mac"
if CURRENT_OS not in ("Linux", "Windows", "Mac"):
    CURRENT_OS = "Other"
try:
    import tkinter as tk
    from tkinter import font
    import tkinter.ttk as ttk
except ImportError:
    if sys.version_info[0] != 3:
        print("Must be run with Python 3.x")
        input()
        raise RuntimeError("Incorrect Python version")

    if CURRENT_OS not in ["Windows", "Mac"]:
        print("Please install tkinter and try again.")
        input()
        raise RuntimeError("tkinter not found")
    else:
        print(
            "tkinter not found on your system. Please contact the Writing3D"
            " maintainer.")

SCRIPTDIR = os.path.abspath(os.path.dirname(__file__))


def module_dir():
    return site.getusersitepackages()


def warn(message):
    warn_window = tk.Toplevel()
    warn_window.title("ERROR")
    error_message = tk.Message(warn_window, text=message, width=200)
    error_message.pack()
    dismiss = tk.Button(
        warn_window, text="Dismiss", command=warn_window.destroy)
    dismiss.pack()


def find_script(name):
    user_base = site.getuserbase()
    script_path = find_subdirectory("bin", user_base)
    if script_path is None:
        script_path = find_subdirectory("Scripts", user_base)
    script_path = os.path.join(script_path, name)
    if os.path.isfile(script_path):
        return script_path
    return None


class W3DCleanAndInstall(threading.Thread):
    def clean_old_install(self):
        subprocess.call(
            [sys.executable, "setup.py", 'clean']
        )
        old_pyw3d = find_existing_pyw3d()
        if old_pyw3d is not None:
            if os.path.splitext(old_pyw3d)[1].lower() == ".egg":
                os.remove(old_pyw3d)
            else:
                shutil.rmtree(old_pyw3d)

    def __init__(self, queue, clean=False):
        super().__init__()
        self.queue = queue
        self.clean = clean

    def run(self):
        if self.clean:
            self.clean_old_install()
        os.chdir(SCRIPTDIR)
        with open("w3d_install.log", "w") as log_file:
            subprocess.call([
                sys.executable, "setup.py", 'install', '--user'],
                stdout=log_file, stderr=log_file
            )
        self.queue.put("Install complete!")


class Installer(tk.Frame):
    """GUI installer for Writing3D"""

    def check_completion(self):
        try:
            self.queue.get(0)
            self.progress.stop()
            self.next_button.config(state=tk.NORMAL)
            self.next_slide()
        except queue.Empty:
            self.after(100, self.check_completion)

    def init_slide(self):
        self.interior.destroy()
        self.interior = tk.Frame(self)
        self.interior.pack(anchor=tk.N, fill=tk.BOTH, expand=1)
        self.create_buttons()
        if self.current_slide == 0:
            self.label = tk.Label(
                self.interior,
                text="""Welcome to Writing3D!

This installer will set up Writing3D and Blender, the engine used to render
Writing3D projects. The install may take some time (especially with a slow
network connection) so please be patient after clicking the Next button.

Please click the Next button to begin the install process.""",
                font=self.font,
                justify=tk.LEFT)
            self.label.pack()
            return

        if self.current_slide == 1:
            self.label = tk.Label(
                self.interior,
                text="""Now installing...

Writing3D is now being installed. Please wait.""",

                font=self.font,
                justify=tk.LEFT)
            self.label.pack()
            self.progress = ttk.Progressbar(
                self.interior, orient="horizontal", mode="indeterminate"
            )
            self.progress.pack(expand=1, fill=tk.X, side=tk.BOTTOM)
            self.next_button.config(state=tk.DISABLED)

            self.queue = queue.Queue()
            self.progress.start()
            W3DCleanAndInstall(self.queue, clean=self.clean).start()
            self.after(100, self.check_completion)
            return

        if self.current_slide == 2:
            self.label = tk.Label(
                self.interior,
                text="""Installation Complete!

Installation of Writing3D is now complete. Log written to w3d_install.log. As a
starting point, try running some of the samples in the samples directory. If
you are using Writing3D with the legacy CWEditor.jar, you will find cwapp.py at
{} """.format(find_script("cwapp.py")),
                font=self.font,
                justify=tk.LEFT)
            self.label.pack()
            self.create_finish_button()
            return

    def next_slide(self):
        self.current_slide = min(
            self.current_slide + 1,
            self.total_slides - 1)
        self.init_slide()

    def back_slide(self):
        self.current_slide = max(self.current_slide - 1, 0)
        self.init_slide()

    def create_finish_button(self):
        self.next_button.destroy()
        self.finish_button = tk.Button(
            self.interior, text="Finish", command=self.parent.destroy)
        self.finish_button.pack(
            side=tk.RIGHT, anchor=tk.SE, fill=tk.X, expand=1)

    def create_buttons(self):
        # TODO: This is an ugly hack
        try:
            self.back_button.destroy()
            self.next_button.destroy()
        except AttributeError:
            pass
        self.back_button = tk.Button(
            self, text="Back", command=self.back_slide)
        if self.current_slide == 0:
            self.back_button.config(state=tk.DISABLED)
        self.next_button = tk.Button(
            self, text="Next", command=self.next_slide)
        if self.current_slide == self.total_slides - 1:
            self.next_button.config(state=tk.DISABLED)
        self.back_button.pack(side=tk.LEFT, anchor=tk.SW, fill=tk.X, expand=1)
        self.next_button.pack(side=tk.RIGHT, anchor=tk.SE, fill=tk.X, expand=1)

    def initUI(self):
        self.parent.title("W3D Installer")
        self.pack(fill=tk.BOTH, expand=1)
        self.interior = tk.Frame(self)
        self.init_slide()
        self.create_buttons()

    def __init__(self, parent, clean=True):
        super(Installer, self).__init__(parent)
        self.parent = parent
        self.current_slide = 0
        self.total_slides = 3
        self.font = font.Font(family="Helvetica", size=14)
        self.initUI()
        self.clean = clean


def start_installer():
    root = tk.Tk()
    Installer(root)
    root.mainloop()

if __name__ == "__main__":
    start_installer()
