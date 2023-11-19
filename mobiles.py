import math
from string import hexdigits
from tkinter import Label, Canvas
from typing import Dict
import random as rand
from constants import mobs, tickDelay, canvas,mobileTag

"""This module stores all of the classes that will be moving around during the game.
This is basically all of the sprites moving around in the game.
"""

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
    def __init__(self, x, y, imageID, height, width, speed,health =1, isEnemy =True) -> None:
        self.x =x
        self.y =y
        self.imageID = imageID
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
            self.x = keepInBounds(self.x,0,canvas().winfo_width() - self.width)

            self.y += self.ySpeed * tickDelay()
            self.y = keepInBounds(self.y,0,canvas().winfo_height() -self.height)
            
            canvas().moveto(self.imageID, math.floor(self.x), math.floor(self.y)) # Could use move, but I prefer this, it could help if things move at weird angles.
            
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

        
class Player(Mobile):
    """This is the player class, which the user will control in this space fighter game.
    """
    def __init__(self, x,y, imageID, height, width, speed =0.5, health =3,score=0) -> None:
        super().__init__(x,y,imageID, height, width,speed,health,isEnemy=False)
        self.healthLabel: Label = None 
        self.scoreLabel: Label = None 
        self.score =score
        
    def move(self):
        super().move()
        IDs = canvas().find_overlapping(self.x,self.y,self.x+self.width,self.y+self.height)
        for ID in IDs:
            if ID in mobs():
                mob = mobs()[ID]
                if mob.isEnemy:
                    self.health -= 1
                    self.healthLabel.config(text = "X" + str(self.health))
                    mob.health -=1
                    print("Damage Taken! Health = " + str(self.health))
                    if self.health <=0:
                        canvas().delete(self.imageID)
                        mobs().pop(self.imageID)
                    if mob.health <= 0:
                        canvas().delete(ID)
                        mobs().pop(ID)
                        if isinstance(mob, GruntEnemy):
                            self.score +=1
                            self.scoreLabel.config(text = "Score:\n" + str(self.score))
                            
                            break # Break is here because otherwise the player could get damaged multiple times in a frame, which is unfun.
                
    
    def fire(self,event):
        """This is how the player fires shots where the mouse is at the time

        Args:
            event (Event): This is the event that triggers shot. It will contain the x and y coordinates of the mouse when the shot is fired, to give the shot its direction

        """
        x = self.x+10
        y = self.y+10
        shotID = canvas().create_oval(x,y,x+10,y+10,fill="yellow",tags=mobileTag())
        
        direction = calcDirection(x,y,event.x,event.y)
        
        shot = Projectile(x,y,shotID,10,10,direction,isEnemy=False, player = self,colour="yellow")
        mobs()[shotID] = shot
    
    

        
class NPC(Mobile):
    """This is the class all other mobile entities fit in, and they will be guided by direction, with a set speed

    Args:
        Mobile (_type_): _description_
    """
    def move(self):
        super().move()
        #This code basically makes NPCs bounce off of walls, so they don't get stuck on them.
        if self.x == 0 or self.x == canvas().winfo_width() - self.width:
            self.direction = (2* math.pi) - self.direction
            self.updateSpeedsFromDirection()
        
        if self.y==0 or self.y == canvas().winfo_height() - self.height: 
            self.direction = math.pi - self.direction
            self.updateSpeedsFromDirection()
    
    def __init__(self,x,y,imageID,height,width, direction, speed =0.3,health=1,isEnemy = True) -> None:
        super().__init__(x,y,imageID,height, width,speed,health,isEnemy)
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
    
    def __init__(self,x,y,imageID,height,width, direction, speed =1.5,health=1, isEnemy = True, player : Player = None, colour = "red") -> None:
        super().__init__(x,y,imageID, height, width,direction,speed,health,isEnemy)
        self.player = player
        self.colour = colour
        
    def move(self):
        """Projectile's move is the same as the regular move - updating position based on x and y speed - but deletes the projectile if it hits the edge of the canvas.
        There is also a section dealing with collision, shooting at enemies
        """
        super().move()
        if not self.isEnemy: # only runs collision logic if it's the player's own shot
            IDs = canvas().find_overlapping(self.x,self.y,self.x+self.width,self.y+self.height)
            for ID in IDs:
                if ID in mobs():
                    mob = mobs()[ID]
                    if mob.isEnemy and isinstance(mob,GruntEnemy):
                        self.health -= 1
                        mob.health -=1
                        if self.health <=0:
                            canvas().delete(self.imageID)
                            mobs().pop(self.imageID)
                        if mob.health <= 0:
                            canvas().delete(ID)
                            mobs().pop(ID)
                            self.player.score +=1
                            self.player.scoreLabel.config(text = "Score:\n" + str(self.player.score))
                        break
                    
                
                    
                
                
        if self.x == canvas().winfo_width() - self.width or self.x == 0 or self.y == canvas().winfo_height() -self.height or self.y == 0:
            self.health =0
            canvas().delete(self.imageID)
            if self.imageID in mobs(): # The if is in an edge case where a projectile is deleted for hitting the wall at the same time as hitting an enemy/player
                mobs().pop(self.imageID) 
        

class GruntEnemy(NPC):
    """Most enemies will be basic grunts, with only 1 health and firing infrequently

    Args:
        NPC (_type_): _description_
    """
    def __init__(self,x,y,imageID,height,width, direction, speed =0.3, shotCooldown = 1000,turnCooldown = 1000) -> None:
        super().__init__(x,y,imageID, height, width,direction,speed,isEnemy=True)
        self.shotCooldown = shotCooldown // tickDelay() 
        self.turnCooldown = turnCooldown // (tickDelay() * 8) # This just makes them change direction quickly after they spawn
        self.shotCooldownReset = self.shotCooldown   
        self.turnCooldownReset = turnCooldown // tickDelay()
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
            if rand.randint(1,9) != 1: # Gives 1/3 chance of going into steering mode
                self.turnCooldown = self.turnCooldownReset //3 # Makes it so that they don't spend ages turning
                self.isSteering = True
                self.turnRate = rand.uniform(-math.pi/(2*self.turnCooldown),math.pi / (2* self.turnCooldown))
            else:
                self.direction = rand.uniform(-math.pi * 9/8,math.pi/8) # This makes them turn a random direction, but mostly they go left
                self.updateSpeedsFromDirection()
                self.turnCooldown = self.turnCooldownReset
    
    def fire(self,x,y):
        """this is the grunt's fire code. It will fire intermittently roughly at the player. It should be called every tick

        Args:
            x int: This is the x coordinate of the player at the time
            y int: this is the y coordinate of the player at the time
 
        """
        if(self.shotCooldown <= 0):
            shotID = canvas().create_oval(self.x + 12,self.y +12,self.x+22,self.y+22,fill="red",tags=mobileTag())
            
            direction = calcDirection(self.x + 12, self.y +12, x,y)
            
            direction += rand.uniform(-math.pi/8, math.pi/8)
            shot = Projectile(self.x +12,self.y +12,shotID,10,10,direction, speed=0.7)
            mobs()[shotID] = shot
            self.shotCooldown = self.shotCooldownReset
        else:
            self.shotCooldown -=1
        
