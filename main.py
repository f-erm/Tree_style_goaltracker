import tkinter as tk
from tkinter import ttk
import os


#TODO
#Alles auf sqlite3 umstellen
#das load beenden
#überprüfen ob load auch wirlich das top aim findet, auch wenn es irgendwo in der mitte steht
#jetzt da aims über id zugänglich sind müssen die tops nicht mehr immer ls referenz mitangegeben werden, oder? zumindest überprüfen bitte
#switchsite und loadsite irgendwie besser machen
###################################
#die ganzen loadsite referenzen, die den frame immer als argument mitgeben entfernen und direkt den ensprechenden frame geben
#alles optisch hübscher machen/stabilität testen
#vlt dassubaim hinzufügen in aimbutton class machen, dann muss nicht immer top mitangegeben werden
#packroutine rekursiv machen


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

    def frame(self):
        #for easier use
        return self.scrollable_frame


class aimbutton(ttk.Button):
    #contains one subaim, connected to its subaims and its top aim. can create new aims.
    def __init__(self, container, *args, **kwargs):
        super().__init__(container,*args,text=kwargs["text"],command=kwargs["command"])
        self.id=kwargs["id"]
        self.listname=kwargs["listname"]
        self.top = kwargs["top"]
        self.text=kwargs["text"]
        self.done = tk.BooleanVar()
        self.done.set(False)
        self.subs=[]
        self.link=None

    def packroutine(self,reihe=1):
        #place the buttons on their destined position and check if link is done
        if(self.link != None):
            if(aims[self.link][0].done.get()):
                self.done.set(True)
        global reihenbreite
        if reihe==1:
            reihenbreite = reihenbreite.fromkeys(reihenbreite,10)
        if len(reihenbreite)<reihe:
            reihenbreite[str(reihe)]=10
        self.place(x=reihenbreite[str(reihe)],y=reihe*60-50)
        self.lift()
        aimframecontent.scrollable_frame.update()
        reihenbreite[str(reihe)] += self.winfo_width() + 10
        for i in self.subs:
            i.packroutine(reihe+1)

    def lineroutine(self):
        #draws the lines
        def drawline(end,done):
            if done:
                fill='green'
                width=3
            else:
                fill='grey'
                width=2
            linecanvas.create_line(
            (self.winfo_x() + self.winfo_width()/2),
            (self.winfo_y()+int(self.winfo_height())),
            (end.winfo_x()+end.winfo_width()/2),
            (end.winfo_y()),
            fill=fill,width=width)
        if self.done.get():
            linecanvas.create_rectangle(self.winfo_x()-2,self.winfo_y()-2
            ,self.winfo_x()+self.winfo_width()+1
            ,self.winfo_y()+self.winfo_height()+1,fill="green")
        if len(self.subs) > 0:
            #draw line and coninue below
            for i in self.subs:
                drawline(i,i.done.get())
                i.lineroutine()

    def getselfinfo(self):
        #returns all relevant atributes, top and subs are given as id
        #Order is listname,id,text,done,top,subs,link
        if self.top==None:
            top="N"
        else:
            top=str(self.top.id)
        if len(self.subs)==0:
            sub = "N"
        else:
            sub = "".join([str(sub.id)+";;" for sub in self.subs])[:-2]
        if self.link==None:
            link="N"
        else:
            link=self.link
        return (self.listname,str(self.id),self.text,str(self.done.get())
        ,top,sub,link)



def save(data,data_old):
    #save current programm state into data.txt
    print("save")
    #try to open datafile
    try:
        with open(data,"r") as f:
            backup = f.readlines()
        f = open(data,mode="w")
    except:
        print("unable to open datafile")
        return
    #write to file
    try:
        for aim in aims.keys():
            for a in aims[aim]:
                f.write("".join([i+"||"for i in a.getselfinfo()]))
                f.write("\n")
            f.write("\n")
        f.close()
        #copy old content to data_old:
        with open(data_old,"w") as ao:
            ao.writelines(backup)
    except:
        print("unable to save, reverted changes")
        f.close()
        with open(data,"w") as f:
            f.writelines(backup)


def cancon(self=0):
    #confiure canvas dimensions on resize
    mainframe.unbind("<Configure>")
    mainframe.update()
    sideframecontent.canvas.configure(width=250,height= vertline.winfo_height()-100)
    aimframecontent.canvas.configure(width=horiline2.winfo_width()-40,height=vertline.winfo_height()-30)
    linecanvas.configure(width=horiline2.winfo_width()-40,height=vertline.winfo_height()-30)
    mainframe.update()
    #get needed dimensions for canvas
    x=1000
    y=1000
    for wid in aimframecontent.scrollable_frame.winfo_children():
        if wid.winfo_x()>x:
            x += 200
        if wid.winfo_y()>y:
            y += 200
    aimframecontent.scrollable_frame.configure(width=x,height=y)
    linecanvas.configure(width=x,height=y)
    mainframe.bind("<Configure>",cancon)


def get_all_ids():
    #return list of all used ids TODO als List comprehenseion [i for i in usw] schreiben
    l= []
    for i in aims.keys():
        for e in aims[i]:
            l.append(e.id)
    return l


def get_new_id():
    #get lowest availible id
    id = 0
    l= get_all_ids()
    while id in l:
        id += 1
    return id


def switchframes(old,new,destroy=False):
    #change from old to new, destroy all children of old if needed
    if old.winfo_ismapped():
        old.pack_forget()
        if destroy:
            for child in old.winfo_children():
                child.destroy()
        new.pack(fill="both",expand=True)

########################################################################################## ab hier sind die unteren nicht mehr clean,
#aber guck nochmal  ob du wirklich die ganzen func argumente hardcoden willst

def destroy_all():
    #destroy the current state TODO auch automatisch den aktuellen frame löschen?
    global aims
    global aims_by_id
    aims = {}
    aims_by_id={}
    for button in sideframecontent.scrollable_frame.winfo_children():
        button.destroy()

def resetsave(data,data_old):
    print("reset save")
    #switch content of data and data_old
    os.rename(data,data_old+"___tmp")
    os.rename(data_old,data)
    os.rename(data_old+"___tmp",data_old)
    destroy_all()
    #prepare site
    switchframes(settingsframe,mainframe,destroy=True)
    loadsite(None,titlevar,aimframecontent.scrollable_frame)
    #load new data
    load(data)


#TODO
#add(name,id)mact das top aim , sidebutton+ersten aimbutton
#add_subaim() ist zum subs ädden
def load(data):
    print("load:")
    print(data)
    try:
        with open(data,mode='r') as file:
            #splitt into lists, containing only sub aims with one main aim
            sections=[[]]
            counter = 0
            for line in file.read().splitlines():
                if line == "":
                    sections.append([])
                    counter += 1
                else:
                    sections[counter].append(line)
            if sections[-1]==[]:
                del sections[-1]
            #turn aims into usable format
            sections=[[s.split("||")[:-1] for s in section] for section in sections]
            #add the aims, starting with the top aim
            for section in sections:
                #add the aims, starting with the top aim
                cur_aim = section.pop(0)
                add_aim(cur_aim[0],int(cur_aim[1]))
                #handle all its subs:
                while(len(section)>0):
                    for aim in list(section):
                        if int(aim[4]) in get_all_ids():#wenn top schon existiert
                            #create it, top is known -- listname,id,text,done,top,subs,link
                            section.remove(aim)
                            add_subaim(aim[0],int(aim[1]),aim[2],aims_by_id[int(aim[4])])
    except:
       destroy_all()
       print("unable to load")
    if len(aims)==0:
        loadsite(None,titlevar,aimframecontent.frame())
    else:
        loadsite(list(aims.keys())[0],titlevar,aimframecontent.frame())

def remove_aim(captvar):
    #invert remove and set catpvar accordingly
    global remove
    if not remove:
        remove = True
        captvar.set("Stop Remove/Configure")
    else:
        remove=False
        captvar.set("Remove/Configure")


def escfunc(x,lastsite=None):
    #return back to mainpage, the x is only filler so bindings can be used
    switchframes(settingsframe,mainframe,destroy=True)
    if lastsite != None:
        loadsite(lastsite,titlevar,aimframecontent.scrollable_frame)
    else:
        loadsite(list(aims.keys())[0],titlevar,aimframecontent.scrollable_frame)


def goto_settings(listofwidgets=[]):
    #goto settings and show all widgets in listofwidgets
    #find last site, to know where to go back to
    lastsite=None
    for i in aims.keys():
        if aims[i][0].winfo_ismapped():
            lastsite = i
            break
    #setup the new frame
    switchframes(mainframe,settingsframe)
    gobackbutton = ttk.Button(settingsframe,text=" Go back to aims "
    ,command=lambda :escfunc(1,lastsite=lastsite))
    root.bind('<Escape>',lambda x:escfunc(x,lastsite=lastsite))
    sep1 = ttk.Separator(settingsframe,orient="horizontal")
    sep2 = ttk.Separator(settingsframe,orient="horizontal")
    sep1.pack(pady=(40,0),expand=True,fill="both")
    for widget in listofwidgets:
        if widget != None:
            widget.pack(pady=(5,5))
    sep2.pack(pady=(50,50),expand=True,fill="both")
    gobackbutton.pack(pady=(100,0))


def mainclick(name,this):
    #when aim is clicked, load the needed settings, or jump to link
    if this == None:
        this = aims[name][0]
    if this.link == None:
        goto_settings(
        [create_subbuttons(name,this)
        ,getcheckbutton(name,this)
        ,getrename(name,this)
        ,getlink(name,this)])
    else:
        global remove
        if not remove:
            loadsite(this.link,titlevar,aimframecontent.scrollable_frame)
        else:
            goto_settings(
            [create_subbuttons(name,this)
            ,getcheckbutton(name,this)
            ,getrename(name,this)
            ,getlink(name,this)])
            remove_aim(remove_side_caption)


def add_subaim(listname,id,text,top):
    #make new subaim of top and append it. vlt lieber als func von aimbutton class?
    new = aimbutton(aimframecontent.scrollable_frame,listname=listname
    ,text=text,id=id,top=top,command=lambda:mainclick(listname,new))
    aims[listname].append(new)
    aims_by_id[id]=new
    top.subs.append(new)
    return new #for manuall adding of subaims


def add_aim(name,id):
    #add the new main aim. creates the nessecary sidebutton and the first
    #aimbutton. only needs listname and id to do this
    if name not in aims.keys():
        aims[name]=[]
        #make new aimbutton
        new = aimbutton(aimframecontent.scrollable_frame
        ,text=name,listname=name,id=id,top=None
        ,command=lambda:mainclick(name,None))
        aims[name].append(new)
        aims_by_id[id]=new
        #add the nessecary sidebutton
        ttk.Button(sideframecontent.scrollable_frame
        ,text = name, command=lambda: sideclick(name)).pack()
        loadsite(name,titlevar,aimframe)
        return new#for adding aims manually


def sideclick(name):
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
                        loadsite(list(aims.keys())[0]
                        ,titlevar,aimframecontent.scrollable_frame)
                    else:
                        loadsite(None,titlevar,aimframecontent.scrollable_frame)
                    break
    else:
        #change to site
        loadsite(name,titlevar,aimframecontent.scrollable_frame)


def loadsite(name,caption,aimframe):
    #load site of name into aimframe and change caption
    for child in aimframe.winfo_children():
        child.place_forget()
    if name != None and name in aims:
        linecanvas.place(x=0,y=0)
        linecanvas.delete("all")
        aims[name][0].packroutine()
        aims[name][0].lineroutine()
        caption.set("Aktuelle Auswahl:     "+name)
    else:
        caption.set("Aktuelle Auswahl:     ")



#Globals
aims={}
aims_by_id={}
global remove
remove = False
reihenbreite={}
data_location="data.txt"
data_old_location="data_old.txt"

#setup frames
root = tk.Tk()
root.title("Aimmap")
img = tk.Image("photo", file="icon.png")
root.tk.call('wm','iconphoto',root._w,img)
mainframe = ttk.Frame(root)#main action
settingsframe = ttk.Frame(root)#change settings
sideframe = ttk.Frame(mainframe)#house sidebuttons and options
aimframe = ttk.Frame(mainframe)#house the aimbuttons
sideframecontent = ScrollableFrame(sideframe)#where the sidebuttons are
aimframecontent = ScrollableFrame(aimframe,orientation="both")#where the aimbuttons are
manage_aims_frame = ttk.Frame(sideframe)#where add and remove aims are
manage_frame = ttk.Frame(sideframe)
linecanvas=tk.Canvas(aimframecontent.scrollable_frame)
mainframe.pack(fill="both",expand=True)
sideframe.grid(column=0,row=2,sticky=("N","W","S"),padx=(10,10),pady=(5,5))
aimframe.grid(column=2,row=2,sticky=("N","W"),padx=(10,10),pady=(5,15))
sideframecontent.grid(column=0,row=3,sticky=("N","W"),pady=(5,5))
aimframecontent.pack(fill="both",expand=True)
manage_aims_frame.grid(column=0,row=1,sticky=("N","W"),pady=(5,5))
manage_frame.grid(column=0,row=100,sticky=("N","W"))
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
settings_button=ttk.Button(manage_frame,text="Settings"
,command = lambda: goto_settings([get_revert()]))
settings_button.pack(side="right")

savebutton=ttk.Button(manage_frame,text="Save"
,command=lambda:save(data_location,data_old_location))
savebutton.pack(side="right",padx=(10,30))

add_side=ttk.Button(manage_aims_frame,text="Add Aim"
,command = lambda:goto_settings([get_side_add_button(
aimframe=aimframecontent.scrollable_frame,settingsframe=settingsframe
,mainframe=mainframe,dict=aims,caption=titlevar)]))
add_side.pack(side="left")

remove_side_caption = tk.StringVar()
remove_side_caption.set("Remove/Configure")
remove_side = ttk.Button(manage_aims_frame,textvariable=remove_side_caption
,command = lambda: remove_aim(captvar=remove_side_caption))
remove_side.pack(side="left",padx=(10,0))
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
            add_aim(name,get_new_id())
            switchframes(settingsframe,mainframe,destroy=True)
            loadsite(name,caption,aimframe)
    button = ttk.Button(frame,text="Add Aim",command=func)
    entry.focus_set()
    entry.bind('<Return>',func)
    label.pack()
    entry.pack()
    button.pack()
    return frame

def create_subbuttons(listname,top):
    #load options to create new subaim of an aim given by id and listname
    #setup
    frame = tk.Frame(settingsframe,highlightbackground="black", highlightthickness=1)
    label = ttk.Label(frame,text="Name of subname:")
    entry = ttk.Entry(frame)
    #clickfunc
    def func(event=0):
        add_subaim(listname,get_new_id(),entry.get(),top)
        escfunc(1,listname)
    #additional setup
    button = ttk.Button(frame,text="Add Aim",command=func)
    entry.focus_set()
    entry.bind('<Return>',func)
    label.pack()
    entry.pack()
    button.pack()
    return frame

def getcheckbutton(listname,this):
    #get checkbutton to finish aim
    frame = tk.Frame(settingsframe,highlightbackground="black"
    , highlightthickness=1)
    label = ttk.Label(frame,text="is aim "+str(this.text)+" done?:")
    check = tk.Checkbutton(frame,text= "",variable=this.done
    , onvalue=True,offvalue=False
    ,command=lambda:escfunc(1,lastsite=this.listname))
    label.pack()
    check.pack()
    return frame

def getrename(listname,this):
    #get option to rename this aim. only works on subaims
    frame = tk.Frame(settingsframe,highlightbackground="black", highlightthickness=1)
    label = ttk.Label(frame,text="Want to rename this aim?")
    entry = ttk.Entry(frame)
    #return None if this is main aim
    if this==aims[listname][0]:
        return None
    def func(event=0):
        this.config(text=entry.get())
        escfunc(1,listname)
    button = ttk.Button(frame,text="Rename",command=func)
    entry.bind('<Return>',func)
    label.pack()
    entry.pack()
    button.pack()
    return frame

def getlink(listname,this):
    #wenn ziel auf das link zeigt nicht mehr vorhanden, entfern den link
    def newlink(event=0):
        if entry.get() in aims.keys():
            this.link=entry.get()
            escfunc(1,listname)
        else:
            textvar.set("This aim does not exist, try again")
    def remlink(event=0):
        this.link = None
        escfunc(1,listname)
    frame = tk.Frame(settingsframe,highlightbackground="black", highlightthickness=1)

    if this.link != None:
        label = ttk.Label(frame,text=f'current Link: {str(this.link)} ')
        removelink = ttk.Button(frame,text="Remove this Link?",command=remlink)
        label.pack()
        removelink.pack()
    else:
        textvar = tk.StringVar()
        textvar.set("Link this aim?")
        label = ttk.Label(frame,textvariable=textvar)
        entry = ttk.Entry(frame)
        submitlink = ttk.Button(frame,text="Link it",command=newlink)
        entry.bind('<Return>',newlink)
        label.pack()
        entry.pack()
        submitlink.pack()
    return frame

def get_revert():
    frame = tk.Frame(settingsframe,highlightbackground="black", highlightthickness=1)
    label = ttk.Label(frame,text="Want to undo your last save?")
    button = ttk.Button(frame,text="Revert to old save"
    ,command=resetsave(data_location,data_old_location))
    label.pack()
    button.pack()
    return frame


################################################################################

#fill with testcontent
add_aim("lol",100)
add_aim("hallo",101)
load(data_location)

#setup resize events
mainframe.bind("<Configure>",cancon)
mainframe.update()
cancon()
root.mainloop()
