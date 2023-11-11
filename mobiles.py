import math
from tkinter import PhotoImage, Canvas

class Mobile:
    def __init__(self, x, y, imageID, canvas) -> None:
        self.x =y
        self.y =y
        self.imageID = imageID
        self.canvas = canvas
        self.xSpeed =0
        self.ySpeed=0
    
    def move(self):
        """This will update the position of the object.

        Returns:
            Boolean: whether the object was moved or not, useful for deciding to redraw it or not.
        """
        if self.xSpeed != 0 or self.ySpeed != 0: 
            self.x += self.xSpeed
            self.y += self.ySpeed
            self.canvas.moveto(self.imageID, math.floor(self.x), math.floor(self.y))
            print(str(self.x) + ", " + str(self.y)) 
    

class Player(Mobile):
    """This is the player class, which the user will control in this space fighter game.
    """
    def __init__(self, x,y, image, canvas, health =3,) -> None:
        super().__init__(x,y,image, canvas)
        # self.x =y
        # self.x =y
        # self.image = image
        self.health =health