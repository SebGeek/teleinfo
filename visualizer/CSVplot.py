#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import csv
import datetime
import operator

# Tkinter
try:
    from Tkinter import *
    from ScrolledText import *
    import tkMessageBox
except:
    print "To install Tkinter: sudo apt-get install python-tk"
# Matplotlib
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
matplotlib.use('TkAgg')

# - Ajouter curseur
# - sauvegarde derniere conf et recharge au prochain lancement
# - Sélectionner le fichier csv
# - teleinfo: colonnes prix, puissance, HC/HP
# - Ne plas planter et fermer correctement l'appli avec la croix
# - Save figure
# - ajout d'annotation (texte) où on veut

LOG_FRAME = False


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
        self.file_nb = 1
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
        if (str(event.key).endswith("i") and (self.CursorOn)):
            self.__decodePacket(str(self.cursor.pktNumber))
            return
        if (str(event.key).endswith("c") and self.CursorOn) or str(event.key).endswith("escape"):
            #cursors OFF
            self.fig.canvas.mpl_disconnect(self.binding_id_move)
            self.fig.canvas.mpl_disconnect(self.binding_id_click)
            self.cursor.clear_cursors()
            self.CursorOn=False
            return
        if str(event.key).endswith("c") and not(self.CursorOn):
            #cursors ON
            self.binding_id_move = self.fig.canvas.mpl_connect('motion_notify_event', self.cursor.mouse_move)
            self.binding_id_click = self.fig.canvas.mpl_connect('button_press_event', self.cursor.mouse_click)
            self.CursorOn=True
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
            self.Log_frame.grid(row=row_current, column=0, sticky = NSEW, padx=5, pady=5)
            self.Log_frame.columnconfigure(0, weight=1)
            self.textPad = ScrolledText(self.Log_frame, width=110, height=10)
            self.textPad.grid(row=0, column=0)

    def plot_figure(self):

        filename = "log.csv.2016-03-1" + str(self.file_nb)
        self.file_nb += 1
        csvfile = open("../log/" + filename, 'rb')
        reader = csv.reader(csvfile, delimiter=";")

        if self.first_time == True:
            # Read the number of columns
            first_line = csvfile.readline()
            nb_col = first_line.count(";") - 1

            subplot = []
            # "2, 3, 4" means "2x3 grid, 4th subplot1".
            for i in range(nb_col):
                subplot.append(self.fig.add_subplot(nb_col, 1, i+1))

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
        for row in reader:
            x_date = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
            if self.first_date == True:
                self.first_date = x_date
            x_date = x_date.replace(year=self.first_date.year, month=self.first_date.month, day=self.first_date.day)
            x_values.append(x_date)

        for i in range(nb_col):
            y_values = []
            first_y_value = True

            csvfile.seek(0)
            for row in reader:
                if "," in row[1]:
                    y_value = float(row[i+1].replace(",", "."))
                    if first_y_value == True:
                        first_y_value = y_value
                    y_value = y_value - first_y_value
                    y_values.append(y_value)
            subplot[i].plot(x_values, y_values, label=filename)

            # Put a legend to the right of the current axis. Set font size
            subplot[i].legend(loc='best', prop={'size': 8})
            subplot[i].grid(True)

        tt = []
        tt = sorted(tt, key=operator.itemgetter(0))
        xx = map(operator.itemgetter(0), tt)
        yy = map(operator.itemgetter(1), tt)
        nn = map(operator.itemgetter(2), tt)
        zz = map(operator.itemgetter(3), tt)

        #  use keys 'c', 'i' and mouse middle button for cursors
        self.cursor = Cursor(subplot[0], self.canvas, xx, yy, nn, zz)
        _binding_key_press = self.fig.canvas.mpl_connect('key_press_event', self.__key)

        self.canvas.draw()


    def do_quit(self):
        plt.close('all')
        self.root.quit()

    def refresh_all(self):
        self.display("refresh_all")

        self.plot_figure()

        # Update window graphics
        self.update()

    def about_command(self):
        tkMessageBox.showinfo("About", "CSV plotter\n\nS. Auray\n14/11/2016")


class Cursor(object):
    # Cursor, crosshair snaps to the nearest point
    # x is assumed to be sorted
    def __init__(self, axes, canvas, x, y, n, z):
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
        self.x = x
        self.y = y
        self.n = n
        self.z = z
        self.txt = self.axes.title
        self.axes.hold(hold)
        self.RefCursorOn = False
        self.pktNumber = 0

    def close(self):
        self.axes.hold(False)

    def _get_xy(self, x, y):
        """Return `(x_p, y_p, i_p)` for the point nearest `(x, y)`"""
        dist = float("infinity")
        indx = -1
        # calculate scale (depends from zoom factor)
        minx, maxx = self.axes.get_xlim()
        miny, maxy = self.axes.get_ylim()
        xs = maxx - minx
        ys = maxy - miny
        xyzip = zip(self.x, self.y, range(len(self.x)))
        for xp, yp, i in xyzip:
            d = (ys * (x - xp)) ** 2 + (xs * (y - yp)) ** 2
            if d < dist:
                dist = d
                xpm = xp
                ypm = yp
                indx = i
        return (xpm, ypm, indx)

    def mouse_move(self, event):
        if not event.inaxes: return
        ax = event.inaxes
        minx, maxx = ax.get_xlim()
        miny, maxy = ax.get_ylim()
        x, y, i = self._get_xy(event.xdata, event.ydata)
        self.pktNumber = self.n[i]
        z = self.z[i]
        # update the line positions
        self.crossx.set_data((minx, maxx), (y, y))
        self.crossy.set_data((x, x), (miny, maxy))
        # update the label
        if not self.RefCursorOn:
            # absolute position
            self.txt.set_text('pkt={:d}, t={:1.6f}, y={:1.6f}, curve #{:d}'.format(self.n[i], x, y, z))
        else:
            # differential measure (comparison to ref)
            self.txt.set_text('delta t={:1.6f}, delta y={:1.6f}'.format(x - self.ref_x, y - self.ref_y))
        self.canvas.draw()

    def mouse_click(self, event):
        if not event.inaxes:
            return
        if event.button != 2:
            return  # ignore non-button-2 clicks
        ax = event.inaxes
        minx, maxx = ax.get_xlim()
        miny, maxy = ax.get_ylim()
        x, y, i = self._get_xy(event.xdata, event.ydata)
        # update reference cursor position
        self.ref_crossx.set_data((minx, maxx), (y, y))
        self.ref_crossy.set_data((x, x), (miny, maxy))
        self.ref_x = x
        self.ref_y = y
        self.ref_i = i
        self.ref_z = self.z[i]
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
        self.txt.set_text('')
        self.canvas.draw()


if __name__ == '__main__':
    root = Tk()
    root.state('zoomed')

    app = Application(root, title="CSV Plot")
    if os.path.exists('CSVplot.ico'):
        app.winfo_toplevel().iconbitmap('CSVplot.ico')
    app.mainloop()

    print "bye bye 1"
    plt.close()
    print "bye bye 2"