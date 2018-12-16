from random import randint, uniform
from vector import Vector
import time
import math

class FiniteStateMachine:
    current_state  = None
    previous_state = None
    global_state   = None 
    owner          = None 

    def __init__(self, owner):
        self.owner = owner

    def set_current_state(self, state):
        self.current_state = state
    def set_global_state(self, state):
        self.global_state = state
    def set_previous_state(self, state):
        self.previous_state = state

    def change_state(self, state):
        self.previous_state = self.current_state
        self.current_state.exit(self.owner)
        self.current_state  = state
        self.current_state.enter(self.owner)

    def update(self,delta):
        if self.current_state:
            self.current_state.execute(self.owner)

    def revert_to_previous_state(self):
        self.change_state(self.previous_state)

    def is_in_state(self,state):
        return state == self.current_state
        
class State:
    state = "None"
    w_target          = Vector(0,0) 

    walls           = [ 
            [ Vector(0    ,   0), Vector(1024,0), Vector( 0 , 1)],
            [ Vector(0    ,   0), Vector(0, 720), Vector( 1 , 0)],
            [ Vector(1024,0),    Vector(1024 , 720),  Vector( -1 , 0 )],
            [  Vector(0, 720),   Vector(1024 , 720), Vector( 0, -1)]
            ]

    def __eq__(self,state):
        return state == self.state

    def wander(self,owner):
        w_r        = 20
        w_distance = 7
        w_jiter    = 5

        self.w_target = Vector(uniform(-1, 1) * w_jiter, uniform(-1, 1) * w_jiter ).norm() * w_r
        target_local  = self.w_target + Vector(w_distance, 0) 
        return self.seek(owner, owner.current_position + owner.velocity + self.w_target)

    def seek(self, owner, target):
        velocity =  (target- owner.current_position).norm() * owner.max_speed     - owner.velocity
        return velocity

    def arrival(self, owner, target):
        distance = owner.current_position.distance_to(target.current_position)
        velocity =  (target.current_position- owner.current_position).norm() * owner.max_speed     - owner.velocity
        return min( velocity , distance ) 

    def avoid(self, owner):
        if owner.closest_obstacle and not owner.velocity.is_zero_len() :
            av_f = owner.ahead - owner.closest_obstacle.current_position                        
            return av_f.norm() * 40
        return Vector(0,0)

    def solve( self, P1, P2, P3, P4):
        nominatorA  =  (P4.x - P3.x)*(P1.y - P3.y) - (P4.y - P3.y)*(P1.x - P3.x)
        nominatorB  =  (P2.x - P1.x)*(P1.y - P3.y) - (P2.y - P1.y)*(P1.x - P3.x)
        denominator =  (P4.y - P3.y)*(P2.x - P1.x) - (P4.x - P3.x)*(P2.y - P1.y)

        if denominator == 0 : return None

        uA = nominatorA/denominator
        uB = nominatorB/denominator

        if uA < 0 or uA > 1 : return None
        if uB < 0 or uB > 1 : return None
        
        return Vector( P1.x + uA*(P2.x-P1.x), P1.y + uA*(P2.y-P1.y) )


    def wallcheckTest(self,owner):
        fleevers           = [ owner.velocity * 5 , owner.velocity.rotate(math.pi/8)*5, owner.velocity.rotate(-math.pi/8)*5 ]
        stering            = Vector(0,0)
        c_wall             = None
        c_distance_to_wall = 999999999
        c_point            = None

        for f in fleevers:
            point = self.solve( owner.current_position, owner.current_position + f, Vector(512, 0),Vector(512,720))
            if point is None : continue
   
            distance_to_wall = point.distance_to(owner.current_position).len()
            if distance_to_wall < c_distance_to_wall: 
                c_distance_to_wall = distance_to_wall
                c_point            = point 
                c_wall             = [[],[],Vector(-1,0 )]

            if c_wall :
                over_shot = f - c_point 
                stering   += c_wall[2] * over_shot.len() * 3
                print( stering )

        return stering

    def wallcheck(self,owner):
        fleevers           = [ owner.velocity * 3 ]# , owner.velocity.rotate(math.pi/8)*3, owner.velocity.rotate(-math.pi/8)*3 ]
        stering            = Vector(0,0)
        c_wall             = None
        c_distance_to_wall = 999999999
        c_point            = None

        for f in fleevers:
            for wall in self.walls:
                point = self.solve( owner.current_position, owner.current_position + f, wall[0],wall[1])
                if point is None : continue
   
                distance_to_wall = point.distance_to(owner.current_position).len()
                if distance_to_wall < c_distance_to_wall:
                    c_distance_to_wall = distance_to_wall
                    c_point            = point 
                    c_wall             = wall

            if c_wall :
                over_shot = f - c_point 
                stering   += c_wall[2] * over_shot.len() #* 10
    #            print( stering )

        return stering


class EvadeWander(State):
    state = "Wander"

    max_stering_force = Vector(22,22)

    def calculate_steering(self, owner):
     #   stering = -self.arrival(owner,player)     *  owner.priorities[0]
    #    stering += self.avoid(owner,player)       *  owner.priorities[1]
    #    stering += self.wallcheck(owner,player)   *  owner.priorities[2]
        stering  = stering.ttrunc(self.max_stering_force)

        return stering


    def enter(self, owner):
        self.start = time.time()
        owner.max_speed = Vector(100,100)
        pass


    def exit(self, owner):
        owner.can_react = True
        owner.max_speed = Vector(50,50)
        pass

    def execute(self, owner):
        stering_force  = self.calculate_steering(owner)
        owner.velocity =  ( owner.velocity + stering_force / owner.m ).ttrunc( owner.max_speed)

        self.end = time.time()

        if self.end - self.start > 12: 
            owner.ai.change_state( HideBehaviour() )

     #   if owner.current_position.distance_to(player.current_position).len() > 200 :
      #      owner.ai.change_state( SteringWander() )

        pass

class StateWander(State):
    state = "Wander"
    start = 0
    duration = 0
    max_stering_force = Vector(22,22)

    def calculate_steering(self, owner):
        stering   = self.wallcheck(owner)  *  owner.priorities[2]
        stering  += self.wander(owner)     *  owner.priorities[0]
        stering  += self.avoid(owner)      *  owner.priorities[1]
        
        stering   = stering.ttrunc(self.max_stering_force)

        return stering


    def enter(self, owner):
        self.start = time.time()
        self.duration = randint(2, 4)
        owner.max_speed = Vector(150,150)
        pass


    def exit(self, owner):
        pass

    def execute(self, owner):
        stering_force  = self.calculate_steering(owner)
        owner.velocity =  ( owner.velocity + stering_force / owner.m ).ttrunc( owner.max_speed)

        self.end = time.time()
    #    if self.end - self.start > self.duration: 
    #        owner.ai.change_state( HideBehaviour() )

    #    if owner.current_position.distance_to(player.current_position).len() < 200:
    #        owner.ai.change_state( HideBehaviour() )

        pass

class HideBehaviour(State):

    max_stering_force = Vector(33,33)
    w_target          = Vector(0,0) 


    def wallcheckTest(self,owner,player):
        fleevers           = [ owner.velocity * 5 , owner.velocity.rotate(math.pi/8)*5, owner.velocity.rotate(-math.pi/8)*5 ]
        stering            = Vector(0,0)
        c_wall             = None
        c_distance_to_wall = 999999999
        c_point            = None

        for f in fleevers:
            point = self.solve( owner.current_position, owner.current_position + f, Vector(512, 0),Vector(512,720))
            if point is None : continue
   
            distance_to_wall = point.distance_to(owner.current_position).len()
            if distance_to_wall < c_distance_to_wall: 
                c_distance_to_wall = distance_to_wall
                c_point            = point 
                c_wall             = [[],[],Vector(-1,0 )]

            if c_wall :
                over_shot = f - c_point 
                stering   += c_wall[2] * over_shot.len() * 3

        return stering

    def get_hid_spot( self, obstacle, player_position):
        dist_away = obstacle.RADIUS + 25
        to_ob     = (obstacle.current_position - player_position).norm()
        return (to_ob * dist_away) + obstacle.current_position        

    def hide(self, owner, player):
     #   print( owner.closest_hideout )

        return self.seek(owner, self.get_hid_spot( owner.closest_hideout, player.current_position) )
    
    def calculate_steering(self, owner, player):
        stering   = self.wallcheck(owner,player)   *  owner.priorities[2]
        stering  += self.hide(owner,player)        *  owner.priorities[0]
        stering  += self.avoid(owner,player)       *  owner.priorities[1]
        
        stering   = stering.ttrunc(self.max_stering_force)

        return stering

    def enter(self, owner):
        self.start = time.time()
        owner.max_speed = Vector(100,100)
        self.duration = randint(5, 15)
        pass


    def exit(self, owner):
        owner.can_react = True
        owner.max_speed = Vector(50,50)
        pass

    def execute(self, owner, player):
        

        self.end = time.time()
        if self.end - self.start > self.duration: 
            owner.ai.change_state( SteringWander() )

     #   if owner.current_position.distance_to(player.current_position).len() < 20 :
    #        owner.ai.change_state( EvadeWander() )

        stering_force  = self.calculate_steering(owner, player)
        owner.velocity =  ( owner.velocity + stering_force / owner.m ).ttrunc( owner.max_speed)

        pass

class PlayerHunt(State):

    max_stering_force = Vector(22,22)
    w_target          = Vector(0,0) 
    walls           = [ 
            [ Vector(0    ,   0), Vector(1024,0), Vector( 0 , 1)],
            [ Vector(0    ,   0), Vector(0, 720), Vector( 1 , 0)],
            [ Vector(1024,0),    Vector(1024 , 720),  Vector( -1 , 0 )],
            [  Vector(0, 720),   Vector(1024 , 720), Vector( 0, -1)]
            ]

    def calculate_steering(self, owner, player):
        stering = self.arrival(owner,player)  *  owner.priorities[0]
    #    stering   = self.arrival(owner,player) #      *  owner.priorities[0]

        stering  += self.avoid(owner,player)       *  owner.priorities[1]

    #    print("Current Stering :", stering)

        stering   += self.wallcheck(owner,player)  *  owner.priorities[2]


        stering   = stering.ttrunc(self.max_stering_force)

        return stering

    def enter(self, owner):
        owner.max_speed   = Vector(200,200)
        max_stering_force = Vector(100,100)
        pass


    def exit(self, owner):
        pass

    def execute(self, owner, player):
        owner.max_speed   = Vector(250,250)
        stering_force  = self.calculate_steering(owner, player)
        owner.velocity =  ( owner.velocity + stering_force / owner.m ).ttrunc( owner.max_speed)
        pass

