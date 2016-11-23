#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import csv
import datetime
import inspect

# Tkinter
from Tkinter import *
import tkMessageBox
import tkFileDialog

# Matplotlib
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from cursor import Cursor
matplotlib.use('TkAgg')

window_zoomed = True
request_file = True
#request_file = "Z:/teleinfo/log/log.csv.2016-11-19"
delimiter_def = ";"

# Use key 'c' to activate cursor
# Use mouse middle button for a second cursor to show difference

# - cas où la premiere colonne n'est pas une date
# - prise en compte de la premiere ligne pour poser label des axes Y
# - unité suivant ligne de titre entre parentheses
# - curseur sur tous les graphs
# - espace (petit) entre les subplots
# - annotation: appui sur touche 'a' puis ajoute une colonne dans le CSV

# - visualizer: premiere ligne avec titre/unites

# Fonctions:
# compatible Linux/Windows


class Application(Frame):
    def __init__(self, root, title):
        self.root = root
        Frame.__init__(self, self.root)
        self.root.title(title)

        # Menu
        menu = Menu(self.root)
        self.root.config(menu=menu)

        menu1 = Menu(menu, tearoff=False)
        menu.add_cascade(label="Fichier", menu=menu1)
        menu1.add_command(label="Charger CSV", command=self.load_CSV)
        menu1.add_command(label="Quitter", command=self.do_quit)

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

    @staticmethod
    def display(msg):
        print msg

    def __key(self, event):
        if str(event.key).endswith("c"):
            if self.CursorOn:
                # cursors OFF
                self.fig.canvas.mpl_disconnect(self.binding_id_move)
                self.fig.canvas.mpl_disconnect(self.binding_id_click)
                self.cursor.clear_cursors()
                self.CursorOn = False
            else:
                # cursors ON
                self.binding_id_move = self.fig.canvas.mpl_connect('motion_notify_event', self.cursor.mouse_move)
                self.binding_id_click = self.fig.canvas.mpl_connect('button_press_event', self.cursor.mouse_click)
                self.CursorOn = True

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
        if not os.name == "posix":
            toolbar = NavigationToolbar2TkAgg(self.canvas, self.root)
            toolbar.grid(row=row_current, column=0, sticky="nw")

        self.plot_figure()

    def plot_figure(self):
        if request_file == True:
            filename = tkFileDialog.askopenfilename(initialdir=inspect.currentframe())
        else:
            filename = request_file
        csvfile = open(filename, 'rb')
        reader = csv.reader(csvfile, delimiter=delimiter_def)

        if self.first_time == True:
            # Read the number of columns
            first_line = csvfile.readline()
            self.nb_col = first_line.count(delimiter_def)

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

        self.cursor = Cursor(subplot, self.canvas)
        self.fig.canvas.mpl_connect('key_press_event', self.__key)

        self.canvas.draw()

    def do_quit(self):
        plt.close('all')
        self.root.quit()

    def load_CSV(self):
        self.display("load_CSV")

        self.plot_figure()

        # Update window graphics
        self.update()

    @staticmethod
    def about_command():
        tkMessageBox.showinfo("About", "CSV plotter\n\nS. Auray\n20/11/2016")


if __name__ == '__main__':
    root_window = Tk()
    if window_zoomed == True:
        w, h = root_window.winfo_screenwidth(), root_window.winfo_screenheight()
        root_window.geometry("%dx%d+0+0" % (w, h))
    else:
        root_window.geometry("800x600")

    app = Application(root_window, title="CSV Plot")

    if not os.name == "posix":
        if os.path.exists('CSVplot.ico'):
            app.winfo_toplevel().iconbitmap('CSVplot.ico')
    app.mainloop()

    plt.close()
