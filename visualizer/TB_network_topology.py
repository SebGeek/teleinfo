#!/usr/bin/python
# -*- coding:utf-8 -*-

import subprocess
import datetime
import threading
import os
from Tkinter import *

class ThreadReadStatus(threading.Thread):

    def __init__(self, read_status_queue, display):

        self.read_status_queue = read_status_queue
        self.display = display
        self.IsTerminated = False

        threading.Thread.__init__(self)

        self.start()  # Start the thread by calling run() method

    def stop(self):
        self.IsTerminated = True

    def update(self):
        pass

    def run(self):
        while True:
            command = self.read_status_queue.get(block=True)

            #self.display("Start " + command, erase=True)

            if command == "terminate_thread":
                break
            elif command == "refresh_all":
                self.refresh_other = True
                self.refresh_TRS_NBX = True
                self.refresh_ED = True

            self.display("Refresh done at " + datetime.datetime.now().strftime("%H:%M:%S "), show=True)


if __name__ == "__main__":
    pass