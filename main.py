import tkinter as tk
from tkinter import ttk
from ScrollableFrame import ScrollableFrame
import os
import shutil
import sqlite3



class aimbutton(ttk.Button):
    '''One aim. Contains all nessecary information and can render subaims
    and the lines connecting them'''
    def __init__(self, container, *args, **kwargs):
        super().__init__(
                container,*args,text=kwargs["text"],command=kwargs["command"])
        self.id=kwargs["id"]
        self.listname=kwargs["listname"]
        self.top = kwargs["top"] #Given as reference. None = this is a Mainaim
        self.text=kwargs["text"]
        self.done = tk.BooleanVar()
        self.done.set(False)
        self.subs=[]
        self.link=None

    def packroutine(self,reihe=1):
        '''place the buttons on their destined position and check the link'''
        global reihenbreite
        if(self.link != None):
            if(aims[self.link][0].done.get()):
                self.done.set(True)
        if reihe==1:
            reihenbreite = reihenbreite.fromkeys(reihenbreite,10)
        if len(reihenbreite)<reihe:
            reihenbreite[str(reihe)]=10
        self.place(x=reihenbreite[str(reihe)],y=reihe*70-50)
        self.lift()
        aimframecontent.scrollable_frame.update()
        reihenbreite[str(reihe)] += self.winfo_width() + 10
        for i in self.subs:
            i.packroutine(reihe+1)

    def lineroutine(self):
        ''' Draws the lines for all subaims'''
        #Helper func, draws one line from this to end. If done, color = green
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
        #draw line and continue with subaims
        if len(self.subs) > 0:
            for i in self.subs:
                drawline(i,i.done.get())
                i.lineroutine()



def cancon(self=0):
    '''Confiure canvas dimensions on resize. Needed for smooth resize'''
    #Adjust frame to current windowsize
    mainframe.unbind("<Configure>")
    mainframe.update()
    sideframecontent.canvas.configure(width=250,height= vertline.winfo_height()-100)
    aimframecontent.canvas.configure(width=horiline2.winfo_width()-40,height=vertline.winfo_height()-30)
    linecanvas.configure(width=horiline2.winfo_width()-40,height=vertline.winfo_height()-30)
    mainframe.update()
    #Get needed dimensions for canvas
    x=1000
    y=1000
    for wid in aimframecontent.scrollable_frame.winfo_children():
        if wid.winfo_x()+wid.winfo_width()>x:
            x += wid.winfo_width()+20
        if wid.winfo_y()+wid.winfo_height()>y:
            y += wid.winfo_height()+20
    #Adjust Canvas
    aimframecontent.scrollable_frame.configure(width=x,height=y)
    linecanvas.configure(width=x,height=y)
    mainframe.bind("<Configure>",cancon)



def get_new_id():
    '''Gets the lowest availible id'''
    id = 0
    while id in aims_by_id.keys():
        id += 1
    return id


def switchframes(old,new,destroy=False):
    '''Change from old frame to new, only if old is mapped.
    Can destroy all children of old if needed'''
    if old.winfo_ismapped():
        old.pack_forget()
        if destroy:
            for child in old.winfo_children():
                child.destroy()
        new.pack(fill="both",expand=True)


def resetsave(data):
    '''Reset to last commited state, data (given as filename) will be replaced
    by data_old file'''
    global aims
    global aims_by_id
    #revert safefile
    print("reset save")
    try:
        oldname = data.split('.')
        oldname = oldname[0] + "_old." + oldname[1]
        shutil.move(os.path.join(os.getcwd(),oldname)
                    ,os.path.join(os.getcwd(),data))
        print("revert successfull")
    except:
        print("No old data availible")
    #destroy current state
    aims = {}
    aims_by_id={}
    for button in sideframecontent.scrollable_frame.winfo_children():
        button.destroy()
    conn.rollback()
    #prepare site
    loadsite(None)
    #load new data
    load(data)


def remove_aim(captvar):
    '''Invert remove and set catpvar accordingly'''
    global remove
    if not remove:
        remove = True
        captvar.set("Stop Remove/Configure")
    else:
        remove=False
        captvar.set("Remove/Configure")


def escfunc(x,lastsite=None):
    '''Return back to mainpage, the x is only filler so bindings can be used.
    Loads lastsite'''
    switchframes(settingsframe,mainframe,destroy=True)
    loadsite(lastsite)


def goto_settings(listofwidgets=[]):
    '''Goto settings and show all widgets in listofwidgets'''
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
    '''When aim is clicked, load the needed settings, or jump to link'''
    if this == None:
        this = aims[name][0]
    if remove:
        remove_aim(remove_side_caption)
    else:
        if this.link != None:
            loadsite(this.link)
            return
    goto_settings([create_subbuttons(name,this), getcheckbutton(name,this)
                   ,getrename(name,this), getlink(name,this)])


def create_subaim(listname, id , text):
    '''Creates instance of a new subaim, without linking it to other aims.
    Top start out with None, needs to be set to the right value ASAP'''
    new = aimbutton(aimframecontent.scrollable_frame,listname=listname
    ,text=text,id=id,top=False,command=lambda:mainclick(listname,new))
    aims[listname].append(new)
    aims_by_id[id]=new
    return new


def add_subaim(listname,id,text,top):
    '''Make new subaim of top(given by ref),append it and save in datafile'''
    global conn
    #create new aim
    new = create_subaim(listname, id , text)
    top.subs.append(new)
    new.top = top
    #save it
    cur = conn.cursor()
    cur.execute(
    f'INSERT into aims Values({str(id)}, "{listname}", "{text}", 0, {str(top.id)}, NULL);')
    cur.execute(
    f'INSERT into subs VALUES({str(top.id)}, {str(id)}, "{listname}");')


def add_aim(name,id):
    '''Add the new main aim. creates the nessecary sidebutton and the first
    aimbutton. Only needs listname and id to do this'''
    if name not in aims.keys():
        aims[name]=[]
        #make new aimbutton
        new = create_subaim(name,id,name)
        new.top = None
        #add to database
        conn.cursor().execute(
        f'INSERT into aims Values({str(id)}, "{name}", "{name}", 0, NULL, NULL)')
        #add the nessecary sidebutton
        ttk.Button(sideframecontent.scrollable_frame
        ,text = name, command=lambda: sideclick(name)).pack()
        #Load the newly created site
        loadsite(name)


def sideclick(name):
    '''CLickfunc of the sidebuttons. If remove: delete name, else: load it'''
    if remove:
        #remove button and site
            for button in sideframecontent.scrollable_frame.winfo_children():
                if button.cget("text")==name:
                    button.destroy()
                    #remove from db:
                    cur = conn.cursor()
                    cur.execute(f'DELETE FROM aims WHERE listname = "{name}"')
                    cur.execute(f'DELETE FROM subs WHERE list = "{name}"')
                    #Clean up
                    del aims[name]
                    remove_aim(remove_side_caption)
                    loadsite(None)
                    break
    else:
        #change to site
        loadsite(name)


def loadsite(name):
    '''Load site of name into aimframe and change caption'''
    switchframes(settingsframe,mainframe,destroy=True)
    for child in aimframecontent.frame().winfo_children():
        child.place_forget()
    if name != None and name in aims:
        linecanvas.place(x=0,y=0)
        linecanvas.delete("all")
        aims[name][0].packroutine()
        aims[name][0].lineroutine()
        titlevar.set("Current aim:     "+name)
    else:
        titlevar.set("Current aim:     ")


def establish_sub(top, sub):
    '''Creates link between top and sub, both given as id'''
    aims_by_id[top].subs.append(aims_by_id[sub])
    aims_by_id[sub].top = aims_by_id[top]


def load(datafile_name):
    '''Loads the data from datafile_name, sets up all the aims and returns the
    sql connection'''
    try:
        global conn
        conn = sqlite3.connect(DATAFILE_NAME)
        cur = conn.cursor()
        cur.execute(
        'create table if not exists \
        aims(id integer, listname text, name text, done integer, top integer, \
        link text);')
        cur.execute(
        'create table if not exists subs(id integer, child_id integer, list text);')
        #load the main aims
        cur.execute('SELECT listname, id, done, link FROM aims WHERE top IS NULL;')
        for row in cur:
            add_aim(row[0],row[1])
            aims_by_id[row[1]].done.set(row[2]==1)
            aims_by_id[row[1]].link = row[3]
        #load the subaims listname,id,text,top
        cur.execute('SELECT listname, id, name, done, link  FROM aims WHERE top IS NOT NULL;')
        for row in cur:
            create_subaim(row[0], row[1], row[2])
            aims_by_id[row[1]].done.set(row[3]==1)
            aims_by_id[row[1]].link = row[4]
        #load the connections between the aims
        cur.execute('SELECT * FROM subs;')
        for row in cur:
            establish_sub(row[0],row[1])
        #Get highest id
        cur.execute('SELECT MAX(id) FROM aims')
        #load site
        if len(aims)==0:
            loadsite(None)
        else:
            loadsite(list(aims.keys())[0])
    except:
        print("unable to open/load datafile, shutting down...")
        exit()


def save(conn,datafile_name):
    '''Commit changes and preserve copy of datafile'''
    try:
        newname = datafile_name.split('.')
        newname = newname[0] + "_old." + newname[1]
        shutil.copyfile(
            os.path.join(os.getcwd(),datafile_name)
            ,os.path.join(os.getcwd(),newname))
        conn.commit()
        print("saved successfully")
    except:
        print("unable to save!!!")


#Globals
DATAFILE_NAME = "data.db"
aims={}
aims_by_id={}
global remove
global conn
remove = False
reihenbreite={}

#Setup frames
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
titlevar.set('Current aim:     ')
settingsvar = tk.StringVar()
settingsvar.set('Settings:')
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

#Permanentbuttons
settings_button=ttk.Button(manage_frame,text="Settings"
,command = lambda: goto_settings([get_revert()]))
settings_button.pack(side="right")

savebutton=ttk.Button(manage_frame,text="Save"
,command=lambda:save(conn,DATAFILE_NAME))
savebutton.pack(side="right",padx=(10,30))

add_side=ttk.Button(manage_aims_frame,text="Add Aim"
,command = lambda:goto_settings([get_side_add_button(
settingsframe=settingsframe,mainframe=mainframe)]))
add_side.pack(side="left")

remove_side_caption = tk.StringVar()
remove_side_caption.set("Remove/Configure")
remove_side = ttk.Button(manage_aims_frame,textvariable=remove_side_caption
,command = lambda: remove_aim(captvar=remove_side_caption))
remove_side.pack(side="left",padx=(10,0))
sideframe.rowconfigure(98,weight=1)

#optionwidgets:
################################################################################
def get_side_add_button(settingsframe,mainframe):
    '''widget to create a new aim main aim'''
    frame = tk.Frame(settingsframe)
    label = ttk.Label(frame,text="Aimname:")
    entry = ttk.Entry(frame)
    #CLickfunc
    def func(event=0):
        if entry.get() not in aims.keys():
            name=entry.get()
            add_aim(name,get_new_id())
            switchframes(settingsframe,mainframe,destroy=True)
            loadsite(name)
    button = ttk.Button(frame,text="Add Aim",command=func)
    entry.focus_set()
    entry.bind('<Return>',func)
    label.pack()
    entry.pack()
    button.pack()
    return frame

def create_subbuttons(listname,top):
    '''Widget to create new subaim of an aim given by ref and listname'''
    frame = tk.Frame(settingsframe,highlightbackground="black", highlightthickness=1)
    label = ttk.Label(frame,text="Name of subname:")
    entry = ttk.Entry(frame)
    #Clickfunc
    def func(event=0):
        add_subaim(listname,get_new_id(),entry.get(),top)
        escfunc(1,listname)
    button = ttk.Button(frame,text="Add Aim",command=func)
    entry.focus_set()
    entry.bind('<Return>',func)
    label.pack()
    entry.pack()
    button.pack()
    return frame

def getcheckbutton(listname,this):
    '''Get Widget with checkbutton to finish this aim'''
    def func(event = 0):
        #save into sql
        d = int(this.done.get())
        conn.cursor().execute(f'UPDATE aims SET done = {d} WHERE id = {this.id};')
        escfunc(1,listname)
    frame = tk.Frame(settingsframe,highlightbackground="black"
    , highlightthickness=1)
    label = ttk.Label(frame,text="is aim "+str(this.text)+" done?:")
    check = tk.Checkbutton(frame,text= "",variable=this.done
    , onvalue=True,offvalue=False
    ,command=func)
    label.pack()
    check.pack()
    return frame

def getrename(listname,this):
    '''Get option to rename this aim. Only works on subaims'''
    frame = tk.Frame(settingsframe,highlightbackground="black", highlightthickness=1)
    label = ttk.Label(frame,text="Want to rename this aim?")
    entry = ttk.Entry(frame)
    #return None if this is main aim
    if this.top == None:
        return None
    def func(event=0):
        this.config(text=entry.get())
        conn.cursor().execute(
            f'UPDATE aims SET name = "{entry.get()}" WHERE id = {this.id};')
        escfunc(1,listname)
    button = ttk.Button(frame,text="Rename",command=func)
    entry.bind('<Return>',func)
    label.pack()
    entry.pack()
    button.pack()
    return frame

def getlink(listname,this):
    '''Widget to manage the link of an aim'''
    def newlink(event=0):
        if entry.get() in aims.keys():
            this.link=entry.get()
            conn.cursor().execute(
                f'UPDATE aims SET link = "{entry.get()}" WHERE id = {this.id};')
            escfunc(1,listname)
        else:
            textvar.set("This aim does not exist, try again")
    def remlink(event=0):
        this.link = None
        conn.cursor.execute(f'UPDATE aims SET link = NULL WHERE id = {this.id};')
        escfunc(1,listname)
    #If aim to which the link points does not exist, remove the link
    if this.link not in aims.keys():
        this.link = None
    frame = tk.Frame(settingsframe,highlightbackground="black", highlightthickness=1)
    #If link exists, load options to remove it
    if this.link != None:
        label = ttk.Label(frame,text=f'current Link: {str(this.link)} ')
        removelink = ttk.Button(frame,text="Remove this Link?",command=remlink)
        label.pack()
        removelink.pack()
    else:
        #load options to create a new link
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
    ''' Widget with revert options'''
    frame = tk.Frame(settingsframe,highlightbackground="black", highlightthickness=1)
    label = ttk.Label(frame,text="Want to undo your last save?")
    button = ttk.Button(frame,text="Revert to old save"
    ,command=lambda:resetsave(DATAFILE_NAME))
    label.pack()
    button.pack()
    return frame


################################################################################

#Setup resize event and Start Programm
load(DATAFILE_NAME)
mainframe.bind("<Configure>",cancon)
mainframe.update()
cancon()
root.mainloop()
