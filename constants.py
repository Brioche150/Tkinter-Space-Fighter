"""This module will just store constants that I have to keep across the game
"""

from tkinter import Canvas, Tk

def tickDelay(): # This should be used for anything that ou want to keep consistent with timings. So that's things like cooldowns, movement speed, etc
    return 10

def window():
    return myWindow

def canvas():
    return myCanvas
def mobs():
    return myMobs
def mobileTag():
    return "mobileTag"
def cheats():
    return myCheats
def setCheats(cheats):
    myCheats = cheats

myWindow = Tk()
myWindow.title("Space-Fighter")
myWindow.geometry("1536x864")
myWindow.configure(bg="black")
    
myCanvas = Canvas(myWindow, bg="black", height=760, width=1336,borderwidth=0,highlightthickness=0)
myCanvas.grid(column=3,row=1,rowspan=10)
myMobs = {}
myCheats={"mark grayson":False,"i show meat":False, "Boogie": False, "brrrt": False}


