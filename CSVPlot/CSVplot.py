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
# from cursor import Cursor
matplotlib.use('TkAgg')

window_zoomed = False
request_file = True
#request_file = ("../log/Classeur1.csv", )
#request_file = ("../log/log.csv.2016-11-26", )
#request_file = ("../log/cpu_end_mem_stats.log", )
#request_file = ("../log/Dashboard_endur_2015_12_09_01-44-10_max_cpu_load.csv", )


class Application(Frame):
    def __init__(self, root, title):
        self.root = root
        Frame.__init__(self, self.root)
        self.root.title(title)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        # Menu
        menu = Menu(self.root)
        self.root.config(menu=menu)

        self.menu_file = Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=self.menu_file)
        self.menu_file.add_command(label="Load CSV", command=self.load_CSV)
        self.menu_file.add_separator()

        self.plot_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Plot", menu=self.plot_menu)

        help_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.about_command)

        # Main window
        self.very_first_time = True
        self.create_menu_over_24h_once = True
        self.create_menu_unselect_all_plots_once = True
        self.first_x_value = True
        self.x_value_type = "to be detected"
        # self.CursorOn = False
        # self.cursor = None

        self.filename_list = []
        self.show_filename_var = {}
        self.show_subplot_var = []
        self.load_CSV()

    @staticmethod
    def display(msg):
        print msg

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

        toolbar_frame = Frame(self.root)
        NavigationToolbar2TkAgg(self.canvas, toolbar_frame)
        toolbar_frame.grid(row=row_current, column=0, sticky="nw")

    def plot_figure(self):
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
                self.display("Unknown delimiter: must be ; or ,")

            if first_time == True:
                first_time = False

                # Detect the number of columns (reading first line) and read the titles
                csvfile.seek(0)
                first_line = csvfile.readline().replace("\n", "").replace("\r", "")
                list_titles = first_line.split(delimiter_def)
                last_column_empty = 0
                if list_titles[-1].strip() == "":
                    last_column_empty = 1
                nb_col = len(list_titles) - last_column_empty - 1 # do not count the first column (x axis)

                if self.very_first_time == True:
                    self.y_col_to_plot = range(nb_col)
                nb_col = len(self.y_col_to_plot)

                if self.x_value_type != "forced":
                    # Detect the type of value in first column (reading second line)
                    second_line = csvfile.readline().split(delimiter_def)
                    try:
                        datetime.datetime.strptime(second_line[0], "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        self.x_value_type = "float"
                    else:
                        self.x_value_type = "date"

                self.subplot = []
                for subplot_idx, y_col in enumerate(self.y_col_to_plot):
                    # (nb_columns, nb_lines, position)
                    self.subplot.append(self.fig.add_subplot(nb_col, 1, subplot_idx+1))

                    # format the x ticks
                    if self.x_value_type == "date":
                        format_ticks = mdates.DateFormatter('%H')
                        self.subplot[subplot_idx].xaxis.set_major_locator(mdates.HourLocator())
                        self.subplot[subplot_idx].xaxis.set_major_formatter(format_ticks)

                    val = list_titles[y_col + 1].decode("utf-8").encode("ascii", "replace")
                    self.subplot[subplot_idx].set_ylabel(val, fontsize='small')

                    if self.very_first_time == True:
                        if self.x_value_type == "date":
                            if self.create_menu_over_24h_once == True:
                                self.create_menu_over_24h_once = False
                                self.over_24h = BooleanVar()
                                self.over_24h.set(False)
                                self.plot_menu.add_checkbutton(label="x-axis over 24h / y-axis offset to 0",
                                                               variable=self.over_24h, command=self.update_graph)

                        if self.create_menu_unselect_all_plots_once == True:
                            self.create_menu_unselect_all_plots_once = False
                            self.plot_menu.add_command(label="First column is not a X-axis", command=self.first_column_is_not_x_axis)
                            self.plot_menu.add_separator()
                            self.plot_menu.add_command(label="Unselect all plots", command=self.unselect_all_plots)
                            self.plot_menu.add_command(label="Draw plots", command=self.update_graph)
                            self.plot_menu.add_separator()

                        self.show_subplot_var.append(IntVar())
                        self.show_subplot_var[-1].set(1)
                        self.plot_menu.add_checkbutton(label=val, variable=self.show_subplot_var[-1],
                                                       command=lambda subplot_nb=subplot_idx: self.show_subplot(subplot_nb))
                # Labels
                plt.xlabel(list_titles[0], fontsize='small')

                plt.subplots_adjust(left=0.08, right=0.99, bottom=0.08, top=0.93, hspace=.15)

            self.very_first_time = False

            # Read X values
            x_values = []
            line_number = 0
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
                        try:
                            x_value = float(row[0].replace(",", "."))
                        except:
                            self.display("Error in row: " + str(row))
                            raise

                    if self.first_x_value == True:
                        self.first_x_value = x_value

                    if self.x_value_type == "date":
                        if self.over_24h.get() == True:
                            # Remove year/month/day information to display on 24h
                            x_value = x_value.replace(year=self.first_x_value.year, month=self.first_x_value.month, day=self.first_x_value.day)

                    if self.x_value_type == "forced":
                        x_values.append(line_number)
                        line_number += 1
                    else:
                        x_values.append(x_value)

            # Read Y values and plot
            self.first_y_value = True
            for subplot_idx, y_col in enumerate(self.y_col_to_plot):
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
                                if self.x_value_type == "date":
                                    if self.over_24h.get() == True:
                                        y_value -= self.first_y_value
                            y_values.append(y_value)
                self.subplot[subplot_idx].plot(x_values, y_values, label=os.path.basename(filename))

                # Put a legend on the current axis. Set font size
                self.subplot[subplot_idx].legend(loc='best', prop={'size': 8})
                self.subplot[subplot_idx].grid(True)
                for tick in self.subplot[subplot_idx].xaxis.get_major_ticks():
                    tick.label.set_fontsize(8)
                for tick in self.subplot[subplot_idx].yaxis.get_major_ticks():
                    tick.label.set_fontsize(8)

                # Detect if user has zoomed on a plot
                self.subplot[subplot_idx].callbacks.connect('xlim_changed', self.ax_update)

        # if self.subplot != []:
        #     if self.cursor != None:
        #         self.cursor.close()
        #         self.cursor = None
        #     self.cursor = Cursor(self.subplot, self.canvas, self.x_value_type)
        #     self.fig.canvas.mpl_connect('key_press_event', self.key_press)

    def ax_update(self, ax):
        x_lim = ax.get_xlim()

        # To avoid a recusivity problem, apply new X axis limits on others plots, not itself
        for subplot in self.subplot:
            if x_lim != subplot.get_xlim():
                subplot.set_xlim(x_lim)

    # def key_press(self, event):
    #     if str(event.key).endswith("c"):
    #         if self.CursorOn:
    #             # cursors OFF
    #             self.fig.canvas.mpl_disconnect(self.binding_id_move)
    #             self.fig.canvas.mpl_disconnect(self.binding_id_click)
    #             self.cursor.clear_cursors()
    #             self.CursorOn = False
    #         else:
    #             # cursors ON
    #             self.binding_id_move = self.fig.canvas.mpl_connect('motion_notify_event', self.cursor.mouse_move)
    #             self.binding_id_click = self.fig.canvas.mpl_connect('button_press_event', self.cursor.mouse_click)
    #             self.CursorOn = True

    def quit(self):
        plt.close('all')
        self.root.quit()
        self.root.destroy()  # this is necessary on Windows to prevent: "Fatal Python Error: PyEval_RestoreThread: NULL tstate"

    def load_CSV(self):
        if request_file == True:
            filename_list_str = tkFileDialog.askopenfilenames(initialdir=inspect.currentframe())
            filename_list_new = self.root.splitlist(filename_list_str)
        else:
            filename_list_new = request_file

        if filename_list_new != []:
            for filename in filename_list_new:
                self.show_filename_var[filename] = IntVar()
                self.show_filename_var[filename].set(1)
                self.menu_file.add_checkbutton(label=filename, variable=self.show_filename_var[filename],
                                               command=lambda file_name=filename: self.show_filename(file_name))

            self.filename_list += filename_list_new
            self.update_graph()

    def update_graph(self):
        self.create_widgets()
        if self.filename_list != []:
            self.plot_figure()

        # Redraw window graphics
        self.canvas.draw()
        self.update()

    def show_filename(self, file_name):
        if self.show_filename_var[file_name].get() == 0:
            # not checked
            self.filename_list.remove(file_name)
        else:
            # checked
            self.filename_list.append(file_name)
        self.update_graph()

    def show_subplot(self, subplot_nb):
        if self.show_subplot_var[subplot_nb].get() == 0:
            # not checked
            self.y_col_to_plot.remove(subplot_nb)
        else:
            # checked
            self.y_col_to_plot.append(subplot_nb)
            self.y_col_to_plot = sorted(self.y_col_to_plot)

    def unselect_all_plots(self):
        self.y_col_to_plot = []
        for subplot in self.show_subplot_var:
            subplot.set(0)

    def first_column_is_not_x_axis(self):
        self.x_value_type = "forced"
        self.update_graph()

    @staticmethod
    def about_command():
        tkMessageBox.showinfo("A propos", '''
        CSV plotter

Auteur: S. Auray - Version du 18/01/2017

Fonctions:
- Compatible Linux & Windows
- Ouverture de plusieurs fichiers à la fois
- Détection du type de séparateur dans le fichier
- Gère première colonne en format date si respecte "%Y-%m-%d %H:%M:%S.%f"
  sinon utilise en flottant
  sinon possibilité d'utiliser "First column is not X-axis"

A venir:
- curseur sur tous les graphs, avec barre des Y qui est sur tous les graphs
- Use key 'c' to activate cursor
- Use mouse middle button for a second cursor to show difference
''')


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
