import tkinter as tk
from tkinter import ttk
from ScrollableFrame import ScrollableFrame
import os
import shutil
import sqlite3


#TODO
#add subaim aufteilen, sodass top als id oder ref gegeben werden kann, und einträge nicht dupliziert werden, da add_subbutton ja auch zu sql hinzufügt
#löschen möglich machen
#top wird nur gebraucht um das neue aim anzuhängen....
#jetzt da aims über id zugänglich sind müssen die tops nicht mehr immer ls referenz mitangegeben werden, oder? zumindest überprüfen bitte
#switchsite und loadsite irgendwie besser machen
#die ganzen loadsite referenzen, die den frame immer als argument mitgeben entfernen und direkt den ensprechenden frame geben
#alles optisch hübscher machen/stabilität testen


DATAFILE_NAME = "data.db"


class aimbutton(ttk.Button):
    #contains one subaim, connected to its subaims and its top aim. can create new aims.
    def __init__(self, container, *args, **kwargs):
        super().__init__(container,*args,text=kwargs["text"],command=kwargs["command"])
        self.id=kwargs["id"]
        self.listname=kwargs["listname"]
        self.top = kwargs["top"] #Given as reference
        self.text=kwargs["text"]
        self.done = tk.BooleanVar()
        self.done.set(False)
        self.subs=[]
        self.link=None

    def packroutine(self,reihe=1):
        '''place the buttons on their destined position and checks if link is done'''
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
        ''' Draws the lines for all subaims'''
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
        #Order is listname,id,text,done,top,subs,link TODO rework pls
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


def get_new_id():
    #get availible id
    global highest_id
    highest_id += 1
    return highest_id


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
    global conn
    aims = {}
    aims_by_id={}
    for button in sideframecontent.scrollable_frame.winfo_children():
        button.destroy()
    conn.rollback()

def resetsave(data,data_old): #TODO
    print("reset save")
    os.rename(DATAFILE_NAME+"_old",DATAFILE_NAME)
    destroy_all()
    #prepare site
    switchframes(settingsframe,mainframe,destroy=True)
    loadsite(None,titlevar,aimframecontent.scrollable_frame)
    #load new data
    load(data)



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

'''
def create_subaim(listname, id , text):
    '''creates instance of new subaim, without linking it to different aim.
    Top start out with None, needs to be set to the right value ASAP'''
    new = aimbutton(aimframecontent.scrollable_frame,listname=listname
    ,text=text,id=id,top=None,command=lambda:mainclick(listname,new))
    aims[listname].append(new)
    aims_by_id[id]=new
'''

def add_subaim(listname,id,text,top):
    #make new subaim of top(given by ref) and append it
    global conn
    new = aimbutton(aimframecontent.scrollable_frame,listname=listname
    ,text=text,id=id,top=top,command=lambda:mainclick(listname,new))
    aims[listname].append(new)
    aims_by_id[id]=new
    top.subs.append(new)
    cur = conn.cursor()
    cur.execute(
    f'INSERT into aims Values({str(id)}, "{listname}", "{text}", 0, {str(top.id)}, NULL);')
    cur.execute(
    f'INSERT into subs VALUES({str(top.id)}, {str(id)}, "{listname}");')


def add_aim(name,id):
    #add the new main aim. creates the nessecary sidebutton and the first
    #aimbutton. only needs listname and id to do this
    global conn
    if name not in aims.keys():
        aims[name]=[]
        #make new aimbutton
        new = aimbutton(aimframecontent.scrollable_frame
        ,text=name,listname=name,id=id,top=None
        ,command=lambda:mainclick(name,None))
        aims[name].append(new)
        aims_by_id[id]=new
        #add to database
        cur = conn.cursor().execute(f'INSERT into aims Values({str(id)}, "{name}", "{name}", 0, NULL, NULL)')
        #add the nessecary sidebutton
        ttk.Button(sideframecontent.scrollable_frame
        ,text = name, command=lambda: sideclick(name)).pack()
        loadsite(name,titlevar,aimframe)


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


def establish_sub(top, sub):
    '''creates link between top and sub, both given as id'''
    aims_by_id[top].subs.append(aims_by_id[sub])
    aims_by_id[sub].top = aims_by_id[top]


def load(datafile_name):
    '''loads the data from datafile_name, sets up all the aims and returns the
    sql connection'''
    #try:
    global conn
    conn = sqlite3.connect(DATAFILE_NAME)
    cur = conn.cursor()
    cur.execute(
    'create table if not exists \
    aims(id integer,listname text, name text, done integer, top integer, \
    link text);')
    cur.execute(
    'create table if not exists subs(id integer, child_id integer, list text);')
    #load the main aims
    cur.execute('SELECT listname, id FROM aims WHERE top IS NULL;')
    for row in cur:
        print(row)
        add_aim(row[0],row[1])
    #load the subaims listname,id,text,top
    cur.execute('SELECT listname, id, name, top FROM aims WHERE top IS NOT NULL;')
    for row in cur:
        print(row)
        add_subaim(row[0], row[1], row[2], row[3])
    #load the connections between the aims
    cur.execute('SELECT * FROM subs;')
    for row in cur:
        establish_sub(row[0],row[1])
    #Get highest id
    cur.execute('SELECT MAX(id) FROM aims')
    global highest_id
    try:
        highest_id = cur.fetchall()[0][0]
    except:
        highest_id = 0
    #except:
    #    print("unable to open/load datafile, shutting down...")
    #    exit()


def save(conn,datafile_name):
    '''commit changes and preserve copy of datafile'''
    try:
        shutil.copyfile(
            os.path.join(os.getcwd(),DATAFILE_NAME)
            ,os.path.join(os.getcwd()+DATAFILE_NAME+"_old"))
        conn.commit()
        print("saved successfully")
    except:
        print("unable to save!!!")


#Globals
aims={}
aims_by_id={}
global remove
global conn
highest_id
remove = False
reihenbreite={}

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
,command=lambda:save(conn,DATAFILE_NAME))
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
    #load options to create new subaim of an aim given by ref and listname
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
load(DATAFILE_NAME)
add_aim("lol",100)
add_aim("hallo",101)

#setup resize events
mainframe.bind("<Configure>",cancon)
mainframe.update()
cancon()
root.mainloop()
