from tkinter import PhotoImage

class Mobile:
    def __init__(self, x, y, image) -> None:
        self.x =y
        self.y =y
        self.image = PhotoImage(file="assets/player/player_boost.png")
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
            return True
        else:
            return False    
    

class Player(Mobile):
    """This is the player class, which the user will control in this space fighter game.
    """
    def __init__(self, x,y, image, health =3) -> None:
        super().__init__(x,y,image)
        # self.x =y
        # self.x =y
        # self.image = image
        self.health =health