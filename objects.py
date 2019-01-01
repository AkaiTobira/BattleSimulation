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
    addings          = []

    COLOR            = Colors.WHITE

    RADIUS           = 5 

    def __init__( self, screen, position):
        self.initializated    = time.time()
        self.screen           = screen
        self.current_position = position

    def time_out(self, durration):
        if time.time() - self.initializated > durration:
            self.exist = False

    def draw_time_out(self, durration):
        font = pygame.font.SysFont("consolas", int(10) )
        text = font.render( str(int(  durration - ( time.time() - self.initializated )  )) , True, get_color(self.COLOR))
        text_rect = text.get_rect(center=(self.current_position.x, self.current_position.y - 10))
        self.screen.blit(text, text_rect)

    def get_addigs(self):
        self.exist = False
        return self.addings

class ItemHp(Item):
    COLOR = Colors.GREEN
    addings = [ "HP", 50 ]

    def draw(self):
        pygame.draw.circle(self.screen, get_color(self.COLOR), self.current_position.to_table(), 5 )
        self.draw_time_out(50)


    def update(self, delta):
        self.time_out( 50 )

    def process(self):
        pass



class ItemArmour(Item):
    COLOR = Colors.WHITE
    addings = [ "AA", 50 ]

    def draw(self):
        pygame.draw.circle(self.screen, get_color(self.COLOR), self.current_position.to_table(), 5 )
        self.draw_time_out(35)

    def update(self, delta):
        self.time_out( 35 )

    def process(self):
        pass



class ItemAmmo(Item):
    def update(self, delta):
        self.time_out( 40 )

    def process(self):
        pass

class ItemAmmoBazzoka(ItemAmmo):
    COLOR = Colors.GOLD
    addings = [ "AB", 15 ]

    def draw(self):
        pygame.draw.circle(self.screen, get_color(self.COLOR), self.current_position.to_table(), 5 )
        self.draw_time_out(40)

class ItemAmmoRailgun(ItemAmmo):
    COLOR = Colors.DARK_VIOLET
    addings = [ "AR", 15 ]

    def draw(self):
        pygame.draw.circle(self.screen, get_color(self.COLOR), self.current_position.to_table(), 5 )
        self.draw_time_out(40)


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
    addings          = [ "BZ", 0 ]

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
            self.RADIUS = int((( time.time() - self.initializated ) / 0.50 ) * 100) 
            if self.RADIUS > 45 : self.exist = False