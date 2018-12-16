from  vector import *

class Item:
    current_position = None
    screen           = None

    def __init__( self, screen, position):
        self.screen           = screen
        self.current_position = position


class ItemHp(Item):
    def draw(self):
        pass

    def update(self, delta):
        pass

    def process(self):
        pass


class ItemAmmo(Item):
    def draw(self):
        pass

    def update(self, delta):
        pass

    def process(self):
        pass