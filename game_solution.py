#Sprites come from a free asset pack made by Cluly, found here https://cluly.itch.io/space-eaters
#Twitter: @_cluly_

from tkinter import Tk, Canvas, PhotoImage, EventType
from PIL import Image, ImageTk
from mobiles import Player

def doSomething():
    print("something")

def moveLeft(event):
    global player, window
    player.xSpeed = -5
    print(player)
    print("left detected" + str(player.xSpeed))
    #window.after(5000,doSomething)
    
def moveRight(event):
    global player
    player.xSpeed = 3
    print("right detected")
def moveUp(event):
    global player
    player.ySpeed = -3
    print("up detected")
def moveDown(event):
    global player
    player.ySpeed = 3
    print("down detected")

def moveMobiles():
    global mobiles
    for mob in mobiles:
        print("in the move loop")
        mob.move()
        

def update(*ignore):
    global window
    if not paused:
        moveMobiles()
        print("in update")
        window.after(10,update)

def moveCrab(*ignore):
    global crabID
    global canvas
    canvas.moveto(crabID, 400, 400)
        

window = Tk()
window.title("Space-Fighter")
canvas = Canvas(window, bg="black", height=864, width=1536)
test = Image.open("crab.jpg") # crab found here https://pixabay.com/photos/crab-beach-sand-crustacean-8258856/
test = test.resize((500,200), Image.LANCZOS) # Not sure how needed LANCZOS is needed, but it's some form of antialias.
test = ImageTk.PhotoImage(test) # Have to convert to PhotoImage to use in the canvas
canvas.pack()
crabID = canvas.create_image(20,20,anchor="nw",image=test) # anchor basically says to take a certain part of an image, a corner, edge or center, and make that part of the image appear at the specified coordinates
#coordinates at the beginning are x then y

mobiles=[]
paused = False
temp = PhotoImage(file="assets/player/player.png") # for some reason I can't just pass it into rhe create_image method
playerImageID = canvas.create_image(766,800,anchor="nw",image= temp)
player = Player(760,800,playerImageID,canvas)
mobiles.append(player)

window.bind("a",moveLeft)
window.bind("d",moveRight)
window.bind("s",moveDown)
window.bind("w",moveUp)
window.bind("p",update)
window.bind("m",moveCrab)

window.mainloop()
