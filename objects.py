import pygame
import time

from  vector import *
from colors import Colors, get_color, POINT_DISTANCE

class Item:
    current_position = None
    screen           = None
    initializated    = 0

    def __init__( self, screen, position):
        self.initializated    = time.time()
        self.screen           = screen
        self.current_position = position


class ItemHp(Item):
    def draw(self):
        pygame.draw.circle(self.screen, get_color(Colors.GREEN), self.current_position.to_table(), 5 )
        pass

    def update(self, delta):
        pass

    def process(self):
        pass


class ItemAmmo(Item):
    def draw(self):
        pygame.draw.circle(self.screen, get_color(Colors.BLUE_BAR), self.current_position.to_table(), 5 )
        pass

    def update(self, delta):
        pass

    def process(self):
        pass