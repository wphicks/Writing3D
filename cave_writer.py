"""A GUI interface for development of artwork in 3D virtual environments

This application is designed to allow non-technical users to work painlessly in
a virtual environment and to allow technical users to develop art and
literature much more quickly than they might otherwise be able to. The goal is
to get the technical challenges out of the way without preventing users from
tinkering "under the hood" if they so desire."""

import tkinter as tk


class UndoAction(object):
    """A discrete change in project values, used to maintain undo stack

    :param attribute: Project attribute to change
    :param old_value: Old value of attribute
    :param new_value: New value of attribute"""

    def __init__(self, attribute, old_value, new_value):
        self.attribute = attribute
        self.old_value = old_value
        self.new_value = new_value

        def do(self):
            #TODO: This is very wrong
            self.attribute = new_value

        def undo(self):
            self.attribute = old_value

class UndoAddAction(object):
    """Record of addition of a feature to project"""


class UndoStack(object):

    def __init__(self):
        self.actions = []


class CaveWriter(tk.Frame):
    """GUI interface to 3D virtual environments"""

    def __init__(self, parent):
        super(CaveWriter, self).__init__(self, parent, background="white")
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title = "Cave Writer"
        self.pack(fill=tk.BOTH, expand=1)


def start_editor():
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry("{}x{}".format(width, height))
    CaveWriter(root)
    root.mainloop()

if __name__ == "__main__":
    start_editor()
