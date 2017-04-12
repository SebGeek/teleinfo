#!/usr/bin/python
# -*- coding:utf-8 -*-

# Matplotlib
import matplotlib
import matplotlib.dates as mdates

#from matplotlib.widgets import Widget

#matplotlib.use('TkAgg')

# - gestion sur plusieurs graphes
# - barre verticale sur tous les graphes
# - annotation

# - si clique gauche, passe en différence avec 2ème barres.
# - si re-clique, revient comme avant

# Volontairement, le curseur n'est pas collé à la courbe, pour que l'utilisateur ait plus de liberté (il n'est pas limité aux points de la courbe)


# class MultiCursor_enhanced(Widget):
#     """
#     Provide a vertical (default) and/or horizontal line cursor shared between
#     multiple axes
#
#     Example usage::
#
#         from matplotlib.widgets import MultiCursor
#         from pylab import figure, show, np
#
#         t = np.arange(0.0, 2.0, 0.01)
#         s1 = np.sin(2*np.pi*t)
#         s2 = np.sin(4*np.pi*t)
#         fig = figure()
#         ax1 = fig.add_subplot(211)
#         ax1.plot(t, s1)
#
#
#         ax2 = fig.add_subplot(212, sharex=ax1)
#         ax2.plot(t, s2)
#
#         multi = MultiCursor(fig.canvas, (ax1, ax2), color='r', lw=1,
#                             horizOn=False, vertOn=True)
#         show()
#
#     """
#     def __init__(self, canvas, axes, useblit=True, horizOn=False, vertOn=True,
#                  **lineprops):
#
#         self.canvas = canvas
#         self.axes = axes
#         self.horizOn = horizOn
#         self.vertOn = vertOn
#
#         self.annotation = None
#
#         xmin, xmax = axes[-1].get_xlim()
#         ymin, ymax = axes[-1].get_ylim()
#         xmid = 0.5 * (xmin + xmax)
#         ymid = 0.5 * (ymin + ymax)
#
#         self.visible = True
#         self.useblit = useblit and self.canvas.supports_blit
#         self.background = None
#         self.needclear = False
#
#         if useblit:
#             lineprops['animated'] = True
#
#         if vertOn:
#             self.vlines = [ax.axvline(xmid, visible=False, **lineprops)
#                            for ax in axes]
#         else:
#             self.vlines = []
#
#         if horizOn:
#             self.hlines = [ax.axhline(ymid, visible=False, **lineprops)
#                            for ax in axes]
#         else:
#             self.hlines = []
#
#         self.canvas.mpl_connect('motion_notify_event', self.onmove)
#         self.canvas.mpl_connect('draw_event', self.clear)
#
#     def clear(self, event):
#         """clear the cursor"""
#         if self.useblit:
#             self.background = (self.canvas.copy_from_bbox(self.canvas.figure.bbox))
#         for line in self.vlines + self.hlines:
#             line.set_visible(False)
#
#     def onmove(self, event):
#         if event.inaxes is None:
#             return
#         if not self.canvas.widgetlock.available(self):
#             return
#         self.needclear = True
#         if not self.visible:
#             return
#         if self.vertOn:
#             for line in self.vlines:
#                 line.set_xdata((event.xdata, event.xdata))
#                 line.set_visible(self.visible)
#                 print event.xdata
#         if self.horizOn:
#             for line in self.hlines:
#                 line.set_ydata((event.ydata, event.ydata))
#                 line.set_visible(self.visible)
#
#         if self.annotation != None:
#             self.annotation.remove()
#         print (event.xdata, event.ydata)
#         self.annotation = event.inaxes.annotate(str(event.xdata) + "\n" + str(event.ydata), xy=(event.xdata, event.ydata),
#                                              xytext=(5, 5), textcoords='offset pixels', fontsize=9)
#
#         self._update()
#
#     def _update(self):
#         if self.useblit:
#             if self.background is not None:
#                 self.canvas.restore_region(self.background)
#             if self.vertOn:
#                 for ax, line in zip(self.axes, self.vlines):
#                     ax.draw_artist(line)
#             if self.horizOn:
#                 for ax, line in zip(self.axes, self.hlines):
#                     ax.draw_artist(line)
#             self.canvas.blit(self.canvas.figure.bbox)
#         else:
#             self.canvas.draw_idle()

####################################################################################

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
