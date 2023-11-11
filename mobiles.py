import math
from tkinter import PhotoImage, Canvas

def keepInBounds(num,min,max):
        if num < min:
            num = min
        elif num > max:
            num = max
        return num

class Mobile:
    def __init__(self, x, y, imageID, canvas, height, width, speed = 10) -> None:
        self.x =y
        self.y =y
        self.imageID = imageID
        self.canvas = canvas
        self.xSpeed =0
        self.ySpeed=0
        self.speed = speed
        self.height = height
        self.width = width
    
    
    
    def move(self):
        """This will update the position of the object.

        Returns:
            Boolean: whether the object was moved or not, useful for deciding to redraw it or not.
        """
        if self.xSpeed != 0 or self.ySpeed != 0: 
            self.x += self.xSpeed
            self.x = keepInBounds(self.x,0,self.canvas.winfo_width() - self.width)

            self.y += self.ySpeed
            self.y = keepInBounds(self.y,0,self.canvas.winfo_height() -self.height)
            self.canvas.moveto(self.imageID, math.floor(self.x), math.floor(self.y)) # Could use move, but I prefer this, it could help if things move at weird angles.
            
    def changeXSpeed(self,change):
        self.xSpeed += change
        self.xSpeed = keepInBounds(self.xSpeed,-self.speed,self.speed)
    def changeYSpeed(self,change):
        self.ySpeed += change
        self.ySpeed = keepInBounds(self.ySpeed,-self.speed,self.speed)
    

class Player(Mobile):
    """This is the player class, which the user will control in this space fighter game.
    """
    def __init__(self, x,y, image, canvas, height, width, health =3, speed =5) -> None:
        super().__init__(x,y,image, canvas, height, width)
        self.health =health
        self.speed = speed
        
    
    