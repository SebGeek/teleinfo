#!/usr/bin/python
# -*- coding:utf-8 -*-

# Matplotlib
import matplotlib
import matplotlib.dates as mdates
matplotlib.use('TkAgg')


class Cursor(object):

    def __init__(self, axes_list, canvas, x_value_type):
        self.axes_list = axes_list
        self.canvas = canvas
        self.x_value_type = x_value_type

        self.axes = self.axes_list[0]
        hold = self.axes.ishold()
        self.axes.hold(True)

        # create cursors at minx, miny (not 0, to keep autoscaling)
        minx, _maxx = self.axes.get_xlim()
        miny, _maxy = self.axes.get_ylim()

        #self.axes_list
        self.crossx,     = self.axes.plot((minx, minx), (miny, miny), 'b-', zorder=4)  # the horiz crosshair
        self.crossy,     = self.axes.plot((minx, minx), (miny, miny), 'b-', zorder=4)  # the vert crosshair
        self.ref_crossx, = self.axes.plot((minx, minx), (miny, miny), 'r-', zorder=4)  # the horiz crosshair (ref cursor)
        self.ref_crossy, = self.axes.plot((minx, minx), (miny, miny), 'r-', zorder=4)  # the horiz crosshair (ref cursor)

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

        if self.x_value_type == "date":
            x_convert = matplotlib.dates.num2date(x, tz=None)
        else:
            x_convert = x

        if not self.RefCursorOn:
            # absolute position
            x_print = str(x_convert)
            y_print = "%.2f" % y
        else:
            # differential measure (comparison to ref)
            x_print = str(x_convert - self.ref_x_convert)
            y_print = "%.2f" % (y - self.ref_y)

        if self.x_value_type == "date":
            if "day" not in x_print:
                x_print = x_print[x_print.find(" ")+1:]
            x_print = x_print[:x_print.find(".")]

        if self.annotation != None:
            self.annotation.remove()
        self.annotation = self.axes.annotate(x_print + "\n" + y_print, xy=(x, y),
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

        if self.x_value_type == "date":
            self.ref_x_convert = matplotlib.dates.num2date(x, tz=None)
        else:
            self.ref_x_convert = x
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
    pass
