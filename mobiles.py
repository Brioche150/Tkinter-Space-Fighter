import math
from string import hexdigits
from tkinter import PhotoImage, Canvas
from typing import Dict
import random as rand
from constants import tickDelay


def keepInBounds(num,min,max):
        if num < min:
            num = min
        elif num > max:
            num = max
        return num
    
def calcDirection(selfX,selfY,targetX,targetY):
    dx = targetX - selfX
    dy =  selfY - targetY # flipped around from the other one, to make it like a normal coordinate system
    
    if(dy == 0): # This avoids 0 division errors
        if(dx <0):
            direction = math.pi * 3/2
        else:
            direction = math.pi / 2
    else:
        direction = math.atan(dx/dy)# this calculates the bearing based on the vector between the mouse click and the shot when it spawns
        if dy < 0:
            direction += math.pi
        elif dx < 0:
            direction += 2 * math.pi
    return direction

class Mobile:
    """This is the super class of all entities that will be moving around.
    attributes: x and y are ints giving the coordinates of the object
    ImageID is an int storing the ID of the object that the canvas uss
    Canvas is a reference to the canvas itself, so that it can be editied easily
    Height and width are ints give the pixel height and width of the image
    speed is a float giving the maximum speed of the object
    health is an int storing the health of the object
    """
    def __init__(self, x, y, imageID, canvas: Canvas, height, width, speed,health =1, isEnemy =True) -> None:
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
        self.isEnemy = isEnemy
        
    
    def move(self):
        """This will update the position of the object based on the xSpeed and ySpeed

        """
        if self.xSpeed != 0 or self.ySpeed != 0: 
            self.x += self.xSpeed * tickDelay()
            self.x = keepInBounds(self.x,0,self.canvas.winfo_width() - self.width)

            self.y += self.ySpeed * tickDelay()
            self.y = keepInBounds(self.y,0,self.canvas.winfo_height() -self.height)
            
            self.canvas.moveto(self.imageID, math.floor(self.x), math.floor(self.y)) # Could use move, but I prefer this, it could help if things move at weird angles.
            
    def changeXSpeed(self,change):
        """This changes the xSpeed of the object, while making sure it doesn't go over the max speed set by self.speed

        Args:
            change (float): The amount that self.Xspeed is to be changed by
        """
        self.xSpeed += change
        self.xSpeed = keepInBounds(self.xSpeed,-self.speed,self.speed)
    def changeYSpeed(self,change):
        """This changes the xSpeed of the object, while making sure it doesn't go over the max speed set by self.speed

        Args:
            change (float): The amount that self.Xspeed is to be changed by
        """
        self.ySpeed += change
        self.ySpeed = keepInBounds(self.ySpeed,-self.speed,self.speed)
    


        
class NPC(Mobile):
    """This is the class all other mobile entities fit in, and they will be guided by direction, with a set speed

    Args:
        Mobile (_type_): _description_
    """
    def __init__(self,x,y,imageID,canvas: Canvas,height,width, direction, speed =0.3,health=1,isEnemy = True) -> None:
        super().__init__(x,y,imageID, canvas, height, width,speed,health,isEnemy)
        self.direction =direction # This is going to be a bearing system, so 0 is up, pi/2 is right (radians because that's what math works in), etc. For most mobs it's going to be easier to direct them in terms of change angles
        self.updateSpeedsFromDirection()
        
    def updateSpeedsFromDirection(self):
        self.ySpeed = self.speed * -math.cos(self.direction)
        self.xSpeed = self.speed * math.sin(self.direction)

class Projectile(NPC):
    """This is class for projectiles shot by the player or enemy. Its main difference is that it deletes the objects

    Args:
        NPC (_type_): _description_
    """
    
    def __init__(self,x,y,imageID,canvas: Canvas,height,width, direction, mobs : Dict[int,Mobile] = None, speed =1.5,health=1, isEnemy = True) -> None:
        super().__init__(x,y,imageID, canvas, height, width,direction,speed,health,isEnemy)
        self.mobs = mobs
        
    def move(self):
        """Projectile's move is the same as the regular move - updating position based on x and y speed - but deletes the projectile if it hits the edge of the canvas.
        There is also a section dealing with collision, shooting at enemies
        """
        super().move()
        if not self.isEnemy: # only runs collision logic if it's the player's own shot
            IDs = self.canvas.find_overlapping(self.x,self.y,self.x+self.width,self.y+self.height)
            for ID in IDs:
                if self.mobs[ID].isEnemy and isinstance(self.mobs[ID],GruntEnemy):
                    self.health -= 1
                    self.mobs[ID].health -=1
                    break
        if self.x == self.canvas.winfo_width() - self.width or self.x == 0 or self.y == self.canvas.winfo_height() -self.height or self.y == 0:
            self.health =0

class GruntEnemy(NPC):
    """Most enemies will be basic grunts, with only 1 health and firing infrequently

    Args:
        NPC (_type_): _description_
    """
    def __init__(self,x,y,imageID,canvas: Canvas,height,width, direction, speed =0.3, isEnemy = True, shotCooldown = 1000,turnCooldown = 1500) -> None:
        super().__init__(x,y,imageID, canvas, height, width,direction,speed,isEnemy)
        self.shotCooldown = shotCooldown // tickDelay()
        self.turnCooldown = turnCooldown // tickDelay()
        self.shotCooldownReset = self.shotCooldown
        self.turnCooldownReset = self.turnCooldown
        self.isSteering = False # This will be used to put the enemy into a state where they "steer", so turn more gradually, rather than suddenly changing direction
        self.turnRate =0
    def move(self):
        super().move()
        if self.turnCooldown >0:
            self.turnCooldown -=1
            if self.isSteering:
                self.direction += self.turnRate
                self.updateSpeedsFromDirection()
                
        else:
            self.isSteering = False
            if rand.randint(1,3) == 1: # Gives 1/3 chance of going into steering mode
                self.turnCooldown = self.turnCooldownReset /5 # Makes it so that they don't spend ages turning
                self.isSteering = True
                self.turnRate = rand.uniform(-math.pi/(2*self.turnCooldown),math.pi / (2* self.turnCooldown))
            else:
                self.direction = rand.uniform(-math.pi * 9/8,math.pi/8) # This makes them turn a random direction, but mostly they go left
                self.updateSpeedsFromDirection()
                self.turnCooldown = self.turnCooldownReset
    
    def fire(self,x,y, mobs : Dict[int,Mobile]):
        """this is the grunt's fire code. It will fire intermittently roughly at the player. It should be called every tick

        Args:
            x int: This is the x coordinate of the player at the time
            y int: this is the y coordinate of the player at the time
 
        """
        if(self.shotCooldown <= 0):
            shotID = self.canvas.create_oval(self.x + 12,self.y +12,self.x+22,self.y+22,fill="red")
            
            direction = calcDirection(self.x + 12, self.y +12, x,y)
            
            direction += rand.uniform(-math.pi/8, math.pi/8)
            shot = Projectile(self.x +12,self.y +12,shotID,self.canvas,10,10,direction, speed=0.7)
            mobs[shotID] = shot
            self.shotCooldown = self.shotCooldownReset
        else:
            self.shotCooldown -=1
        
class Player(Mobile):
    """This is the player class, which the user will control in this space fighter game.
    """
    def __init__(self, x,y, imageID, canvas: Canvas, height, width, mobs : Dict[int,Mobile], speed =0.5, health =3, isEnemy = False) -> None:
        super().__init__(x,y,imageID, canvas, height, width,speed,health,isEnemy)
        self.mobs = mobs
        
    def move(self):
        super().move()
        IDs = self.canvas.find_overlapping(self.x,self.y,self.x+self.width,self.y+self.height)
        for ID in IDs:
            if self.mobs[ID].isEnemy:
                self.health -= 1
                self.mobs[ID].health -=1
                print("Damage Taken! Health = " + str(self.health))
                break # Break is here because otherwise the player could get damaged multiple times in a frame, which is unfun.
    
    def fire(self,event):
        """This is how the player fires shots where the mouse is at the time

        Args:
            event (Event): This is the event that triggers shot. It will contain the x and y coordinates of the mouse when the shot is fired, to give the shot its direction

        """
        x = self.x+10
        y = self.y+10
        shotID = self.canvas.create_oval(x,y,x+10,y+10,fill="yellow")
        
        direction = calcDirection(x,y,event.x,event.y)
        
        shot = Projectile(x,y,shotID,self.canvas,10,10,direction,mobs= self.mobs,isEnemy=False)
        self.mobs[shotID] = shot
    
    