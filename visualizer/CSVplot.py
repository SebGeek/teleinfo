#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import csv
import datetime
import inspect

# Tkinter
from Tkinter import *
from ScrolledText import *
import tkMessageBox
import tkFileDialog

# Matplotlib
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
matplotlib.use('TkAgg')

LOG_FRAME = False
window_zoomed = True
request_file = True #"Z:/teleinfo/log/log.csv.2016-11-19"


class Application(Frame):
    def __init__(self, root, title):
        self.root = root
        Frame.__init__(self, self.root)
        self.root.title(title)

        # Menu
        menu = Menu(self.root)
        self.root.config(menu=menu)

        refresh_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Refresh", menu=refresh_menu)
        refresh_menu.add_command(label="refresh_all", command=self.refresh_all)

        action_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Action", menu=action_menu)
        action_menu.add_command(label="do_quit", command=self.do_quit)

        help_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.about_command)

        # Main window
        self.first_time = True
        self.first_date = True
        self.CursorOn = False

        self.__create_widgets()

        # Update window graphics
        self.update()

    def display(self, msg):
        if LOG_FRAME == True:
            self.textPad.insert('insert', msg + "\n")
            self.textPad.see('end')

        print msg

    def __key(self, event):
        if str(event.key).endswith("i") and self.CursorOn:
            print "interactive"
            return

        if (str(event.key).endswith("c") and self.CursorOn) or str(event.key).endswith("escape"):
            #cursors OFF
            self.fig.canvas.mpl_disconnect(self.binding_id_move)
            self.fig.canvas.mpl_disconnect(self.binding_id_click)
            self.cursor.clear_cursors()
            self.CursorOn = False
            print "cursor OFF"
            return

        if str(event.key).endswith("c") and not self.CursorOn:
            #cursors ON
            self.binding_id_move = self.fig.canvas.mpl_connect('motion_notify_event', self.cursor.mouse_move)
            self.binding_id_click = self.fig.canvas.mpl_connect('button_press_event', self.cursor.mouse_click)
            self.CursorOn = True
            print "cursor ON"
            return

    def __create_widgets(self):
        # Define a weight for automatic resize of components
        self.root.columnconfigure(0, weight=1)
        row_current = 0

        # Plot frame
        self.fig = plt.figure(figsize=(5, 4), dpi=100)
        self.root.rowconfigure(row_current, weight=1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas._tkcanvas.config(background='white', borderwidth=0, highlightthickness=0)
        self.canvas.get_tk_widget().grid(row=row_current, column=0, sticky="nsew")
        toolbar = NavigationToolbar2TkAgg(self.canvas, self.root)
        toolbar.grid(row=row_current, column=0, sticky="nw")

        self.plot_figure()

        # Log frame
        if LOG_FRAME == True:
            row_current += 1
            self.root.rowconfigure(row_current, weight=1)
            self.Log_frame = LabelFrame(self.root, text='Log', padx=2, pady=2)
            self.Log_frame.rowconfigure(0, weight=1)
            self.Log_frame.grid(row=row_current, column=0, sticky=NSEW, padx=5, pady=5)
            self.Log_frame.columnconfigure(0, weight=1)
            self.textPad = ScrolledText(self.Log_frame, width=110, height=10)
            self.textPad.grid(row=0, column=0)

    def plot_figure(self):
        if request_file == True:
            filename = tkFileDialog.askopenfilename(initialdir=inspect.currentframe())
        else:
            filename = request_file
        csvfile = open(filename, 'rb')
        reader = csv.reader(csvfile, delimiter=";")

        if self.first_time == True:
            # Read the number of columns
            first_line = csvfile.readline()
            self.nb_col = first_line.count(";")

            subplot = []
            for i in range(self.nb_col):
                # "2, 3, 4" means "2x3 grid, 4th subplot1".
                subplot.append(self.fig.add_subplot(self.nb_col, 1, i+1))

                # format the ticks
                format_ticks = mdates.DateFormatter('%H')
                subplot[i].xaxis.set_major_locator(mdates.HourLocator())
                subplot[i].xaxis.set_major_formatter(format_ticks)

            # Labels
            plt.xlabel("Temps (h)")
            plt.ylabel("Puissance (W)")

            plt.subplots_adjust(left=0.06, right=0.99, bottom=0.08, top=0.93, hspace=.001)

        x_values = []
        csvfile.seek(0)
        first_line = True
        for row in reader:
            if first_line == True:
                # Evite la première ligne qui peut être une ligne de titre
                first_line = False
            else:
                x_date = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
                if self.first_date == True:
                    self.first_date = x_date
                x_date = x_date.replace(year=self.first_date.year, month=self.first_date.month, day=self.first_date.day)
                x_values.append(x_date)

        for i in range(self.nb_col):
            y_values = []
            first_y_value = True

            csvfile.seek(0)
            first_line = True
            for row in reader:
                if first_line == True:
                    # Evite la première ligne qui peut être une ligne de titre
                    first_line = False
                else:
                    y_value = float(row[i+1].replace(",", "."))
                    if first_y_value == True:
                        first_y_value = y_value
                    y_value -= first_y_value
                    y_values.append(y_value)
            subplot[i].plot(x_values, y_values, label=filename)

            # Put a legend to the right of the current axis. Set font size
            subplot[i].legend(loc='best', prop={'size': 8})
            subplot[i].grid(True)

        #  use keys 'c', 'i' and mouse middle button for cursors
        self.cursor = Cursor(subplot[0], self.canvas)
        self.fig.canvas.mpl_connect('key_press_event', self.__key)

        self.canvas.draw()

    def do_quit(self):
        plt.close('all')
        self.root.quit()

    def refresh_all(self):
        self.display("refresh_all")

        self.plot_figure()

        # Update window graphics
        self.update()

    @staticmethod
    def about_command():
        tkMessageBox.showinfo("About", "CSV plotter\n\nS. Auray\n20/11/2016")

#########################################################################################################


class Cursor(object):
    # Cursor, crosshair snaps to the nearest point
    # x is assumed to be sorted
    def __init__(self, axes, canvas):
        self.axes = axes
        self.canvas = canvas
        hold = self.axes.ishold()
        self.axes.hold(True)
        # create cursors at minx, miny (not 0, to keep autoscaling)
        minx, _maxx = self.axes.get_xlim()
        miny, _maxy = self.axes.get_ylim()
        self.crossx, = axes.plot((minx, minx), (miny, miny), 'b-', zorder=4)  # the horiz crosshair
        self.crossy, = axes.plot((minx, minx), (miny, miny), 'b-', zorder=4)  # the vert crosshair
        self.ref_crossx, = axes.plot((minx, minx), (miny, miny), 'r-', zorder=4)  # the horiz crosshair (ref cursor)
        self.ref_crossy, = axes.plot((minx, minx), (miny, miny), 'r-', zorder=4)  # the horiz crosshair (ref cursor)
        self.axes.hold(hold)
        self.RefCursorOn = False
        self.annotation = None

    def close(self):
        self.axes.hold(False)

    def mouse_move(self, event):
        if not event.inaxes:
            return

        ax = event.inaxes
        x, y = event.xdata, event.ydata

        # update the line positions
        minx, maxx = ax.get_xlim()
        miny, maxy = ax.get_ylim()
        self.crossx.set_data((minx, maxx), (y, y))
        self.crossy.set_data((x, x), (miny, maxy))

        x_datetime = matplotlib.dates.num2date(x, tz=None)
        if not self.RefCursorOn:
            # absolute position
            x_datetime_print = str(x_datetime)
            y_print = "%.2f" % y
        else:
            # differential measure (comparison to ref)
            x_datetime_print = str(x_datetime - self.ref_x_datetime)
            y_print = "%.2f" % (y - self.ref_y)

        if "day" not in x_datetime_print:
            x_datetime_print = x_datetime_print[x_datetime_print.find(" ")+1:]
        x_datetime_print = x_datetime_print[:x_datetime_print.find(".")]

        if self.annotation != None:
            self.annotation.remove()
        self.annotation = self.axes.annotate(x_datetime_print + "\n" + y_print, xy=(x, y),
                                             xytext=(5, 5), textcoords='offset pixels', fontsize=9)
        self.canvas.draw()

    # Mouse middle click
    def mouse_click(self, event):
        if not event.inaxes:
            return

        if event.button != 2:
            return  # ignore non-button-2 clicks

        ax = event.inaxes
        x, y = event.xdata, event.ydata

        # update reference cursor position
        minx, maxx = ax.get_xlim()
        miny, maxy = ax.get_ylim()
        self.ref_crossx.set_data((minx, maxx), (y, y))
        self.ref_crossy.set_data((x, x), (miny, maxy))
        self.ref_x_datetime = matplotlib.dates.num2date(x, tz=None)
        self.ref_y = y

        self.canvas.draw()
        self.RefCursorOn = True

    def clear_cursors(self):
        # reduce lines to points (within the displayed plot area, to avoid scale modification)
        minx, _maxx = self.axes.get_xlim()
        miny, _maxy = self.axes.get_ylim()
        self.crossx.set_data((minx, minx), (miny, miny))
        self.crossy.set_data((minx, minx), (miny, miny))

        if self.RefCursorOn:
            self.ref_crossx.set_data((minx, minx), (miny, miny))
            self.ref_crossy.set_data((minx, minx), (miny, miny))
            self.RefCursorOn = False

        self.canvas.draw()


if __name__ == '__main__':
    root_window = Tk()
    if window_zoomed == True:
        root_window.state('zoomed')
    else:
        root_window.geometry("800x600")

    app = Application(root_window, title="CSV Plot")
    if os.path.exists('CSVplot.ico'):
        app.winfo_toplevel().iconbitmap('CSVplot.ico')
    app.mainloop()

    plt.close()
