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

window_zoomed = False
request_file = True
#request_file = "../log/After_Simulation_TU4_CRS1.csv"
#request_file = "../log/log.csv.2016-11-23"
#request_file = "Z:/teleinfo/log/log.csv.2016-11-19"


# - menu qui indique les colonnes affichées, que l'on peut cacher
# - choix d'avoir la premiere colonne des Y mise à 0
# - zoom sur un graph qui zoome les autres
# - curseur sur tous les graphs, avec barre des Y qui est sur tous les graphs
# - curseur qui apparait mal
# - annotation: appui sur touche 'a' puis ajoute une colonne dans le CSV

# Fonctions:
# compatible Linux/Windows
# gère première colonne en format date si respecte "%Y-%m-%d %H:%M:%S.%f"
# Use key 'c' to activate cursor
# Use mouse middle button for a second cursor to show difference


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

        self.plot_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Plot", menu=self.plot_menu)

        help_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.about_command)

        # Main window
        self.very_first_time = True
        self.first_x_value = True
        self.CursorOn = False

        self.filename_list = []
        self.y_axis_remove = []
        self.load_CSV()

    @staticmethod
    def display(msg):
        print msg

    def key_press(self, event):
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

    def create_widgets(self):
        # Define a weight for automatic resize of components
        self.root.columnconfigure(0, weight=1)
        row_current = 0

        # Plot frame
        plt.clf() # clear figure
        self.fig = plt.figure(figsize=(5, 4), dpi=100)
        self.root.rowconfigure(row_current, weight=1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas._tkcanvas.config(background='white', borderwidth=0, highlightthickness=0)
        self.canvas.get_tk_widget().grid(row=row_current, column=0, sticky="nsew")
        if not os.name == "posix":
            toolbar = NavigationToolbar2TkAgg(self.canvas, self.root)
            toolbar.grid(row=row_current, column=0, sticky="nw")

    def plot_figure(self):
        print "self.filename_list", self.filename_list
        print "self.y_axis_remove", self.y_axis_remove
        first_time = True
        for filename in self.filename_list:
            # Detect delimiter
            csvfile = open(filename, 'rb')
            first_line = csvfile.readline()
            if ";" in first_line:
                delimiter_def = ";"
            elif "," in first_line:
                delimiter_def = ","
            else:
                delimiter_def = ""
                print "Unknown delimiter: must be ; or ,"

            if first_time == True:
                first_time = False

                # Detect the number of columns (reading first line) and read the titles
                csvfile.seek(0)
                first_line = csvfile.readline().replace("\n", "").replace("\r", "")
                list_titles = first_line.split(delimiter_def)
                last_column_empty = 0
                if list_titles[-1].strip() == "":
                    last_column_empty = 1
                self.nb_col = len(list_titles) - last_column_empty - 1 # do not count the first column (x axis)

                # Detect the type of value in first column (reading second line)
                second_line = csvfile.readline().split(delimiter_def)
                try:
                    datetime.datetime.strptime(second_line[0], "%Y-%m-%d %H:%M:%S.%f")
                except:
                    self.x_value_type = "float"
                else:
                    self.x_value_type = "date"

                self.subplot = []
                for i in range(self.nb_col):
                    # (nb_columns, nb_lines, position)
                    self.subplot.append(self.fig.add_subplot(self.nb_col, 1, i+1))

                    # format the x ticks
                    if self.x_value_type == "date":
                        format_ticks = mdates.DateFormatter('%H')
                        self.subplot[i].xaxis.set_major_locator(mdates.HourLocator())
                        self.subplot[i].xaxis.set_major_formatter(format_ticks)

                    val = list_titles[i + 1].decode("utf-8").encode("ascii", "replace")
                    self.subplot[i].set_ylabel(val, fontsize='small')

                    if self.very_first_time == True:
                        self.plot_menu.add_checkbutton(label=val, command=lambda subplot_nb=i: self.show_subplot(subplot_nb))

                # Labels
                plt.xlabel(list_titles[0], fontsize='small')

                plt.subplots_adjust(left=0.08, right=0.99, bottom=0.08, top=0.93, hspace=.15)

            self.very_first_time = False

            # Read X values
            x_values = []
            csvfile.seek(0)
            first_line = True
            reader = csv.reader(csvfile, delimiter=delimiter_def)
            for row in reader:
                if first_line == True:
                    # Evite la première ligne qui peut être une ligne de titre
                    first_line = False
                else:
                    if self.x_value_type == "date":
                        try:
                            x_value = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
                        except:
                            self.display("error, not a date value (%Y-%m-%d %H:%M:%S.%f): " + row[0])
                    else:
                        x_value = float(row[0].replace(",", "."))

                    if self.first_x_value == True:
                        self.first_x_value = x_value
                    if self.x_value_type == "date":
                        # Remove year/month/day information to display on 24h
                        x_value = x_value.replace(year=self.first_x_value.year, month=self.first_x_value.month, day=self.first_x_value.day)

                    x_values.append(x_value)

            # Read Y values and plot
            y_col_to_plot = range(self.nb_col)
            for y_axis in self.y_axis_remove:
                y_col_to_plot.remove(y_axis)
            self.first_y_value = True
            for y_col in y_col_to_plot:
                y_values = []
                csvfile.seek(0)
                first_line = True
                for row in reader:
                    if first_line == True:
                        # Avoid first line which can be a title
                        first_line = False
                    else:
                        try:
                            y_value = float(row[y_col + 1].replace(",", "."))
                        except:
                            self.display("error, not a float value: " + row[y_col + 1])
                            y_values.append(0.0)
                        else:
                            if y_col == 0:
                                # First y column has its values starting from origin
                                if self.first_y_value == True:
                                    self.first_y_value = y_value
                                y_value -= self.first_y_value
                            y_values.append(y_value)
                self.subplot[y_col].plot(x_values, y_values, label=os.path.basename(filename))

                # Put a legend to the right of the current axis. Set font size
                self.subplot[y_col].legend(loc='best', prop={'size': 8})
                self.subplot[y_col].grid(True)
                for tick in self.subplot[y_col].xaxis.get_major_ticks():
                    tick.label.set_fontsize(8)
                for tick in self.subplot[y_col].yaxis.get_major_ticks():
                    tick.label.set_fontsize(8)

            self.cursor = Cursor(self.subplot, self.canvas, self.x_value_type)
            self.fig.canvas.mpl_connect('key_press_event', self.key_press)

            # Update window graphics
            self.canvas.draw()
            self.update()

    def do_quit(self):
        plt.close('all')
        self.root.quit()

    def load_CSV(self):
        if request_file == True:
            filename = tkFileDialog.askopenfilename(initialdir=inspect.currentframe())
        else:
            filename = request_file
        self.filename_list.append(filename)

        self.create_widgets()
        self.plot_figure()

    def show_subplot(self, subplot_nb):
        self.y_axis_remove.append(subplot_nb)

        self.create_widgets()
        self.plot_figure()

    @staticmethod
    def about_command():
        tkMessageBox.showinfo("About", "CSV plotter\n\nS. Auray\n20/11/2016")


if __name__ == '__main__':
    root_window = Tk()
    if window_zoomed == True:
        if os.name == "posix":
            w, h = root_window.winfo_screenwidth(), root_window.winfo_screenheight()
            root_window.geometry("%dx%d+0+0" % (w, h))
        else:
            root_window.state('zoomed')
    else:
        root_window.geometry("800x600")

    app = Application(root_window, title="CSV Plot")

    if not os.name == "posix":
        if os.path.exists('CSVplot.ico'):
            app.winfo_toplevel().iconbitmap('CSVplot.ico')
    app.mainloop()

    plt.close()
