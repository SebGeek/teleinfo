#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import datetime
try:
    import Tkinter
except:
    print "To install Tkinter: sudo apt-get install python-tk"


class ActionGUI:

    def __init__(self, gui_root, display=None):
        self.gui_root = gui_root
        self.display = display

    def power_mgt(self, action):
        self.display(datetime.datetime.now().strftime("%H:%M:%S ") + "Done.", show=True)

    def ED_mgt(self, action):
        self.display(datetime.datetime.now().strftime("%H:%M:%S ") + "Done.", show=True)

    def Device_mgt(self, action):
        self.display(datetime.datetime.now().strftime("%H:%M:%S ") + "Done.", show=True)

if __name__ == "__main__":
    ActionGUI(None)
