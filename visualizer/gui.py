#!/usr/bin/python
# -*- coding:utf-8 -*-

import Tkinter # To install Tkinter:  sudo apt-get install python-tk
from tkMessageBox import *
import cPickle

class Gui():
    
    def __init__(self, gui_root = None, dryrun = False):
        self.value_selected = None
        self.dryrun = dryrun
        if self.dryrun == True:
            self.selected_button = "ok"
        else:
            self.selected_button = None

        if gui_root == None:
            self.root = Tkinter.Tk()
            self.root.withdraw() # Hide the root window
        else:
            self.root = gui_root
    
    def CurSelect(self, evt):
        if self.dryrun == False:
            self.value_selected = self.l1.get(self.l1.curselection())
    
    def gui_list(self, title_name, list_to_display):
        if self.dryrun == False:

            self.root.title(title_name)
            f1 = Tkinter.Frame(self.root) 
            s1 = Tkinter.Scrollbar(f1) 
            self.l1 = Tkinter.Listbox(f1,width=60,height=10,font=('Alstom',13))
            for i,item in enumerate(list_to_display):
                self.l1.insert(i, item)
            s1.config(command = self.l1.yview) 
            self.l1.config(yscrollcommand = s1.set) 
            self.l1.bind('<<ListboxSelect>>',self.CurSelect)
            self.quitButton = Tkinter.Button(f1, text='OK', command=self.root.destroy)
            self.quitButton.pack(side = Tkinter.BOTTOM, fill = Tkinter.X)
            self.l1.pack(side = Tkinter.LEFT, fill = Tkinter.BOTH) 
            s1.pack(side = Tkinter.RIGHT, fill = Tkinter.Y) 
            f1.pack(fill = Tkinter.BOTH)
            self.root.update_idletasks()
            # get screen width and height
            ws = self.root.winfo_screenwidth() # width of the screen
            hs = self.root.winfo_screenheight() # height of the screen
            size = tuple(int(_) for _ in self.root.geometry().split('+')[0].split('x'))
            x = ws/2 - size[0]/2
            y = hs/2 - size[1]/2
            # set the dimensions of the screen 
            # and where it is placed
            self.root.geometry("%dx%d+%d+%d" % (size + (x, y)))

            self.root.wait_window()
    
    def CurSelect_Multiple(self, evt):
        if self.dryrun == False:
            for i in range(len(self.l1)):
                if self.l1[i] == evt.widget:
                    if len(self.l1[i].curselection()) == 1:
                        self.value_selected[i] = self.l1[i].get(self.l1[i].curselection())
                    else:
                        self.value_selected[i] = []
                        for elem in self.l1[i].curselection():
                            self.value_selected[i].append(self.l1[i].get(elem))
    
    def gui_multiple_list(self, title_name, list_to_display, allow_multiple_selection = False, list_to_select = None,
                          save_selection = None):

        # If a previous selection was saved, take it
        if save_selection != None:
            try:
                fd_file = open(save_selection, 'rb')
            except:
                pass
            else:
                list_to_select = cPickle.load(fd_file)
                #print "list_to_select=" + str(list_to_select)
                fd_file.close()

        if isinstance(list_to_display, (list, tuple)):
            if isinstance(list_to_display[0], (list, tuple)):
                pass
            else:
                list_to_display = [list_to_display]
        else:
            list_to_display = [[list_to_display]]
        
        if isinstance(allow_multiple_selection, (bool)):
            allow_multiple_selection = [allow_multiple_selection for _ in list_to_display]
        elif isinstance(allow_multiple_selection, (list, tuple)):
            if len(allow_multiple_selection) >= len(list_to_display):
                pass
            else:
                allow_multiple_selection_tmp = allow_multiple_selection
                allow_multiple_selection = []
                for i in range(len(list_to_display)):
                    if i < len(allow_multiple_selection_tmp):
                        allow_multiple_selection.append(allow_multiple_selection_tmp[i])
                    else:
                        allow_multiple_selection.append(False)

        self.value_selected = [None for _ in list_to_display]
            
        if self.dryrun == False:

            self.root.title(title_name)
            f1 = Tkinter.Frame(self.root)
            self.quitButton = Tkinter.Button(f1, text='OK', command=self.ok_button)
            self.quitButton.pack(side = Tkinter.BOTTOM, fill = Tkinter.X)
    
            s1                  = [None for _ in list_to_display]
            self.l1             = [None for _ in list_to_display]
            f2                  = [None for _ in list_to_display]
            for j in reversed(range(len(list_to_display))):
                # Frame creation for each listbox
                f2[j] = Tkinter.Frame(f1)
                
                # Create scrollbar
                s1[j] = Tkinter.Scrollbar(f2[j])
                
                # Create listbox
                if allow_multiple_selection[j] == True:
                    self.l1[j] = Tkinter.Listbox(f2[j],width=60,height=min(10,len(list_to_display[j])),font=('Alstom',13), selectmode='multiple', exportselection = False)
                else:
                    self.l1[j] = Tkinter.Listbox(f2[j],width=60,height=min(10,len(list_to_display[j])),font=('Alstom',13), exportselection = False)
                    
                # Insert elements of list
                self.value_selected[j] = list_to_display[j][0]
                for i, item in enumerate(list_to_display[j]):
                    self.l1[j].insert(i, item)
                    if list_to_select != None:
                        if item in list_to_select[j]:
                            # Select by default
                            self.l1[j].selection_set(i)
                            self.value_selected[j] = list_to_display[j][i]

                #Manage scrollbar
                s1[j].config(command = self.l1[j].yview) 
                self.l1[j].config(yscrollcommand = s1[j].set) 
                self.l1[j].bind('<<ListboxSelect>>', self.CurSelect_Multiple)
                self.l1[j].pack(side = Tkinter.LEFT, fill = Tkinter.BOTH)
                
                # Valorize value_selected
                if allow_multiple_selection[j] == True:
                    if isinstance(self.value_selected[j], (list, tuple)) == False :
                        self.value_selected[j] = [self.value_selected[j],]
                
                #Pack Listbox + scrollbar
                s1[j].pack(side = Tkinter.RIGHT, fill = Tkinter.Y) 
                f2[j].pack(side = Tkinter.BOTTOM, fill = Tkinter.BOTH)
            
            f1.pack(fill = Tkinter.BOTH)

            # Center window
            self.center_window(self.root)
            # self.root.update_idletasks()
            # # get screen width and height
            # ws = self.root.winfo_screenwidth() # width of the screen
            # hs = self.root.winfo_screenheight() # height of the screen
            # size = tuple(int(_) for _ in self.root.geometry().split('+')[0].split('x'))
            # x = ws/2 - size[0]/2
            # y = hs/2 - size[1]/2
            # # set the dimensions of the screen and where it is placed
            # self.root.geometry("%dx%d+%d+%d" % (size + (x, y)))
            
            # WAIT FOR USER response
            self.root.wait_window()

        if self.dryrun == True:
            # Force value selected with allow_multiple_selection == True to be a list even if only one element has been selected by the user
            for j in reversed(range(len(list_to_display))):
                # Valorize value_selected with first element
                self.value_selected[j] = list_to_display[j][0]
                if allow_multiple_selection[j] == True:
                    if isinstance(self.value_selected[j], (list, tuple)) == False :
                        self.value_selected[j] = [self.value_selected[j],]

        # Save the selection
        if save_selection != None:
            fd_file = open(save_selection, 'wb')
            #print "self.value_selected=" + str(self.value_selected)
            cPickle.dump(self.value_selected, fd_file, protocol = -1)
            fd_file.close()

        return self.selected_button, self.value_selected
    
    def ok_button(self):
        self.selected_button = "ok"
        self.root.destroy()

    def popupWarning(self, text, title=""):
        showwarning(title=title, message=text)
        #self.root.wait_window()

    def close(self):
        if self.root != None:
            self.root.quit()

    def center_window(self, root):
        # Center window
        root.update_idletasks()
        # get screen width and height
        ws = root.winfo_screenwidth() # width of the screen
        hs = root.winfo_screenheight() # height of the screen
        size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
        x = ws/2 - size[0]/2
        y = hs/2 - size[1]/2
        # set the dimensions of the screen and where it is placed
        root.geometry("%dx%d+%d+%d" % (size + (x, y)))

    def popup(self, text, title="Information"):
        root = Tkinter.Tk()
        root.title(title)

        label = Tkinter.Label(root, text=text, justify=Tkinter.LEFT)
        label.pack(side="top", fill="both", expand=True, padx=20, pady=20)

        button = Tkinter.Button(root, text="OK", command=lambda: root.destroy())
        button.pack(side="bottom", fill="none", expand=True)

        self.center_window(root)
        root.mainloop()

####################################################
#### Unitary test


if __name__ == "__main__":
    # root = Tkinter.Tk()
    # ObjGui = Gui(gui_root = root)
    # ObjGui.gui_list(title_name = "Choose something", list_to_display = ("toto", "tata"))
    # print "You have selected: " + str(ObjGui.value_selected)
    # ObjGui.close()

    # root = Tkinter.Tk()
    # ObjGui = Gui(gui_root = root)
    # ObjGui.gui_multiple_list("Choose something... multiple selection is possible on 2nd list",
    #                          list_to_display = (("toto", "tata"),("titi", "tutu")),
    #                          allow_multiple_selection  = [False, True])
    # print "You have selected: " + str(ObjGui.value_selected)
    # ObjGui.close()

    root = Tkinter.Tk()
    ObjGui = Gui(gui_root=root)
    ObjGui.popupWarning(text="coucou"*10)
    ObjGui.close()

    # ObjGui = Gui(gui_root = None)
    # text = "Hello World\n"*10 + "coucou\n" + "incredible long text "*3
    # ObjGui.popup(text)
    # ObjGui.close()
