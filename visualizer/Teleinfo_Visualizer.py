#!/usr/bin/python
# -*- coding:utf-8 -*-

#############################################
#
#
#
#############################################

import os
import sys

# Tkinter
try:
    from Tkinter import *
    from ScrolledText import *
    import tkMessageBox
except:
    print "To install Tkinter: sudo apt-get install python-tk"
# Matplotlib
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

# Maths
from numpy import arange, sin, pi
import random

LOG_FRAME = False

class Application(Frame):

    def __init__(self, root, title):
        self.root = root
        Frame.__init__(self, self.root)
        self.root.title(title)

        self.display_text = ""

        menu = Menu(self.root)
        self.root.config(menu=menu)

        refresh_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Refresh", menu=refresh_menu)
        refresh_menu.add_command(label="refresh_all", command=self.refresh_all)

        action_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Action", menu=action_menu)
        action_menu.add_command(label="refresh_all", command=self.refresh_all)
        action_menu.add_separator()
        action_menu.add_command(label="refresh_all", command=self.refresh_all)

        help_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.about_command)

        self.__createWidgets(self.root)

        # Update window graphics
        self.update()

    def display(self, msg, erase=False, show=False):
        if LOG_FRAME == True:
            self.textPad.insert('insert', msg + "\n")
            self.textPad.see('end')

        print msg

    def __createWidgets(self, parent):
        # Define a weight for automatic resize of components
        parent.columnconfigure(0, weight=1)
        row_current = 0

        # Plot
        f = Figure(figsize=(5, 4), dpi=100)
        a = f.add_subplot(111)
        t = arange(0.0, 3.0, 0.01)
        s = sin(pi * t * random.randint(1, 5))
        a.plot(t, s, label="CPU0")

        a.legend()
        #a.axis([0, 300, 0, 100])  # axis range: 0-300s / 0-100%
        #matplotlib.pyplot.xlabel("time (s)")
        #a.ylabel("CPU used (%)")
        a.grid(True)

        parent.rowconfigure(row_current, weight=1)
        canvas = FigureCanvasTkAgg(f, master=parent)
        canvas.get_tk_widget().grid(row=row_current, column=0, sticky="nsew")
        toolbar = NavigationToolbar2TkAgg(canvas, parent)
        toolbar.grid(row=row_current, column=0, sticky="nw")

        # Log_frame
        if LOG_FRAME == True:
            row_current += 1
            parent.rowconfigure(row_current, weight=1)
            self.Log_frame = LabelFrame(parent, text='Log', padx=2, pady=2)
            self.Log_frame.rowconfigure(0, weight=1)
            self.Log_frame.grid(row=row_current, column=0, sticky = NSEW, padx=5, pady=5)

            self.Log_frame.columnconfigure(0, weight=1)

            self.textPad = ScrolledText(self.Log_frame, width=110, height=10)
            self.textPad.grid(row=0, column=0)

    def refresh_all(self):
        self.display("refresh_all")
        # Update window graphics
        self.update()

    def about_command(self):
        tkMessageBox.showinfo("About", "Teleinfo visualizer\n\nS. Auray\n14/11/2016")


if __name__ == '__main__':
    root = Tk()
    root.geometry("1000x800")

    current_dir = os.path.dirname(os.path.realpath(__file__))
    icon_path = os.path.join(current_dir, 'icon.gif')

    img = PhotoImage(file=icon_path)
    root.tk.call('wm', 'iconphoto', root._w, img)

    app = Application(root, title="Teleinfo visualizer")
    app.mainloop()
