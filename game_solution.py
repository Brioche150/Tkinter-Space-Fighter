#Sprites come from a free asset pack made by Cluly, found here https://cluly.itch.io/space-eaters
#Twitter: @_cluly_

import math
from tkinter import Label, Tk, Canvas, PhotoImage, EventType
from PIL import Image, ImageTk
from numpy import sign
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

def tick():
    global window
    if not paused:
        handleMobs()
        window.after(10,tick)

def fire(event):
    global mobs
    player.fire(event)
#     global mobs, player
#     mobs.append(player.fire(event))
#     x = player.x+10
#     y = player.y+10
#     shotID = canvas.create_oval(x,y,x+10,y+10,fill="yellow")
    
#     dx = event.x - x
#     dy =  y - event.y # flipped around from the other one, to make it like a normal coordinate system
    
#     if(dy == 0):
#         direction = math.pi/2 + (((-sign(dx) + 1)/2) * math.pi) # This is here to avoid zero division errors.
#     else:
#         direction = math.atan(dx/dy)# this calculates the bearing based on the vector between the mouse click and the shot when it spawns
#         if dy < 0:
#             direction += math.pi
#         elif dx < 0:
#             direction += 2 * math.pi
#     shot = mobiles.Projectile(x,y,shotID,canvas,10,10,direction,isEnemy=False)
#     mobs.append(shot)
    
    

        

window = Tk()
window.title("Space-Fighter")
window.geometry("1536x864")
window.configure(bg="black")

test = Image.open("crab.jpg") # crab found here https://pixabay.com/photos/crab-beach-sand-crustacean-8258856/
test = test.resize((500,200), Image.LANCZOS) # Not sure how needed LANCZOS is needed, but it's some form of antialias.
test = ImageTk.PhotoImage(test) # Have to convert to PhotoImage to use in the canvas
#crabID = canvas.create_image(20,20,anchor="nw",image=test) # anchor basically says to take a certain part of an image, a corner, edge or center, and make that part of the image appear at the specified coordinates
#coordinates at the beginning are x then y


canvas = Canvas(window, bg="black", height=800, width=1336,borderwidth=0,highlightthickness=0)
canvas.grid(column=2,row=1,rowspan=10)
leftWall = Image.open("assets/Statics/bigLeftWall.png")
#leftWall = leftWall.crop( (0, 0, leftWall.width, int(canvas.cget('height'))) )
#leftWall.configure(height=int(canvas.cget('height')))
tempImage = ImageTk.PhotoImage(leftWall)
tempLabel = Label(window,image=tempImage,borderwidth=0)
tempLabel.grid(column=1,row=1,rowspan=10)
tempLabel = Label(window,image=PhotoImage(leftWall.rotate(180)),borderwidth=0)
tempLabel.grid(column=3,row=1,rowspan=10)

# rightWall = PhotoImage(file="assets/Statics/rightWallPanel.png")


# print(int(824 / leftWall.height()))
# for i in range(1,int(int(canvas.cget('height')) / leftWall.height()) +1):
#     tempLabel = Label(window,image=leftWall,borderwidth=0)
#     tempLabel.grid(column=1,row=i)
#     tempLabel = Label(window,image=rightWall,borderwidth=0)
#     tempLabel.grid(column=3,row=i)


# #canvas.pack(side="top")



# #topLeftCorner = PhotoImage(file="assets/Statics/topLeftCorner.png") 
# topLeftCorner=Image.open("assets/Statics/topLeftCorner.png")

 
# tempLabel = Label(window,image=PhotoImage(topLeftCorner),borderwidth=0)
# tempLabel.grid(column=1,row=0)
# tempLabel = Label(window,image=PhotoImage(topLeftCorner.rotate(270)),borderwidth=0)
# tempLabel.grid(column=3,row=0)
# tempLabel = Label(window,image=PhotoImage(topLeftCorner.rotate(180)),borderwidth=0)
# tempLabel.grid(column=3,row=0)




mobs : dict[int,mobiles.Mobile] = {} # This list is useful for keeping track of things that need to have the move function ran on them
paused = True
temp = PhotoImage(file="assets/player/player.png") # for some reason I can't just pass it into rhe create_image method
playerID = canvas.create_image(766,800,anchor="nw",image= temp)
player = mobiles.Player(766,800,playerID,canvas, temp.height(), temp.width(),mobs)
mobs[playerID] = player

enemyImage = PhotoImage(file="assets/enemies/littleGreenEnemy.png")
enemyID = playerImageID = canvas.create_image(1066,500,anchor="nw",image= enemyImage)
enemy = mobiles.GruntEnemy(1066,500,enemyID,canvas,enemyImage.height(),enemyImage.width(),math.pi * 1.5)
mobs[enemyID] = enemy

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
