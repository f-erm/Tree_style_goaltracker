import tkinter as tk
from tkinter import ttk


#TODO scrollbinds damit man die frames auch mit maus  scrollen kann

#Globals
aims={}
global remove
remove = False


class ScrollableFrame(ttk.Frame):
    #frame with scrollbars.Can can be vertical or both
    #use self.scrollable_frame to acces content of frame
    def __init__(self, container, orientation ="vertical", *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.canvas.configure(width=250,height = 250)
        if orientation == "vertical":
            scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self.scrollable_frame = ttk.Frame(self.canvas)
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")))
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=scrollbar.set)
            self.canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        elif orientation == "horizontal":
            scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.scrollable_frame = ttk.Frame(self.canvas)
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")))
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(xscrollcommand=scrollbar.set)
            self.canvas.pack(side="top",fill="both",expand=True)
            scrollbar.pack(side="bottom", fill="x")
        elif orientation == "both":
            vertbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            horbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.scrollable_frame = ttk.Frame(self.canvas)
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")))
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(xscrollcommand=horbar.set)
            self.canvas.configure(yscrollcommand=vertbar.set)
            vertbar.pack(side="right", fill="y")
            self.canvas.pack(side="top",fill="both",expand=True)
            horbar.pack(side="bottom", fill="x")
        else:
            raise("orientation required. Use vertical,horizontal,both")


class aimbutton(ttk.Button):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container,*args,text=kwargs["text"],command=kwargs["command"])
        self.subs=[]
        self.id=kwargs["id"]
        self.listname=kwargs["listname"]

    def packself(self):
        self.pack()

    def packroutine(self):
        for sub in self.subs:
            sub.packself()
            sub.packroutine()


def test(self=0):
    print("test")

def cancon(self=0):
    #confiure canvas dimensions on resize
    mainframe.unbind("<Configure>")
    mainframe.update()
    sideframecontent.canvas.configure(width=250,height= vertline.winfo_height()-100)
    aimframecontent.canvas.configure(width=horiline2.winfo_width()-40,height=vertline.winfo_height()-30)
    mainframe.update()
    mainframe.bind("<Configure>",cancon)

def switchframes(old,new,destroy=False):
    #change from old to new, destroy all children of old if needed
    if old.winfo_ismapped():
        old.pack_forget()
        if destroy:
            for child in old.winfo_children():
                child.destroy()
        new.pack(fill="both",expand=True)

def remove_aim(captvar):
    #invert remove and set catpvar accordingly
    global remove
    if not remove:
        remove = True
        #remove_side_caption.set("Click aim to remove it")
        captvar.set("Click aim to remove it")
    else:
        remove=False
        captvar.set("Remove Aim")

def goto_settings(listofwidgets=[]):
    #goto settings and show all widgets in listofwidgets
    switchframes(mainframe,settingsframe)
    gobackbutton = ttk.Button(settingsframe,text=" Go back to aims "
    ,command=lambda:switchframes(settingsframe,mainframe,destroy=True))
    sep1 = ttk.Separator(settingsframe,orient="horizontal")
    sep2 = ttk.Separator(settingsframe,orient="horizontal")
    sep1.pack(pady=(40,0),expand=True,fill="both")
    for widget in listofwidgets:
        widget.pack()
    sep2.pack(pady=(50,50),expand=True,fill="both")
    gobackbutton.pack(pady=(100,0))

def add_aim(name,dict,aimframe,caption):
    #add the new aim to frame.
    if name not in dict.keys():
        dict[name]=[]
        id = get_new_id()
        dict[name].append(aimbutton(aimframecontent.scrollable_frame
        ,text=name,listname=name,id=id
        ,command=lambda:goto_settings([create_subbuttons(name,id)])))
        ttk.Button(sideframecontent.scrollable_frame
        ,text = name, command=lambda: sideclick(name,dict,caption)).pack()
        loadsite(name,caption,aimframe)

def sideclick(name,dict,caption):
    #if remove==True delete the name aim, else change to aim
    global remove
    if remove:
        #remove button and site
            for button in sideframecontent.scrollable_frame.winfo_children():
                if button.cget("text")==name:
                    button.destroy()
                    del aims[name]
                    #global remove
                    remove=False
                    remove_side_caption.set("Remove Aim")
                    if len(aims) != 0:
                        loadsite(list(aims.keys())[0],caption
                        ,aimframecontent.scrollable_frame)
                    else:
                        loadsite(None,caption,aimframecontent.scrollable_frame)
                    break
    else:
        #change to site
        loadsite(name,caption,aimframecontent.scrollable_frame)


def loadsite(name,caption,aimframe):
    #load site of name name into aimframe and change caption
    for child in aimframe.winfo_children():
        child.pack_forget()
    if name != None and name in aims:
        aims[name][0].packself()
        aims[name][0].packroutine()
        caption.set("Aktuelle Auswahl:     "+name)
    else:
        caption.set("Aktuelle Auswahl:     ")

def get_new_id():
    #get lowest availible id
    id = 0
    l= []
    for i in aims.keys():
        for e in aims[i]:
            l.append(e.id)
    while id in l:
        id += 1
    return id



#setup frames
root = tk.Tk()
root.title("Aimmap")
mainframe = ttk.Frame(root)#main action
settingsframe = ttk.Frame(root)#change settings
sideframe = ttk.Frame(mainframe)#house sidebuttons and options
aimframe = ttk.Frame(mainframe)#house the aimbuttons
sideframecontent = ScrollableFrame(sideframe)#where the sidebuttons are
aimframecontent = ScrollableFrame(aimframe,orientation="both")#where the aimbuttons are
manage_aims_frame = ttk.Frame(sideframe)#where add and remove aims are
mainframe.pack(fill="both",expand=True)
sideframe.grid(column=0,row=2,sticky=("N","W","S"),padx=(10,10),pady=(5,5))
aimframe.grid(column=2,row=2,sticky=("N","W"),padx=(10,10),pady=(5,15))
sideframecontent.grid(column=0,row=3,sticky=("N","W"),pady=(5,5))
aimframecontent.pack(fill="both",expand=True)
manage_aims_frame.grid(column=0,row=1,sticky=("N","W"),pady=(5,5))
mainframe.rowconfigure(2, weight=1)
mainframe.columnconfigure(2,weight=1)
root.minsize(600,400)

#Title Labels
titlevar = tk.StringVar()
titlevar.set('Aktuelle Auswahl:     ERSTE TESTSEITE')
settingsvar = tk.StringVar()
settingsvar.set('Einstellungen:')
settingstitle = ttk.Label(mainframe, textvariable=settingsvar)
title = ttk.Label(mainframe, textvariable=titlevar)
settingstitle.grid(column=0,row=0,sticky=("N", "W"))
title.grid(column=2,row=0, sticky=("N","W"))

#Lines
horiline = ttk.Separator(mainframe, orient="horizontal")
horiline2 = ttk.Separator(mainframe, orient="horizontal")
horiline3 = ttk.Separator(mainframe, orient="horizontal")
horiline4 = ttk.Separator(mainframe, orient="horizontal")
vertline = ttk.Separator(mainframe, orient="vertical")
horiline.grid(column=0,row=1,sticky=("W","E"))
horiline2.grid(column=2,row=1,sticky=("W","E"))
horiline3.grid(column=0,row=101,sticky=("W","E"))
horiline4.grid(column=2,row=101,sticky=("W","E"))
vertline.grid(column=1,row=2,sticky=("N","S","W"))
sepline1 = ttk.Separator(sideframe, orient="horizontal")
sepline2 = ttk.Separator(sideframe, orient="horizontal")
sepline1.grid(column=0,row=4,sticky=("W","E","N"),pady=(0,5))
sepline2.grid(column=0,row=2,sticky=("W","E","S"),pady=(5,0))

#permanentbuttons
settings_button=ttk.Button(sideframe,text="Settings",command = goto_settings)
settings_button.grid(column=0,row=100,sticky=("N","W"))
add_side=ttk.Button(manage_aims_frame,text="Add Aim"
,command = lambda:goto_settings([get_side_add_button(
aimframe=aimframecontent.scrollable_frame,settingsframe=settingsframe
,mainframe=mainframe,dict=aims,caption=titlevar)]))
add_side.pack(side="left")
remove_side_caption = tk.StringVar()
remove_side_caption.set("Remove Aim")
remove_side = ttk.Button(manage_aims_frame,textvariable=remove_side_caption
,command = lambda: remove_aim(captvar=remove_side_caption))
remove_side.pack(side="left",padx=(10,10))
sideframe.rowconfigure(98,weight=1)

#optionwidgets:
################################################################################
def get_side_add_button(aimframe,settingsframe,mainframe,dict,caption):
    #load options to create a new aim
    frame = tk.Frame(settingsframe)
    label = ttk.Label(frame,text="Aimname:")
    entry = ttk.Entry(frame)
    def func(event=0):
        if entry.get() not in dict.keys():
            name=entry.get()
            add_aim(name,dict,aimframe=aimframe,caption=caption)
            switchframes(settingsframe,mainframe,destroy=True)
            loadsite(name,caption,aimframe)
    button = ttk.Button(frame,text="Add Aim",command=func)
    entry.focus_set()
    entry.bind('<Return>',func)
    label.pack()
    entry.pack()
    button.pack()
    return frame

def create_subbuttons(listname,id):
    #load options to create new subaim of aaim given by id and listname
    frame = tk.Frame(settingsframe)
    label = ttk.Label(frame,text="Name of subname:")
    entry = ttk.Entry(frame)
    def func(event=0):
        newid = get_new_id()
        new = aimbutton(aimframecontent.scrollable_frame,listname=listname
        ,text=entry.get(),id=newid
        ,command=lambda:goto_settings([create_subbuttons(listname,newid)]))
        aims[listname].append(new)
        for b in aims[listname]:
            if b.id==id:
                b.subs.append(new)
        switchframes(settingsframe,mainframe,destroy=True)
        loadsite(listname,caption=titlevar,aimframe=aimframecontent.scrollable_frame)
    button = ttk.Button(frame,text="Add Aim",command=func)
    entry.focus_set()
    entry.bind('<Return>',func)
    label.pack()
    entry.pack()
    button.pack()
    return frame

################################################################################

#fill with testcontent
add_aim("erster test",aims,aimframe=aimframecontent.scrollable_frame
,caption=titlevar)
add_aim("zweiter test",aims,aimframe=aimframecontent.scrollable_frame
,caption=titlevar)

#setup resize events
mainframe.bind("<Configure>",cancon)
mainframe.update()
cancon()
root.mainloop()
