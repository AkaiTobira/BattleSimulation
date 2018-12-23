import pygame
import time

from  vector import *
from colors import Colors, get_color, POINT_DISTANCE

class Item:
    current_position = None
    screen           = None
    initializated    = 0
    exist            = True

    def __init__( self, screen, position):
        self.initializated    = time.time()
        self.screen           = screen
        self.current_position = position

    def time_out(self, durration):
        if time.time() - self.initializated > durration:
            self.exist = False

class ItemHp(Item):
    def draw(self):
        pygame.draw.circle(self.screen, get_color(Colors.GREEN), self.current_position.to_table(), 5 )
        pass

    def update(self, delta):
        self.time_out( 10 )
        pass

    def process(self):
        pass


class ItemArmour(Item):
    def draw(self):
        pygame.draw.circle(self.screen, get_color(Colors.YELLOW), self.current_position.to_table(), 5 )
        pass

    def update(self, delta):
        self.time_out( 20 )
        pass

    def process(self):
        pass

class ItemAmmo(Item):
    def draw(self):
        pygame.draw.circle(self.screen, get_color(Colors.BLUE_BAR), self.current_position.to_table(), 5 )
        pass

    def update(self, delta):
        self.time_out( 20 )
        pass

    def process(self):
        pass


class ItemAmmoBazzoka(ItemAmmo):
    def draw(self):
        pygame.draw.circle(self.screen, get_color(Colors.WHITE), self.current_position.to_table(), 5 )


class ItemAmmoRailgun(ItemAmmo):
     def draw(self):
        pygame.draw.circle(self.screen, get_color(Colors.BLACK), self.current_position.to_table(), 5 )
        pass

class BazookaMissle:
    spawn_point      = None
    current_position = None
    screen           = None
    initializated    = 0
    direction        = None
    exist            = True


    def __init__( self, screen, position, direction):
        self.initializated    = time.time()
        self.screen           = screen
        self.current_position = position
        self.direction        = direction.norm()
        self.spawn_point      = position

    def time_out(self, durration):
        if time.time() - self.initializated > durration:
            self.exist = False
        if self.current_position.distance_to(self.spawn_point).len() > 1000:
            self.exist = False

    def draw(self):
        pygame.draw.circle(self.screen, get_color(Colors.KHAKI), self.current_position.to_table(), 5 )

    def update(self, delta):
        self.current_position += self.direction * 100 * delta 