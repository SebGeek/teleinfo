#! /usr/bin/env python
# -*- coding:utf-8 -*-
#############################################
#
# 

import matplotlib
matplotlib.use('TkAgg')
from Tkinter import *
from xml.dom.minidom import parse
import os, operator
import tkFileDialog, inspect
import pylab
from csv_extract import c_Parser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure


class Application(Frame):
    # THE MAIN APPLICATION
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pcapFileName=StringVar()
        self.pcapFileName.set("Z:/teleinfo/log/log.csv.2016-03-15") # Default
        self.inputFileName=""
        self.framesStructureFileNameVar=StringVar()
        self.status=StringVar()
        self.dataSetNames=StringVar()
        self.dataSetDescription=StringVar()
        self.privateIpBase=StringVar()
        self.dataSetParams=StringVar()
        self.paramName=StringVar()
        self.paramTmin=StringVar()
        self.paramTmax=StringVar()
        self.paramSN=StringVar()
        self.dataSetList=[]
        self.framesStructureFileNameVar.set("Frames_Structure.xml")
        self.grid()
        self.__createWidgets()
        self.Parser = c_Parser("")
        self.PlotConfFileName="Plot_Config.xml"
        self.__refreshList()    
        self.update()
        
    def __loadData(self):
        self.status.set("")
        #create parser from .xml configuration file which defines frames structures
        try:
            self.Parser = c_Parser(self.framesStructureFileNameVar.get())
        except:
            return False
        self.master.title(__file__ + " - frames format : " + self.Parser.confFileVersion)
        #parse plot .xml configuration file
        self.dataSetList=[]
        try:
            for Elt in parse(self.PlotConfFileName).documentElement.getElementsByTagName("DataSet"):
                self.dataSetList.append(self.Parser.xmlElt2DataSet(Elt, DataSetParams=self.dataSetParams.get().split(",")))
        except:
            return False
        return True
        
    def __refreshList(self):
        if (self.__loadData()):
            self.status.set("xml configuration files successfully loaded")
        else:
            self.status.set("error while parsing xml configuration file")
        s=""
        for dataSet in self.dataSetList: s = s + dataSet.name.replace(" ","_") + " "
        self.dataSetNames.set("") # to bypass a absence of refresh by Tkinter
        self.dataSetNames.set(s)
        if s:
            self.getdataSetList.selection_clear(1)
            self.getdataSetList.selection_set(0)
            self.dataSetDescription.set(self.dataSetList[0].description)
            self.__updateDataSet(None)
        else: self.dataSetDescription.set("")
        
    def __createWidgets(self):    #graphical definition of the window
        #frames format file name
        self.getFramesStructureFrame = LabelFrame (self, text='frames structure file', padx=2, pady=2)
        self.getFramesStructureFrame.grid()
        self.getFramesStructureFrame.columnconfigure(0, minsize=500)
        self.framesStructureFileNameEntry = Entry( self.getFramesStructureFrame, textvariable = self.framesStructureFileNameVar, width = 70, justify=RIGHT)
        self.framesStructureFileNameEntry.grid(sticky=W, row=0)
        self.getFramesStructureFileNameButton = Button ( self.getFramesStructureFrame, text='Browse...', command=self.__getFramesStructureFileName)
        self.getFramesStructureFileNameButton.grid(sticky=E, row=0)
        #get csv file name
        self.getFileLabelFrame = LabelFrame (self, text='csv file', padx=2, pady=2)
        self.getFileLabelFrame.grid()
        self.getFileLabelFrame.columnconfigure(0, minsize=500)
        self.pcapFileNameEntry = Entry( self.getFileLabelFrame, textvariable = self.pcapFileName, width = 70, justify=RIGHT)
        self.pcapFileNameEntry.grid(sticky=W, row=0)
        self.getFileNameButton = Button ( self.getFileLabelFrame, text='Browse...', command=self.getFileName)
        self.getFileNameButton.grid(sticky=E, row=0)
        self.loadPcapFileButton = Button ( self.getFileLabelFrame, text='Reload file', command=self.__reloadPcapFile)
        self.loadPcapFileButton.grid()
        #Select dataSet
        self.getdataSet = LabelFrame (self, text='Data set', padx=2, pady=2)
        self.getdataSet.grid()
        self.getdataSet.columnconfigure(0, minsize=500)
        self.getdataSetList = Listbox( self.getdataSet , listvariable=self.dataSetNames, height=18)
        self.getdataSetList.grid(sticky=W)
        self.getdataSetList.bind("<ButtonRelease-1>", self.__updateDataSet)
        self.dataSetDescriptionLabel = Label(self.getdataSet, textvariable = self.dataSetDescription, width=50)
        self.dataSetDescriptionLabel.grid(row=0, sticky=E)
        #parameters
        self.getParams = LabelFrame (self, text='Parameters', padx=2, pady=2)
        self.getParams.grid(sticky=W)
        self.getPrivateIpBaseEntry=Entry( self.getParams, textvariable = self.privateIpBase)
        self.getPrivateIpBaseEntry.grid(sticky=W, pady=2, row=0, column=0)
        self.getPrivateIpBaseLabel=Label(self.getParams, text="IPbase")
        self.privateIpBase.set("10.0")
        self.getPrivateIpBaseLabel.grid(row=0, column=1, sticky=W)
        self.getdataSetParamsEntry=Entry( self.getParams, textvariable = self.dataSetParams)
        self.getdataSetParamsEntry.grid(sticky=W, pady=2, row=1, column=0)
        self.getdataSetParamsLabel=Label(self.getParams, textvariable=self.paramName)
        self.getdataSetParamsLabel.grid(row=1, column=1, sticky=W)
        self.getParamTminEntry=Entry( self.getParams, textvariable = self.paramTmin)
        self.getParamTminEntry.grid(sticky=W, pady=2, row=2, column=0)
        self.getParamTminLabel=Label(self.getParams, text="Tmin                 ")
        self.getParamTminLabel.grid(row=2, column=1, sticky=W)
        self.getParamTmaxEntry=Entry( self.getParams, textvariable = self.paramTmax)
        self.getParamTmaxEntry.grid(sticky=W, pady=2, row=3, column=0)
        self.getParamTmaxLabel=Label(self.getParams, text="Tmax")
        self.getParamTmaxLabel.grid(row=3, column=1, sticky=W)
        self.getParamSNEntry=Entry( self.getParams, textvariable = self.paramSN)
        self.getParamSNEntry.grid(sticky=W, pady=2, row=4, column=0)
        self.getParamSNLabel=Label(self.getParams, text="force SN: X,Y")
        self.getParamSNLabel.grid(row=4, column=1, sticky=W)
        #refresh list button
        self.refreshListButton = Button ( self.getdataSet, text='Refresh list', command=self.__refreshList)
        self.refreshListButton.grid()
        #plot
        self.plotButton = Button ( self, text='Plot', command=self.__plot)
        self.plotButton.grid(pady=5)
        self.plotButton.configure(state=DISABLED)
        #Status
        self.statusLabel = Label(self, textvariable = self.status, width = 80, relief=RIDGE, pady=2, height=4, justify=LEFT)
        self.statusLabel.grid()
        #Quit
        self.quitButton = Button ( self, text='Quit', command=self.__quit, padx=5, pady=2)
        self.quitButton.grid()

        
    def addStatus(self, msg):
        #adds one line in box "status" (and shifts others up if necessary)
        if self.status.get()=="":
            self.status.set(msg)
        else:
            statusLines=self.status.get().split("\n")
            statusLines=statusLines[-3:]
            s=""
            for line in statusLines: s = s + line + "\n"
            s=s+msg
            self.status.set(s)
        self.statusLabel.update()
        
    def __updateDataSet(self, event):
        i=int(self.getdataSetList.curselection()[0])
        self.dataSetDescription.set(self.dataSetList[i].description)
        self.paramName.set(self.dataSetList[i].paramName)
        if (self.dataSetList[i].paramName):
            self.getdataSetParamsEntry.configure(state=NORMAL)
        else:
            self.getdataSetParamsEntry.configure(state=DISABLED)
        
    def __reloadPcapFile(self):
        self.status.set("")
        if (self.paramSN):
            self.plotButton.configure(state=NORMAL)
        else:
            self.plotButton.configure(state=DISABLED)
        self.inputFileName = self.pcapFileName.get()
        if (not(self.inputFileName)):
            self.addStatus("No input file selected")
            return False
        #if (not(self.inputFileName.endswith(".csv"))):
        #    self.addStatus("Unknown input file extension")
        #    return False
        self.addStatus("looking for " + self.inputFileName + "...")
        self.plotButton.configure(state=NORMAL)
        return True
    
    def __getFramesStructureFileName(self):
        self.status.set("")
        self.plotButton.configure(state=DISABLED)
        myFormats = [('xml','*.xml')]
        fileName = tkFileDialog.askopenfilename(filetypes=myFormats)
        self.framesStructureFileNameVar.set(fileName)
        self.framesStructureFileNameEntry.xview_moveto(1)
        if (not(fileName)):
            self.addStatus("No frames structure file selected")
            return False
        if (not(fileName.endswith(".xml"))):
            self.addStatus("Unknown frames structure file extension")
            return False
        if (self.__loadData()):
            self.addStatus("Frames structure file parsed successfully")
            self.plotButton.configure(state=NORMAL)
            return True
        self.addStatus("Error while parsing frames structure file")
        return False
        
        self.__loadData()
        return
    
    def __plot(self):
        self.status.set("")
        self.__loadData()
        #try to close plot window (if not already closed by user)
        self.__ClosePlot()
        #get selected DataSet (if any !)
        try:
            i=int(self.getdataSetList.curselection()[0])
        except:
            self.addStatus("No DataSet selected !")
            return
        
        self.addStatus("Extracting data...")
        DataSet=self.dataSetList[i]
        
        #parameters
        _ptmin=_ptmax=-1
        try:
            if(self.paramTmin.get()!=""): _ptmin=int(self.paramTmin.get())
            if(self.paramTmax.get()!=""): _ptmax=int(self.paramTmax.get())
        except:
            self.addStatus("Invalid parameter tmin or tmax")
            return            
        
        #extract data
        self.Parser.openPcap(self.inputFileName)
        extractedData=self.Parser.ExtractData(self.PlotConfFileName, DataSet.name, LinesList=True, DataSetParams=self.dataSetParams.get().split(","), tmin=0, tmax=0)
        if not(extractedData):
            self.addStatus("Data extraction failed, check command window for error message")
            return
        (t,n,y,l) = extractedData
        
        #create window for figure
        self.ap=AppPlot(self.Parser)
        
        #plot
        self.ap.plot(DataSet,t,n,y,l)
        self.addStatus("Done, use keys 'c', 'i' and mouse middle button for cursors")
        
    def getFileName(self):
        #user prompt to select an input file
        myFormats = [('csv','*.csv')]
        self.inputFileName = tkFileDialog.askopenfilename(initialdir=inspect.currentframe(),filetypes=myFormats)
        self.pcapFileName.set(self.inputFileName)
        self.pcapFileNameEntry.xview_moveto(1)
        self.__reloadPcapFile()
        
    def __ClosePlot(self):
        #try to close plot window (if not already closed by user)
        if (hasattr(self, 'ap')):
            try:
                del(self.ap)
            except:
                pass
    def __quit(self):
        self.__ClosePlot()
        sys.exit()


class AppPlot():
    # PLOT APPLICATION in dedicated window
    def __init__(self, parser, master=None):
        self.root = Tk()
        self.root.wm_title("Visualizer")
        self.root.state("zoomed")
        # figure
        self.f = Figure()
        # a tk.DrawingArea
        self.canvas = FigureCanvasTkAgg(self.f, master=self.root)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.root)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        self.root.grid()
        self.CursorOn=False
        self.parser=parser
        self.pktWindows=[]
        self.pktApp=[]

    #TEST
    def __del__(self):
        #close sub window appPckDisplay (if any)
        #try to close window (if not already closed by user)
        for pktWin in self.pktWindows:
            pktWin.destroy()
        for pApp in self.pktApp:
            del(pApp)
        try:
            self.root.destroy()
        except:
            pass

    def mainloop(self):
        self.root.mainloop()
    def __decodePacket(self, pkt):
        #look for packet (dichotomia)
        l1=0
        l2=len(self.lines)-1
        while (l2-l1 > 5):
            l=(l1+l2)/2
            if (int(self.lines[l].split(";")[0]) > int(pkt)):
                l2=l
            else:
                l1=l
        for i in range(l1,l2+1):
            fields = self.lines[i].split(";")
            if (fields[0]==pkt):
                #tkMessageBox.showinfo("Packet #" + fields[0], self.parser.Frame2Text(self.lines[i]))
                #TEST
                #self.pw = Toplevel()
                #self.appPktDisplay = ApplicationPktDisplay(self.pw, self.parser.Frame2Text(self.lines[i]),fields[0], 6)
                #self.appPktDisplay.mainloop()
                self.pktWindows.append(Toplevel())
                self.pktApp.append(ApplicationPktDisplay(self.pktWindows[-1], self.parser.Frame2Text(self.lines[i]),fields[0], 6))
                self.pktApp[-1].mainloop()
                break

    def __key(self, event):
        if (str(event.key).endswith("i") and (self.CursorOn)):
            self.__decodePacket(str(self.cursor.pktNumber))
            return
        if (str(event.key).endswith("c") and self.CursorOn) or str(event.key).endswith("escape"):
            #cursors OFF
            self.f.canvas.mpl_disconnect(self.binding_id_move)
            self.f.canvas.mpl_disconnect(self.binding_id_click)
            self.cursor.clear_cursors()
            self.CursorOn=False
            return
        if str(event.key).endswith("c") and not(self.CursorOn):
            #cursors ON
            self.binding_id_move = self.f.canvas.mpl_connect('motion_notify_event', self.cursor.mouse_move)
            self.binding_id_click = self.f.canvas.mpl_connect('button_press_event', self.cursor.mouse_click)
            self.CursorOn=True
            return

    def plot(self, DataSet, t, n, y, l):
        # TBD
        self.lines = l
        #plot data
        self.f.clf()
        self.axes = self.f.add_subplot(111)
        tt = []
        legende = []
        for i in range(0, len(DataSet.DataList)):
            #plot only non-empty data (to avoid meaningless legend)
            if t[i]:
                self.axes.plot(t[i], y[i], DataSet.DataList[i].PlotStyle)
                legende_str = "#" + str(i) + " " + str(DataSet.DataList[i].FrameType) + " - " + str(DataSet.DataList[i].DataName) + " - "
                
                for k in range(0,len(DataSet.DataList[i].FilterList)):
                    if k > 0:
                        legende_str = legende_str + " and "
                    legende_str = legende_str + str(DataSet.DataList[i].FilterList[k].DataName) + "=" + str(DataSet.DataList[i].FilterList[k].DataValue)
                
                legende.append(legende_str)
                for j in range(len(t[i])):
                    data_xyni = (t[i][j], y[i][j], n[i][j], i)
                    tt.append(data_xyni)
            tt = sorted(tt, key=operator.itemgetter(0))
        xx = map(operator.itemgetter(0), tt)
        yy = map(operator.itemgetter(1), tt)
        nn = map(operator.itemgetter(2), tt)
        zz = map(operator.itemgetter(3), tt)

        self.cursor = Cursor(self.axes, self.canvas, xx, yy, nn, zz)
        _binding_key_press = self.f.canvas.mpl_connect('key_press_event', self.__key)
        
        self.axes.legend(legende, 'upper left', prop={'size':8})
        pylab.show()


###TEST
class ApplicationPktDisplay():
    def __init__(self, pw, pkt, pktNumber, headerLength ,master=None):
        self.w=pw
        #pkt = string, contatenation of 'data_name : data_value\n'
        #header_length enable to distinguish which data is displayed in label / in lists
        #Frame.__init__(self, master)
        #self.master.title("packet #" + str(pktNumber))
        self.dataNamesFiltered=StringVar()
        self.dataValuesFiltered=StringVar()
        self.filterName=StringVar()
        self.pktDescr=StringVar()
        self.w.grid()
        self.__createWidgets()
        #parse pkt
        l=[x.split(" : ") for x in pkt.split("\n")]
        l=l[:-1]
        self.dataNames=[x[0] for x in l]
        self.dataValues=[x[1].replace(" ","") for x in l]   #replace : for enums, ex "Master (1)"
        #header
        desc=""
        for i in range(headerLength):
            desc = desc + self.dataNames[i] + " : " + self.dataValues[i] + "\n"
        self.pktDescr.set(desc)
        self.dataNames=self.dataNames[headerLength:]
        self.dataValues=self.dataValues[headerLength:]
        self.__apply_filter()
        self.w.update()

    #TEST
    def __del__(self):
        #close window, if not already closed by user
        try:
            self.w.destroy()
        except:
            pass

    def mainloop(self):
        self.w.mainloop()         
    def __scrollLists(self,*args):  #to scroll the 2 lists with 1 scrollbar
        self.dataNamesList.yview(*args)
        self.dataValuesList.yview(*args)
    def __apply_filter(self,*args):
        self.dataNamesFiltered.set("") # to bypass a absence of refresh by Tkinter
        self.dataValuesFiltered.set("")
        n=""
        v=""
        for i in range(len(self.dataNames)):
            if (self.filterName.get() in self.dataNames[i]):
                n = n + self.dataNames[i] + " "
                v = v + self.dataValues[i]+ " "
        self.dataNamesFiltered.set(n)
        self.dataValuesFiltered.set(v)
    def __createWidgets(self):
        #header
        self.pktLabel = Label(self.w, textvariable = self.pktDescr, width = 40, anchor=NW, padx=2, pady=2, justify=LEFT) #", relief=RIDGE, pady=2, height=4)
        self.pktLabel.grid(sticky=W)
        self.filterEntry = Entry(self.w, textvariable = self.filterName, width=40)
        self.filterEntry.bind("<KeyRelease>", self.__apply_filter)
        self.filterEntry.grid(sticky=W)
        self.filterEntry.focus_set()
        #data names & values lists
        self.dataListFrame = LabelFrame (self.w, text='frame content')#, padx=2, pady=2)
        self.dataListFrame.grid()
        self.dataListFrame.columnconfigure(0, minsize=180)
        self.yScroll = Scrollbar(self.dataListFrame, orient=VERTICAL)
        self.yScroll.grid(row=0,column=2,sticky=N+S)
        self.dataNamesList = Listbox(self.dataListFrame , listvariable=self.dataNamesFiltered, height=20, width=30, yscrollcommand=self.yScroll.set)
        self.dataNamesList.grid(row=0, column=0) #sticky=W)
        self.dataValuesList = Listbox(self.dataListFrame , listvariable=self.dataValuesFiltered, height=20, width=30, yscrollcommand=self.yScroll.set)
        self.dataValuesList.grid(row=0, column=1)
        self.yScroll["command"] = self.__scrollLists #self.dataNamesList.yview



class Cursor (object):
    # Cursor, crosshair snaps to the nearest point
    # x is assumed to be sorted
    def __init__(self, axes, canvas, x, y, n, z):
        self.axes = axes
        self.canvas = canvas
        hold = self.axes.ishold()
        self.axes.hold(True)
        #create cursors at minx, miny (not 0, to keep autoscaling)
        minx,_maxx = self.axes.get_xlim()
        miny,_maxy = self.axes.get_ylim()
        self.crossx, = axes.plot((minx,minx), (miny,miny), 'b-', zorder=4)  # the horiz crosshair
        self.crossy, = axes.plot((minx,minx), (miny,miny), 'b-', zorder=4)  # the vert crosshair
        self.ref_crossx, = axes.plot((minx,minx), (miny,miny), 'r-', zorder=4)  # the horiz crosshair (ref cursor)
        self.ref_crossy, = axes.plot((minx,minx), (miny,miny), 'r-', zorder=4)  # the horiz crosshair (ref cursor)
        self.x = x
        self.y = y
        self.n = n
        self.z = z
        self.txt = self.axes.title
        self.axes.hold(hold)
        self.RefCursorOn=False
        self.pktNumber=0

    def close(self):
        self.axes.hold(False)
        
    def _get_xy(self, x, y):
        """Return `(x_p, y_p, i_p)` for the point nearest `(x, y)`"""
        dist = float("infinity")
        indx = -1
        #calculate scale (depends from zoom factor)
        minx,maxx = self.axes.get_xlim()
        miny,maxy = self.axes.get_ylim()
        xs = maxx-minx
        ys = maxy-miny
        xyzip=zip(self.x, self.y,range(len(self.x)))
        for xp,yp,i in xyzip:
            d = (ys*(x-xp))**2 + (xs*(y-yp))**2
            if d < dist:
                dist = d
                xpm = xp
                ypm = yp
                indx = i
        return (xpm,ypm,indx)

    def mouse_move(self, event):
        if not event.inaxes: return
        ax = event.inaxes
        minx,maxx = ax.get_xlim()
        miny,maxy = ax.get_ylim()
        x,y,i = self._get_xy(event.xdata, event.ydata)
        self.pktNumber=self.n[i]
        z = self.z[i]
        # update the line positions
        self.crossx.set_data((minx, maxx), (y, y))
        self.crossy.set_data((x, x), (miny, maxy))
        # update the label
        if not self.RefCursorOn:
            #absolute position
            self.txt.set_text('pkt={:d}, t={:1.6f}, y={:1.6f}, curve #{:d}'.format(self.n[i], x, y, z))
        else:
            #differential measure (comparison to ref)
            self.txt.set_text('delta t={:1.6f}, delta y={:1.6f}'.format(x-self.ref_x, y-self.ref_y))
        self.canvas.draw()

    def mouse_click(self, event):
        if not event.inaxes:
            return
        if event.button != 2:
            return # ignore non-button-2 clicks
        ax = event.inaxes
        minx,maxx = ax.get_xlim()
        miny,maxy = ax.get_ylim()
        x,y,i = self._get_xy(event.xdata, event.ydata)
        #update reference cursor position
        self.ref_crossx.set_data((minx, maxx), (y, y))
        self.ref_crossy.set_data((x, x), (miny, maxy))
        self.ref_x = x
        self.ref_y = y
        self.ref_i = i
        self.ref_z = self.z[i]
        self.canvas.draw()
        self.RefCursorOn=True
        
    def clear_cursors(self):
        #reduce lines to points (within the displayed plot area, to avoid scale modification)
        minx,_maxx = self.axes.get_xlim()
        miny,_maxy = self.axes.get_ylim()
        self.crossx.set_data((minx,minx),(miny,miny))
        self.crossy.set_data((minx,minx),(miny,miny))
        if self.RefCursorOn:
            self.ref_crossx.set_data((minx,minx),(miny,miny))
            self.ref_crossy.set_data((minx,minx),(miny,miny))
            self.RefCursorOn=False
        self.txt.set_text('')
        self.canvas.draw()


app = Application()
if (os.path.exists('chart_curve.ico')):
    app.winfo_toplevel().iconbitmap('chart_curve.ico')
app.mainloop()
