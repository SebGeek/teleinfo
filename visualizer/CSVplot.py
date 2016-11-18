#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import csv

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
matplotlib.use('TkAgg')

# - Axe X: afficher l'heure, sans la date
# - Ajouter curseur
# - Ne plas planter et fermer correctement l'appli avec la croix
# - Sélectionner le fichier csv


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
        self.__create_widgets()

        # Update window graphics
        self.update()

    def display(self, msg):
        if LOG_FRAME == True:
            self.textPad.insert('insert', msg + "\n")
            self.textPad.see('end')

        print msg

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
        with open("../log/" + filename, 'rb') as csvfile:
            self.file_nb += 1
            reader = csv.reader(csvfile, delimiter=";")

            x_values = []
            y_values = []
            index = 0
            for row in reader:
                if "," in row[1]:
                    x_values.append(index)
                    y_values.append(float(row[1].replace(",", ".")))
                    index += 1

        # "234" means "2x3 grid, 4th subplot".
        subplot = self.fig.add_subplot(4, 1, self.file_nb)
        subplot.plot(x_values, y_values, label=filename)

        subplot.grid(True)
        if self.first_time == True:
            #self.first_time = False
            # Shrink current axis by 20% to let some place for the legend at right
            box = subplot.get_position()
            subplot.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis. Set font size
        subplot.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})

        plt.xlabel("Date")
        plt.ylabel("Puissance (Watt)")

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
        tkMessageBox.showinfo("About", "Teleinfo visualizer\n\nS. Auray\n14/11/2016")


if __name__ == '__main__':
    root = Tk()
    root.geometry("800x600")

    app = Application(root, title="CSV Plot")
    if os.path.exists('CSVplot.ico'):
        app.winfo_toplevel().iconbitmap('CSVplot.ico')
    app.mainloop()

    print "bye bye 1"
    plt.close()
    print "bye bye 2"