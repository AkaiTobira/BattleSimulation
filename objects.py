import pygame
import time

from  vector import *
from colors import Colors, get_color, POINT_DISTANCE

class Item:
    current_position = None
    screen           = None
    initializated    = 0
    exist            = True
    is_missle        = False

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
    explode          = False
    is_missle        = True 
    dmg              = 75

    def __init__( self, screen, position, direction):
       
        self.screen           = screen
        self.current_position = position
        self.direction        = direction.norm()
        self.spawn_point      = position
        self.exist            = True
        self.explode          = False
        self.RADIUS           = 1

    def make_explode(self):
        self.explode = True
        self.initializated    = time.time()

    def time_out(self):
        if self.current_position.x < 0 or self.current_position.x > 1024:
            self.make_explode()
        if self.current_position.y < 0 or self.current_position.y > 720:
            self.make_explode()

        if self.current_position.distance_to(self.spawn_point).len() > 1000:
            self.exist = False

    def get_dmg(self):
        return self.dmg * (1-(( time.time() - self.initializated ) / 0.50 ) )

    def draw(self):
        if not self.explode:
            pygame.draw.circle(self.screen, get_color(Colors.KHAKI), self.current_position.to_table(), 5 )
        else:
            pygame.draw.circle(self.screen, get_color(Colors.ORANGERED), self.current_position.to_table(), self.RADIUS )

    def update(self, delta):
        if not self.explode : 
            self.current_position += self.direction * 200 * delta 
            self.time_out()
        else:
            self.RADIUS = int((( time.time() - self.initializated ) / 0.50 ) * 50) 
            if self.RADIUS > 45 : self.exist = False