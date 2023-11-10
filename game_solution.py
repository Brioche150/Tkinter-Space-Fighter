#Sprites come from a free asset pack made by Cluly, found here https://cluly.itch.io/space-eaters
#Twitter: @_cluly_

from tkinter import Tk, Canvas, PhotoImage
from PIL import Image, ImageTk
from mobiles import Player

def move_mobiles():
    pass

window = Tk()
window.title("Space-Fighter")
canvas = Canvas(window, bg="black", height=864, width=1536)
test = Image.open("crab.jpg") # crab found here https://pixabay.com/photos/crab-beach-sand-crustacean-8258856/
test = test.resize((500,200), Image.LANCZOS) # Not sure how needed LANCZOS is needed, but it's some form of antialias.
test = ImageTk.PhotoImage(test) # Have to convert to PhotoImage to use in the canvas
canvas.pack()
canvas.create_image(20,20,anchor="nw",image=test) # anchor basically says to take a certain part of an image, a corner, edge or center, and make that part of the image appear at the specified coordinates
#coordinates at the beginning are x then y

player = Player(x=760,y=800, image=PhotoImage(file="assets/player/player_boost.png"))
canvas.create_image(player.x,player.y,anchor="nw",image=player.image)

window.mainloop()