#Sprites come from a free asset pack made by Cluly, found here https://cluly.itch.io/space-eaters
#Twitter: @_cluly_

from tkinter import Tk, Canvas, PhotoImage, EventType
from PIL import Image, ImageTk
from mobiles import Player

def doSomething():
    print("something")

def moveLeft(*ignore):
    global player
    player.changeXSpeed(-player.speed)
    print("left detected")
def moveRight(*ignore):
    global player
    player.changeXSpeed(player.speed)
    print("right detected")
def moveUp(*ignore):
    global player
    player.changeYSpeed(-player.speed)
    print("up detected")
def moveDown(*ignore):
    global player
    player.changeYSpeed(player.speed)
    print("down detected")

def moveMobiles():
    global mobiles
    for mob in mobiles:
        mob.move()
        

def update(*ignore):
    global window
    if not paused:
        moveMobiles()
        window.after(10,update)

def fire(event):
    global player
    shotID = canvas.create_oval(player.x+10,player.y+10,player.x+20,player.y+20,fill="yellow")

        

window = Tk()
window.title("Space-Fighter")
canvas = Canvas(window, bg="black", height=864, width=1536)
test = Image.open("crab.jpg") # crab found here https://pixabay.com/photos/crab-beach-sand-crustacean-8258856/
test = test.resize((500,200), Image.LANCZOS) # Not sure how needed LANCZOS is needed, but it's some form of antialias.
test = ImageTk.PhotoImage(test) # Have to convert to PhotoImage to use in the canvas
canvas.pack()
print(canvas.winfo_height())
print(canvas.winfo_width())
crabID = canvas.create_image(20,20,anchor="nw",image=test) # anchor basically says to take a certain part of an image, a corner, edge or center, and make that part of the image appear at the specified coordinates
#coordinates at the beginning are x then y
canvas.create_oval(520,520,530,530,fill="yellow")
mobiles=[]
paused = False
temp = PhotoImage(file="assets/player/player.png") # for some reason I can't just pass it into rhe create_image method
playerImageID = canvas.create_image(766,800,anchor="nw",image= temp)
player = Player(766,800,playerImageID,canvas, temp.height(), temp.width())
mobiles.append(player)


window.bind("a",moveLeft)
window.bind("d",moveRight)
window.bind("s",moveDown)
window.bind("w",moveUp)
window.bind("<KeyRelease-a>",moveRight)
window.bind("<KeyRelease-d>",moveLeft)
window.bind("<KeyRelease-s>",moveUp)
window.bind("<KeyRelease-w>",moveDown)
window.bind("<Button-1>",fire)
window.bind("p",update)

window.mainloop()
