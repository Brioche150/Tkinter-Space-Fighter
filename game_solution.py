#Sprites come from a free asset pack made by Cluly, found here https://cluly.itch.io/space-eaters
#Twitter: @_cluly_
"""This is the main game module that will handle the setup of the game, and keep running ticks to update the state of the game. 
    """
import math
from random import randint
from tkinter import Label, Tk, Canvas, PhotoImage, EventType
from PIL import Image, ImageTk
from typing import Dict
from constants import tickDelay, window, canvas, mobs
import mobiles

def moveLeft(*ignore):
    player.changeXSpeed(-player.speed)
def moveRight(*ignore):
    player.changeXSpeed(player.speed)
def moveUp(*ignore):
    player.changeYSpeed(-player.speed)
def moveDown(*ignore):
    player.changeYSpeed(player.speed)

def handleMobs():
    """This gets called with every tick, and it makes all of the mobs update their state as needed.
    """
    global score, paused
    temp = mobs.copy()
    for ID in temp:
        mob = temp[ID]
        mob.move()
        # if mob.health <=0:
        #     if isinstance(mob,mobiles.GruntEnemy):
        #         score +=1
        #         scoreLabel.config(text = "Score:\n" + str(score))
        #     canvas.delete(mob.imageID)
        #     mobs.pop(ID)
        if isinstance(mob,mobiles.GruntEnemy):
            mob.fire(player.x,player.y)
    if player.health <=0:
        paused = True
        window.unbind_all("p") #Normal unbind requires you to pass a functionID as well, but I'll only ever have one function bound to this anyway. May need it for mouse clicks though

def pause(event):
    global paused
    if not paused:
        paused = True
        canvas.move(pauseMenu,-2000,0)
        canvas.tag_raise(pauseMenu)

def unpause(event):
    global paused
    if paused:
        paused = False
        canvas.move(pauseMenu,2000,0)
        tick()

def generateEnemies():
    global enemySpawnCooldown
    if enemySpawnCooldown >0:
        enemySpawnCooldown -=1
    else:
        enemyX = randint(canvas.winfo_width() * 3/4, canvas.winfo_width())
        enemyY = randint(0,canvas.winfo_height())
        enemyID =  canvas.create_image(enemyX,enemyY,anchor="nw",image= greenEnemyImage)
        enemy = mobiles.GruntEnemy(enemyX,enemyY,enemyID,greenEnemyImage.height(),greenEnemyImage.width(),math.pi * 1.5)
        mobs[enemyID] = enemy
        enemySpawnCooldown = enemySpawnReset

def tick():
    """This is the key function that has to be called to allow the game to be played
    """
    if not paused:
        generateEnemies()
        handleMobs()
        window.after(tickDelay(),tick)

def fire(event):
    if not paused and player.health >0:
        global mobs
        player.fire(event)

def removeLeaderboard(event):
    canvas.delete(leaderboard)

def showLeaderboard(event):
    #This generates a new leaderboard every time because it could change, I can't just move it off screen
    scoreRead = open("leaderboard.txt", "r")
    scoreString =""
    for line in scoreRead:
        scoreString += line
    
    #This code generates the text, and then generates outlines that go around the text using bounding boxes.
    scores = canvas.create_text(5*(canvas.winfo_width()//6), canvas.winfo_height()//2,text=scoreString,font="Fixedsys 36",fill="white",tags=("leaderboardContent",leaderboard)) 
    scoresBBox = canvas.bbox(scores)
    leaderboardExit = canvas.create_text(scoresBBox[0] - 30,scoresBBox[1] - 30, text="X", font="Fixedsys 44",fill="white",tags=("leaderboardContent",leaderboard,"exitLeaderboard"))
    exitBBox = canvas.bbox(leaderboardExit)
    exitOutline = canvas.create_rectangle(exitBBox,fill="black",outline="red",tags=("outline",leaderboard,"exitLeaderboard"))
    overallBBox = canvas.bbox(leaderboardExit,scores)
    
    overallOutline = canvas.create_rectangle(overallBBox[0]-5,overallBBox[1]-5,overallBBox[2] +30 ,overallBBox[3] + 30,outline="white",fill="black",tags=("outline",leaderboard))
    
    canvas.tag_raise(exitOutline,overallOutline)
    canvas.tag_raise("leaderboardContent","outline") # the way raise and lower work is that it raises the first thing, over the second thing given
    canvas.tag_bind("exitLeaderboard","<Button-1>",removeLeaderboard)
    scoreRead.close()
    
    
def start(event):
    window.unbind("KeyPress")
    window.bind("a",moveLeft)
    window.bind("d",moveRight)
    window.bind("s",moveDown)
    window.bind("w",moveUp)
    window.bind("<KeyRelease-a>",moveRight)
    window.bind("<KeyRelease-d>",moveLeft)
    window.bind("<KeyRelease-s>",moveUp)
    window.bind("<KeyRelease-w>",moveDown)
    window.bind("<Button-1>",fire)
    window.bind("p",pause)
    startScreen.destroy()
    startText.destroy()
    
    backgroundBlock = canvas.create_rectangle(canvas.winfo_width()//3, 30, 2*(canvas.winfo_width()//3),canvas.winfo_height()-30,fill="black",tags=(pauseMenu),outline="white")
    
    startX = canvas.winfo_width()//3 +10
    startY = 40
    
    blockHeight = canvas.winfo_height()//3 - 40
    blockWidth = canvas.winfo_width()//3 - 20
    
    resumeBlock = canvas.create_rectangle(startX, startY, startX + blockWidth, startY + blockHeight,fill="black",outline="white",tags=(pauseMenu,resume))
    resumeText = canvas.create_text(startX + blockWidth//2, startY + blockHeight//2,tags=(pauseMenu,resume),text="Resume",font="Fixedsys 36",fill="white")
    startY += blockHeight 
    
    leaderboardBlock = canvas.create_rectangle(startX, startY, startX + blockWidth, startY + blockHeight,fill="black",outline="white",tags=(pauseMenu,leaderboardButton))
    leaderboardText = canvas.create_text(startX + blockWidth//2, startY + blockHeight//2,tags=(pauseMenu,leaderboardButton),text="leaderboard",font="Fixedsys 36",fill="white")
    startY += blockHeight
    
    
    
    
    canvas.tag_raise(pauseMenu)
    canvas.tag_raise(resumeText,leaderboardButton)
    canvas.tag_bind(resume,"<Button-1>",unpause)
    canvas.tag_bind(leaderboardButton,"<Button-1>",showLeaderboard)

window = window()
canvas = canvas()


mobs : Dict[int, mobiles.Mobile]= mobs() # This list is useful for keeping track of things that need to have the move function ran on them
paused = True
playerImage = PhotoImage(file="assets/player/player.png") # I can't just pass this in the create_image method because the reference tp the image has to stay to not get eaten by garbage collection
playerID = canvas.create_image(766,700,anchor="nw",image= playerImage)
player = mobiles.Player(766,700,playerID,playerImage.height(),playerImage.width())
player = mobiles.Player(766,700,playerID, playerImage.height(), playerImage.width())
mobs[playerID] = player

greenEnemyImage = enemyImage = PhotoImage(file="assets/enemies/littleGreenEnemy.png")

verticalWall = Image.open("assets/statics/bigLeftWall.png")
verticalWall = verticalWall.crop( (0, 0, verticalWall.width, int(canvas.cget('height'))) )
leftWall = ImageTk.PhotoImage(verticalWall) # this extra line is ESSENTIAL to making it display. Also this variable can't be overwritten without it breaking. All hail garbage collection
tempLabel = Label(window,image=leftWall,borderwidth=0)
tempLabel.grid(column=2,row=1,rowspan=10,sticky="w")
rightWall = ImageTk.PhotoImage(verticalWall.rotate(180))
tempLabel = Label(window,image=rightWall,borderwidth=0)
tempLabel.grid(column=4,row=1,rowspan=10,sticky="e")

horizontalWall = Image.open("assets/statics/horizontalWall.png") # keeping the references to an image is ESSENTIAL to making it display. Also this variable can't be overwritten without it breaking. All hail garbage collection
horizontalWall = horizontalWall.crop( (0, 0, int(canvas.cget('width')), horizontalWall.height) )
horizontalWall = ImageTk.PhotoImage(horizontalWall)
tempLabel = Label(window,image=horizontalWall,borderwidth=0)
tempLabel.grid(column=3,row=11,sticky="s")
tempLabel = Label(window,image=horizontalWall,borderwidth=0)
tempLabel.grid(column=3,row=0,sticky="n")

topLeft = PhotoImage(file="assets/statics/topLeftCorner.png")
tempLabel = Label(window,image=topLeft,borderwidth=0)
tempLabel.grid(column=2,row=0,sticky="s")
topRight  = PhotoImage(file="assets/statics/topRightCorner.png")
tempLabel = Label(window,image=topRight,borderwidth=0)
tempLabel.grid(column=4,row=0,sticky="nw")
botLeft  = PhotoImage(file="assets/statics/bottomLeftCorner.png")
tempLabel = Label(window,image=botLeft,borderwidth=0)
tempLabel.grid(column=2,row=11,sticky="sw")
botRight = PhotoImage(file="assets/statics/bottomRightCorner.png")
tempLabel = Label(window,image=botRight,borderwidth=0)
tempLabel.grid(column=4,row=11,sticky="n")
heart = PhotoImage(file="assets/statics/heart.png")
heartLabel = Label(window,image=heart,borderwidth=0)
heartLabel.grid(column=1,row=1)

#Fixedsys makes a cool pixel font in wondows, I can't find one for Linux though
healthLabel = Label(window,text="x" + str(player.health),borderwidth=0,font=("Fixedsys",26),bg="black",fg="white")
healthLabel.grid(column=0,row=1)
scoreLabel =Label(window,text="Score:\n0",borderwidth=0,font=("Fixedsys",23),bg="black",fg="white")
scoreLabel.grid(column=0,row=2,columnspan=2,rowspan=2)
player.healthLabel = healthLabel
player.scoreLabel = scoreLabel





# test = Image.open("crab.jpg") # crab found here https://pixabay.com/photos/crab-beach-sand-crustacean-8258856/
# test = test.resize((500,200), Image.LANCZOS) # Not sure how needed LANCZOS is needed, but it's some form of antialias.
# test = ImageTk.PhotoImage(test) # Have to convert to PhotoImage to use in the canvas
# crabID = canvas.create_image(20,20,anchor="nw",image=test) # anchor basically says to take a certain part of an image, a corner, edge or center, and make that part of the image appear at the specified coordinates
#coordinates at the beginning are x then y

pauseMenu = "pauseMenu"
resume = "resume"
leaderboardButton= "leaderboardButton"
leaderboard = "leaderboard"

enemySpawnCooldown = 1000 / tickDelay()
enemySpawnReset = enemySpawnCooldown
score =0


window.bind("<KeyPress>",start)

startScreen = Label(window,borderwidth=999,bg="black")
startScreen.place(x=1536//2,y=864//2,anchor="center")
startText = Label(window,text="Press any button to start" ,font=("Fixedsys",50),borderwidth=20,bg="black",fg="white")
startText.place(x=1536//2,y=864//2,anchor="center")
window.mainloop()
