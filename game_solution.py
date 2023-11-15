#Sprites come from a free asset pack made by Cluly, found here https://cluly.itch.io/space-eaters
#Twitter: @_cluly_

import math
from random import randint
from tkinter import Label, Tk, Canvas, PhotoImage, EventType
import tkinter
from PIL import Image, ImageTk
from typing import Dict
from constants import tickDelay
import mobiles

def moveLeft(*ignore):
    global player
    player.changeXSpeed(-player.speed)
def moveRight(*ignore):
    global player
    player.changeXSpeed(player.speed)
def moveUp(*ignore):
    global player
    player.changeYSpeed(-player.speed)
def moveDown(*ignore):
    global player
    player.changeYSpeed(player.speed)

def handleMobs():
    global mobs
    temp = mobs.copy()
    for ID in temp:
        mob = mobs[ID]
        mob.move()
        if mob.health <=0:
            canvas.delete(mob.imageID)
            mobs.pop(ID)
        if isinstance(mob,mobiles.GruntEnemy):
            mob.fire(player.x,player.y,mobs)

def flipPaused(*ignore):
    global paused
    paused = not paused
    tick()

def generateEnemies():
    global enemySpawnCooldown
    if enemySpawnCooldown >0:
        enemySpawnCooldown -=1
    else:
        
        enemyX = randint(canvas.winfo_width() * 3/4, canvas.winfo_width())
        enemyY = randint(0,canvas.winfo_height())
        enemyID = playerImageID = canvas.create_image(enemyX,enemyY,anchor="nw",image= greenEnemyImage)
        enemy = mobiles.GruntEnemy(enemyX,enemyY,enemyID,canvas,greenEnemyImage.height(),greenEnemyImage.width(),math.pi * 1.5)
        mobs[enemyID] = enemy
        enemySpawnCooldown = enemySpawnReset

def tick():
    global window
    if not paused:
        generateEnemies()
        handleMobs()
        window.after(tickDelay(),tick)

def fire(event):
    global mobs
    player.fire(event)


window = Tk()
window.title("Space-Fighter")
window.geometry("1536x864")
window.configure(bg="black")




canvas = Canvas(window, bg="black", height=800, width=1336,borderwidth=0,highlightthickness=0)
canvas.grid(column=3,row=1,rowspan=10)

mobs :  Dict[int,mobiles.Mobile] = {} # This list is useful for keeping track of things that need to have the move function ran on them
paused = True
temp = PhotoImage(file="assets/player/player.png") # for some reason I can't just pass it into rhe create_image method
playerID = canvas.create_image(766,700,anchor="nw",image= temp)
player = mobiles.Player(766,700,playerID,canvas,temp.height(),temp.width(),mobs)
player = mobiles.Player(766,700,playerID,canvas, temp.height(), temp.width(),mobs)
mobs[playerID] = player

greenEnemyImage = enemyImage = PhotoImage(file="assets/enemies/littleGreenEnemy.png")

verticalWall = Image.open("assets/Statics/bigLeftWall.png")
verticalWall = verticalWall.crop( (0, 0, verticalWall.width, int(canvas.cget('height'))) )
leftWall = ImageTk.PhotoImage(verticalWall) # this extra line is ESSENTIAL to making it display. Also this variable can't be overwritten without it breaking. All hail garbage collection
tempLabel = Label(window,image=leftWall,borderwidth=0)
tempLabel.grid(column=2,row=1,rowspan=10,sticky="w")
rightWall = ImageTk.PhotoImage(verticalWall.rotate(180))
tempLabel = Label(window,image=rightWall,borderwidth=0)
tempLabel.grid(column=4,row=1,rowspan=10,sticky="e")

horizontalWall = Image.open("assets/Statics/horizontalWall.png") # keeping the references to an image is ESSENTIAL to making it display. Also this variable can't be overwritten without it breaking. All hail garbage collection
horizontalWall = horizontalWall.crop( (0, 0, int(canvas.cget('width')), horizontalWall.height) )
horizontalWall = ImageTk.PhotoImage(horizontalWall)
tempLabel = Label(window,image=horizontalWall,borderwidth=0)
tempLabel.grid(column=3,row=11,sticky="s")
tempLabel = Label(window,image=horizontalWall,borderwidth=0)
tempLabel.grid(column=3,row=0,sticky="n")

topLeft = PhotoImage(file="assets/Statics/topLeftCorner.png")
tempLabel = Label(window,image=topLeft,borderwidth=0)
tempLabel.grid(column=2,row=0,sticky="s")
topRight  = PhotoImage(file="assets/Statics/topRightCorner.png")
tempLabel = Label(window,image=topRight,borderwidth=0)
tempLabel.grid(column=4,row=0,sticky="nw")
botLeft  = PhotoImage(file="assets/Statics/bottomLeftCorner.png")
tempLabel = Label(window,image=botLeft,borderwidth=0)
tempLabel.grid(column=2,row=11,sticky="sw")
botRight = PhotoImage(file="assets/Statics/bottomRightCorner.png")
tempLabel = Label(window,image=botRight,borderwidth=0)
tempLabel.grid(column=4,row=11,sticky="n")
heart = PhotoImage(file="assets/Statics/heart.png")
heartLabel = Label(window,image=heart,borderwidth=0)
heartLabel.grid(column=1,row=1)
health = Label(window,text="x" + str(player.health),borderwidth=0,font=("Fixedsys",26),bg="black",fg="white")
health.grid(column=0,row=1)


# test = Image.open("crab.jpg") # crab found here https://pixabay.com/photos/crab-beach-sand-crustacean-8258856/
# test = test.resize((500,200), Image.LANCZOS) # Not sure how needed LANCZOS is needed, but it's some form of antialias.
# test = ImageTk.PhotoImage(test) # Have to convert to PhotoImage to use in the canvas
# crabID = canvas.create_image(20,20,anchor="nw",image=test) # anchor basically says to take a certain part of an image, a corner, edge or center, and make that part of the image appear at the specified coordinates
#coordinates at the beginning are x then y






enemySpawnCooldown = 1000 / tickDelay()
enemySpawnReset = enemySpawnCooldown

window.bind("a",moveLeft)
window.bind("d",moveRight)
window.bind("s",moveDown)
window.bind("w",moveUp)
window.bind("<KeyRelease-a>",moveRight)
window.bind("<KeyRelease-d>",moveLeft)
window.bind("<KeyRelease-s>",moveUp)
window.bind("<KeyRelease-w>",moveDown)
window.bind("<Button-1>",fire)
window.bind("p",flipPaused)

window.mainloop()
