#Sprites come from a free asset pack made by Cluly, found here https://cluly.itch.io/space-eaters
#Twitter: @_cluly_
"""This is the main game module that will handle the setup of the game, and keep running ticks to update the state of the game. 
    Screen resolution is 1536 x 864
    """
import json
import math
from random import randint
from textwrap import fill
from tkinter import END, Button, Entry, Label, Tk, Canvas, PhotoImage, EventType
from PIL import Image, ImageTk
from typing import Dict
from constants import tickDelay, window, canvas, mobs, mobileTag
import mobiles

def moveLeft(*ignore):
    player.changeXSpeed(-player.speed)
def moveRight(*ignore):
    player.changeXSpeed(player.speed)
def moveUp(*ignore):
    player.changeYSpeed(-player.speed)
def moveDown(*ignore):
    player.changeYSpeed(player.speed)

def submit():
    name = entry.get()[:3].upper() # First three letters that the user enters
    with open("leaderboard.txt") as file:
        leaderboardString = ""
        for line in file:
            score = int(line.split(" ")[1]) # This gets the score, since the score comes after a space
            if player.score > score:
                
                dotIndex = line.find(".")
                newLine = line[:dotIndex + 1] # This copies the number into the new line
                newLine += name
                newLine += " " * (3-len(name)) #Makes sure that 3 character's space is used up if their name is less than 3 letters
                newLine += ": " + str(player.score) + "\n"
                
                leaderboardString += newLine
                player.score=score # This makes it step through and act like the person that just got removed just got that score, so cascades down the list
                name = line[dotIndex+1:dotIndex +4]
            else:
                leaderboardString += line
    with open("leaderboard.txt","w") as file:
        file.write(leaderboardString)
    
    
    
    canvas.delete(GOWindowTag)
    canvas.tag_lower(gameOverTag)
    canvas.tag_raise(menuTag)
    canvas.tag_raise(startTag,resumeTag)
    canvas.tag_lower(onlyPausedTag)
    
    
def gameOver():
    
    #all these unbinds are to get rid of the erorrs of "there is no instance of player" when it doesn't really matter either way.
    window.unbind("a")
    window.unbind("d")
    window.unbind("s")
    window.unbind("w")
    window.unbind("<KeyRelease-a>")
    window.unbind("<KeyRelease-d>")
    window.unbind("<KeyRelease-s>")
    window.unbind("<KeyRelease-w>")
    window.unbind("<Button-1>")
    
    entry.delete(0,END)
    canvas.create_window(canvas.winfo_width()//2,240,window = entry,tags=(gameOverTag,GOWindowTag))
    canvas.create_window(canvas.winfo_width()//2,320,window=buttonSubmit,tags=(gameOverTag,GOWindowTag))
    canvas.tag_raise(gameOverTag)

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
        window.unbind("p")
        gameOver()
        
def pause(*ignore):
    global paused
    if not paused:
        paused = True
        canvas.tag_raise(menuTag)
        canvas.tag_raise(onlyPausedTag)

def unpause(*ignore):
    global paused
    if paused:
        paused = False
        canvas.tag_lower(menuTag)
        tick()

def generateEnemies():
    global enemySpawnCooldown
    if enemySpawnCooldown >0:
        enemySpawnCooldown -=1
    else:
        enemyX = randint(canvas.winfo_width() * 3/4, canvas.winfo_width())
        enemyY = randint(0,canvas.winfo_height())
        enemyID =  canvas.create_image(enemyX,enemyY,anchor="nw",image= greenEnemyImage,tags=mobileTag())
        enemy = mobiles.GruntEnemy(enemyX,enemyY,enemyID,greenEnemyImage.height(),greenEnemyImage.width(),math.pi * 1.5)
        mobs[enemyID] = enemy
        enemySpawnCooldown = enemySpawnReset

def tick():
    """This is the key function that has to be called to allow the game to be played
    """
    if not paused:
        generateEnemies()
        handleMobs()
        if canvas.coords(background)[0] == -2988: # This sets the background back to the beginning if it's scrolled too far
            canvas.moveto(background,0,0)
        else:
            canvas.move(background,-1,0)# Makes a cool scrolling effect. 
        
        window.after(tickDelay(),tick)

def fire(event):
    if not paused and player.health >0:
        global mobs
        player.fire(event)

def saveGame(event):
    dictList = []
    for ID in mobs:
        mob = mobs[ID]
        mobInfo = {}
        mobInfo["type"] = str(type(mob))
        mobInfo.update(mob.__dict__)
        if "Player" in mobInfo["type"]: # This makes sure player is saved first, so that projectiles can have their player attribute set correctly.
            dictList.insert(0,mobInfo)
        else:
            dictList.append(mobInfo)
        
    with open("gameSave.txt","w") as file:
        file.write(json.dumps(dictList,default= lambda obj: None))

def loadGame(event):
    with open("gameSave.txt","r") as file:   
        fileContents = file.read()
        if len(fileContents) ==0:
            startGame(event)
            print("There is no game save to be loaded")
        else:
            for ID in mobs: #Just clears out all of the enemies on the canvas
                canvas.delete(ID)
            mobs.clear()
            global playerID, player,paused,enemySpawnCooldown,enemySpawnReset
            
            enemySpawnCooldown = 1000 / tickDelay()
            enemySpawnReset = enemySpawnCooldown
            
            dictList = json.loads(fileContents) # Making my classes serializable would make this a good bit easier, but I'm not sure how to do that.
            for dict in dictList:
                type = dict["type"]
                if "Player" in type:
                    playerID = canvas.create_image(dict["x"],dict["y"], anchor="nw",image= playerImage,tags=mobileTag())
                    player = mobiles.Player(dict["x"],dict["y"],playerID,dict["height"],dict["width"],dict["speed"],dict["health"],dict["score"])
                    mobs[playerID] = player
                elif "Projectile" in type:
                    projectileID = canvas.create_oval(dict["x"],dict["y"],dict["x"]+dict["width"],dict["y"]+dict["height"], fill=dict["colour"],tags = mobileTag())
                    projectile = mobiles.Projectile(dict["x"],dict["y"],projectileID,dict["height"],dict["width"],dict["direction"],speed=dict["speed"],health=dict["health"],isEnemy=dict["isEnemy"],colour=dict["colour"])
                    if not dict["isEnemy"]:
                        projectile.player = player
                    mobs[projectileID] = projectile
                    #projectile.updateSpeedsFromDirection()
                elif "GruntEnemy" in type:
                    enemyID =  canvas.create_image(dict["x"],dict["y"],anchor="nw",image= greenEnemyImage,tags=mobileTag())
                    enemy = mobiles.GruntEnemy(dict["x"],dict["y"],enemyID,dict["height"],dict["width"],dict["direction"],speed=dict["speed"],shotCooldown=dict["shotCooldownReset"] * tickDelay(),turnCooldown=dict["turnCooldownReset"] * tickDelay())
                    mobs[enemyID] = enemy
                    #enemy.updateSpeedsFromDirection()
                
            healthLabel.config(text="x" + str(player.health))
            scoreLabel.config(text="Score:\n" + str(player.score))
            player.healthLabel = healthLabel
            player.scoreLabel = scoreLabel
            
            unpause(event)
                


def removeLeaderboard(event):
    canvas.delete(leaderboardTag)


def showLeaderboard(event):
    #This generates a new leaderboard every time because it could change, I can't just move it off screen
    scoreRead = open("leaderboard.txt", "r")
    scoreString =""
    for line in scoreRead:
        scoreString += line
    
    #This code generates the text, and then generates outlines that go around the text using bounding boxes.
    scores = canvas.create_text(5*(canvas.winfo_width()//6), canvas.winfo_height()//2,text=scoreString,font="Fixedsys 36",fill="white", tags=("leaderboardContent",leaderboardTag,menuTag)) 
    scoresBBox = canvas.bbox(scores)
    leaderboardExit = canvas.create_text(scoresBBox[0] - 30,scoresBBox[1] - 30, text="X", font="Fixedsys 44",fill="white",tags=("leaderboardContent",leaderboardTag,"exitLeaderboard",menuTag))
    exitBBox = canvas.bbox(leaderboardExit)
    exitOutline = canvas.create_rectangle(exitBBox,fill="black",outline="red",tags=("outline",leaderboardTag,"exitLeaderboard",menuTag))
    overallBBox = canvas.bbox(leaderboardExit,scores)
    
    overallOutline = canvas.create_rectangle(overallBBox[0]-5,overallBBox[1]-5,overallBBox[2] +30 ,overallBBox[3] + 30,outline="white",fill="black",tags=("outline",leaderboardTag,menuTag))
    
    canvas.tag_raise(exitOutline,overallOutline)
    canvas.tag_raise("leaderboardContent","outline") # the way raise and lower work is that it raises the first thing, over the second thing given
    canvas.tag_bind("exitLeaderboard","<Button-1>",removeLeaderboard)
    scoreRead.close()

def startGame(event):
    """This function will reset the game to be played again, or just for the first time
    """
    
    
    
    for ID in mobs: #Just clears out all of the enemies on the canvas
        canvas.delete(ID)
    mobs.clear()
    global playerID, player,paused,enemySpawnCooldown,enemySpawnReset
    
    enemySpawnCooldown = 1000 / tickDelay()
    enemySpawnReset = enemySpawnCooldown
    
    playerID = canvas.create_image(canvas.winfo_width()//3,canvas.winfo_height()//2, anchor="nw",image= playerImage,tags=mobileTag())
    player = mobiles.Player(canvas.winfo_width()//3,canvas.winfo_height()//2, playerID,playerImage.height(),playerImage.width())
    mobs[playerID] = player

    
    healthLabel.config(text="x" + str(player.health))
    scoreLabel.config(text="Score:\n0")
    player.healthLabel = healthLabel
    player.scoreLabel = scoreLabel
    
    window.unbind("<KeyRelease>")
    window.bind("a",moveLeft )
    window.bind("d",moveRight )
    window.bind("s",moveDown )
    window.bind("w",moveUp )
    window.bind("<KeyRelease-a>",moveRight )
    window.bind("<KeyRelease-d>",moveLeft )
    window.bind("<KeyRelease-s>",moveUp )
    window.bind("<KeyRelease-w>",moveDown )
    window.bind("<Button-1>",fire)
    window.bind("p",pause)
    
    
    canvas.tag_raise(resumeTag,startTag)
    unpause()

def start(event):
    """This function could all be put in main, except the canvas dimensions wouldn't exist then, so it has to be in a function after an event has happened and the mainloop has given the canvas dimensions.
    """
    
    startScreen.destroy()
    startText.destroy()
    
    #This will make a start/pause menu, since they have elements in common. So on top, there's a start / resume button for the start and pause menu respectively
    #Then there's the leaderboard, which is the same for both.
    
    backgroundBlock = canvas.create_rectangle(canvas.winfo_width()//3, 30, 2*(canvas.winfo_width()//3),canvas.winfo_height()-30,fill="black",tags=menuTag,outline="white")
    
    startX = canvas.winfo_width()//3 +10
    startY = 40
    
    blockHeight = canvas.winfo_height()//5 - 40
    blockWidth = canvas.winfo_width()//3 - 20
    
    #These make the resume block
    canvas.create_rectangle(startX, startY, startX + blockWidth, startY + blockHeight,fill="black",outline="white",tags=(menuTag,resumeTag))
    canvas.create_text(startX + blockWidth//2, startY + blockHeight//2,text="Resume",font="Fixedsys 32",fill="white",tags=(menuTag,resumeTag))
    
    #These make the start block, in the same place, since one will just be in front of the other
    canvas.create_rectangle(startX, startY, startX + blockWidth, startY + blockHeight,fill="black",outline="white",tags=(menuTag,startTag))
    canvas.create_text(startX + blockWidth//2, startY + blockHeight//2,text="Start New Game",font="Fixedsys 32",fill="white",tags=(menuTag,startTag))
    
    
    startY += blockHeight +10
    #Makes the leaderboard button
    canvas.create_rectangle(startX, startY, startX + blockWidth, startY + blockHeight,fill="black",outline="white",tags=(menuTag,leaderboardButtonTag))
    canvas.create_text(startX + blockWidth//2, startY + blockHeight//2,text="leaderboard",font="Fixedsys 32",fill="white",tags=(menuTag,leaderboardButtonTag))
    
    startY += blockHeight +10
    #Makes the load game button
    canvas.create_rectangle(startX, startY, startX + blockWidth, startY + blockHeight,fill="black",outline="white",tags=(menuTag,loadTag))
    canvas.create_text(startX + blockWidth//2, startY + blockHeight//2,text="Load Game",font="Fixedsys 32",fill="white",tags=(menuTag,loadTag))
    
    startY += blockHeight +10
    #Makes the save game button
    canvas.create_rectangle(startX, startY, startX + blockWidth, startY + blockHeight,fill="black",outline="white",tags=(menuTag,saveTag,onlyPausedTag))
    canvas.create_text(startX + blockWidth//2, startY + blockHeight//2,text="Save Game",font="Fixedsys 32",fill="white",tags=(menuTag,saveTag,onlyPausedTag))
    
    startY += blockHeight +10
    #Makes the restart button
    canvas.create_rectangle(startX, startY, startX + blockWidth, startY + blockHeight,fill="black",outline="white",tags=(menuTag,restartTag,onlyPausedTag))
    canvas.create_text(startX + blockWidth//2, startY + blockHeight//2,text="Restart Game",font="Fixedsys 32",fill="white",tags=(menuTag,restartTag,onlyPausedTag))
    
    
    #Making the game over block
    canvas.create_rectangle(canvas.winfo_width()//4,40,3* canvas.winfo_width()//4,canvas.winfo_height() -40,fill="black",outline="white",tags=gameOverTag)
    canvas.create_text(canvas.winfo_width()//2,90,text="Game Over!",font= "Fixedsys 48",fill="white",tags=gameOverTag)
    canvas.create_text(canvas.winfo_width()//2,160,text="Name (Three letters) ",font= "Fixedsys 32",fill="white",tags=gameOverTag)
    #There are windows made after this, but they have to keep getting deleted and remade in the game over code, because they go in front of everything
    
    canvas.tag_lower(gameOverTag)
    
    canvas.tag_raise(menuTag)
    canvas.tag_raise(startTag,resumeTag)
    canvas.tag_lower(onlyPausedTag)
    canvas.tag_bind(resumeTag,"<Button-1>",unpause)
    canvas.tag_bind(startTag,"<Button-1>",startGame)
    canvas.tag_bind(saveTag,"<Button-1>",saveGame)
    canvas.tag_bind(loadTag,"<Button-1>",loadGame)
    canvas.tag_bind(restartTag,"<Button-1>",startGame) # Pulling a bit of a sneaky here. Restarting does the same thing as startGame does
    canvas.tag_bind(leaderboardButtonTag,"<Button-1>",showLeaderboard)

window = window()
canvas = canvas()

backgroundImage = PhotoImage(file="assets/background.png")
background = canvas.create_image(0,0,anchor="nw",image= backgroundImage)
canvas.tag_lower(background)

mobs : Dict[int, mobiles.Mobile]= mobs() # This list is useful for keeping track of things that need to have the move function ran on them
playerImage = PhotoImage(file="assets/player/player.png") # I can't just pass this in the create_image method because the reference tp the image has to stay to not get eaten by garbage collection
paused = True

playerID : int
player : mobiles.Player

# playerImage = PhotoImage(file="assets/player/player.png") # I can't just pass this in the create_image method because the reference tp the image has to stay to not get eaten by garbage collection
# playerID = canvas.create_image(766,700,anchor="nw",image= playerImage)
# player = mobiles.Player(766,700,playerID,playerImage.height(),playerImage.width())
# mobs[playerID] = player

greenEnemyImage = PhotoImage(file="assets/enemies/littleGreenEnemy.png")

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
healthLabel = Label(window,borderwidth=0,font=("Fixedsys",26),bg="black",fg="white")
healthLabel.grid(column=0,row=1)
scoreLabel =Label(window,borderwidth=0,font=("Fixedsys",23),bg="black",fg="white")
scoreLabel.grid(column=0,row=2,columnspan=2,rowspan=2)






# test = Image.open("crab.jpg") # crab found here https://pixabay.com/photos/crab-beach-sand-crustacean-8258856/
# test = test.resize((500,200), Image.LANCZOS) # Not sure how needed LANCZOS is needed, but it's some form of antialias.
# test = ImageTk.PhotoImage(test) # Have to convert to PhotoImage to use in the canvas
# crabID = canvas.create_image(20,20,anchor="nw",image=test) # anchor basically says to take a certain part of an image, a corner, edge or center, and make that part of the image appear at the specified coordinates
#coordinates at the beginning are x then y

#Just collecting tags here in case I change them, and to avoid typos. 
menuTag = "menuTag"
resumeTag = "resume"
leaderboardButtonTag= "leaderboardButton"
leaderboardTag = "leaderboard"
startTag = "start"
gameOverTag = "gameOver"
GOWindowTag = "GameOverWindowTag"
restartTag = "restartTag"
onlyPausedTag = "onlyPausedTag" #this is here to lower elements in the menu that should only be there when the game is paused, and not there when the game is over
loadTag = "loadTag"
saveTag = "saveTag"

enemySpawnCooldown = 1000 / tickDelay()
enemySpawnReset = enemySpawnCooldown
score =0

#Making the gameOver elements
entry = Entry(window,bg="black",font=("Fixedsys",32),fg="white")
buttonSubmit = Button(window,command=submit,text="submit",bg="black",font=("Fixedsys",32),fg="white")



window.bind("<KeyRelease>",start) # Bit of cheating here, because otherwise there's issues of using a movement key making you start off moving in the wrong direction because of the keyrelease code.



startScreen = Label(window,borderwidth=999,bg="black")
startScreen.place(x=1536//2,y=864//2,anchor="center")
startText = Label(window,text="Press any key to start" ,font=("Fixedsys",50),borderwidth=20,bg="black",fg="white")
startText.place(x=1536//2,y=864//2,anchor="center")
window.mainloop()
