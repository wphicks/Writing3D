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

"""Non-input Tk widgets for structuring UI"""

import tkinter as tk


class ScrollableFrame(tk.Frame):
    """Scrollable frame widget

    This implementation based on the one presented at
    http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame"""

    def __init__(self, parent, *args, **kwargs):
        super(ScrollableFrame, self).__init__(parent, *args, **kwargs)
        self.scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scroll.pack(fill=tk.Y, side=tk.RIGHT, expand=0)
        self.canvas = tk.Canvas(
            self, bd=0, highlightthickness=0, yscrollcommand=self.scroll.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.scroll.config(command=self.canvas.yview)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        self.inside_frame = tk.Frame(self.canvas)
        self.in_id = self.canvas.create_window(
            0, 0, window=self.inside_frame, anchor=tk.NW)

        self.inside_frame.bind('<Configure>', self._update_inside_dimensions)
        self.canvas.bind('<Configure>', self._update_canvas_dimensions)

    def _update_inside_dimensions(self, event):
        new_dims = (
            self.inside_frame.winfo_reqwidth(),
            self.inside_frame.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 {} {}".format(*new_dims))
        if self.inside_frame.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.inside_frame.winfo_reqwidth())

    def _update_canvas_dimensions(self, event):
        if self.inside_frame.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure(
                self.in_id, width=self.canvas.winfo_width())
