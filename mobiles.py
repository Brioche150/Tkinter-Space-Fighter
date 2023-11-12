import math
from tkinter import PhotoImage, Canvas
from numpy import sign
import random as rand

def keepInBounds(num,min,max):
        if num < min:
            num = min
        elif num > max:
            num = max
        return num

class Mobile:
    def __init__(self, x, y, imageID, canvas: Canvas, height, width, speed, health =1 ) -> None:
        self.x =x
        self.y =y
        self.imageID = imageID
        self.canvas = canvas
        self.xSpeed =0
        self.ySpeed=0
        self.speed = speed
        self.height = height
        self.width = width
        self.health = health
        
    
    def move(self):
        """This will update the position of the object based on the xSpeed and ySpeed

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
    


        
class NPC(Mobile):
    """This is the class all other mobile entities fit in, and they will be guided by direction, with a set speed

    Args:
        Mobile (_type_): _description_
    """
    def __init__(self,x,y,imageID,canvas: Canvas,height,width, direction, speed =3, isEnemy = True) -> None:
        super().__init__(x,y,imageID, canvas, height, width,speed)
        self.direction =direction # This is going to be a bearing system, so 0 is up, pi/2 is right (radians because that's what math works in), etc. For most mobs it's going to be easier to direct them in terms of change angles
        self.isEnemy = isEnemy
        self.updateSpeedsFromDirection()
        
    def updateSpeedsFromDirection(self):
        self.ySpeed = self.speed * -math.cos(self.direction)
        self.xSpeed = self.speed * math.sin(self.direction)

class Projectile(NPC):
    """This is class for projectiles shot by the player or enemy. Its main difference is that it deletes the objects

    Args:
        NPC (_type_): _description_
    """
    
    def __init__(self,x,y,imageID,canvas: Canvas,height,width, direction, speed =15, isEnemy = True) -> None:
        super().__init__(x,y,imageID, canvas, height, width,direction,speed,isEnemy)
        self.direction =direction
        self.speed =speed
        
    def move(self):
        """Projectile's move is the same as the regular move - updating position based on x and y speed - but deletes the projectile if it hits the edge of the canvas
        """
        super().move()
        if self.x == self.canvas.winfo_width() - self.width or self.x == 0 or self.y == self.canvas.winfo_height() -self.height or self.y == 0:
            self.health =0

class GruntEnemy(NPC):
    """Most enemies will be basic grunts, with only 1 health and firing infrequently

    Args:
        NPC (_type_): _description_
    """
    def __init__(self,x,y,imageID,canvas: Canvas,height,width, direction, speed =3, isEnemy = True, shotCooldown = 100) -> None:
        super().__init__(x,y,imageID, canvas, height, width,direction,speed,isEnemy)
        self.direction =direction
        self.speed =speed
        self.shotCooldown = shotCooldown
    
    def fire(self,x,y, mobs):
        """this is the grunt's fire code. It will fire intermittently roughly at the player. It should be called every tick

        Args:
            x int: This is the x coordinate of the player at the time
            y int: this is the y coordinate of the player at the time
 
        """
        if(self.shotCooldown <= 0):
            shotID = self.canvas.create_oval(self.x + 12,self.y +12,self.x+22,self.y+22,fill="red")
            
            dx = x - self.x
            dy =  self.y - y # flipped around from the other one, to make it like a normal coordinate system
            
            if(dy == 0):
                direction = math.pi/2 + (((-sign(dx) + 1)/2) * math.pi) # This is here to avoid zero division errors.
            else:
                direction = math.atan(dx/dy)# this calculates the bearing based on the vector between the mouse click and the shot when it spawns
                if dy < 0:
                    direction += math.pi
                elif dx < 0:
                    direction += 2 * math.pi
            direction += rand.uniform(-math.pi/8, math.pi/8)
            shot = Projectile(self.x,self.y,shotID,self.canvas,10,10,direction, speed=7)
            mobs.append(shot)
            self.shotCooldown = 200
        else:
            self.shotCooldown -=1
        
class Player(Mobile):
    """This is the player class, which the user will control in this space fighter game.
    """
    def __init__(self, x,y, imageID, canvas: Canvas, height, width, speed =5, health =3) -> None:
        super().__init__(x,y,imageID, canvas, height, width,speed)
        self.health =health
        
    def fire(self,event,mobs):
        """This is how the player fires shots where the mouse is at the time

        Args:
            event (Event): This is the event that triggers shot. It will contain the x and y coordinates of the mouse when the shot is fired, to give the shot its direction

        """
        x = self.x+10
        y = self.y+10
        shotID = self.canvas.create_oval(x,y,x+10,y+10,fill="yellow")
        
        dx = event.x - x
        dy =  y - event.y # flipped around from the other one, to make it like a normal coordinate system
        
        if(dy == 0):
            direction = math.pi/2 + (((-sign(dx) + 1)/2) * math.pi) # This is here to avoid zero division errors.
        else:
            direction = math.atan(dx/dy)# this calculates the bearing based on the vector between the mouse click and the shot when it spawns
            if dy < 0:
                direction += math.pi
            elif dx < 0:
                direction += 2 * math.pi
        shot = Projectile(x,y,shotID,self.canvas,10,10,direction,isEnemy=False)
        mobs.append(shot)
    