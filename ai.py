from random import randint, uniform
from vector import Vector
from colors import POINT_DISTANCE
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
        distance = owner.current_position.distance_to(target)
        velocity =  (target- owner.current_position).norm() * owner.max_speed     - owner.velocity
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

    def path_realizer(self,owner):
        if len(owner.path) <= 0 : 
            owner.need_path = True
            owner.destination = Vector( randint(0,50) * POINT_DISTANCE, randint(0,40)* POINT_DISTANCE)
        else:
            dist = owner.current_position.distance_to(owner.path[0])
            owner.velocity = self.arrival(owner,owner.path[0]).norm() * ( POINT_DISTANCE-5 )
            owner.look_at  = (owner.look_at + ( owner.velocity.norm() - owner.look_at )).norm()
            if dist.len() - owner.velocity.len() < 0: 
                owner.velocity = owner.velocity.norm() * dist.len()
                owner.path = owner.path[1:] 


    def have_in_space(self,owner, kind):
        for i in owner.scaner[1]:
            if i.addings[0] == kind:
                return True
        return False

    destination = None
    def execute(self, owner):
        self.path_realizer(owner)

        ranomizer = randint(0,100)


        if len(owner.scaner[0]) > 0 and owner.hp > 30 and (( owner.ammo_bazooka > 0) or (owner.ammo_railgun > 0)):
            owner.ai.change_state( StateAtack() )
            owner.path = owner.path[:1]
            #stateAtack
        elif  self.have_in_space(owner, "AR") and ( owner.get_ammo()[0] < 50 ):
            owner.ai.change_state( StateCollectAmmoRailgun() )
            owner.path = owner.path[:1]
            #CollectAmmoRailgun

        elif self.have_in_space(owner, "AB") and ( owner.get_ammo()[1] < 50 ):
            owner.ai.change_state( StateCollectAmmoBazooka() )
            owner.path = owner.path[:1]
            #CollectAmmoRailgun

        elif len(owner.scaner[1]) > 0 and len(owner.scaner[0]) == 0:
            owner.ai.change_state( StateCollect() )
            owner.path = owner.path[:1]
            #CollectEveryting
        
    

        elif owner.hp < 30:
            pass
            #stateRun
        elif len(owner.scaner[0]) == 0 and len(owner.scaner[1]) > 0:
            pass
            
        elif owner.hp < 30 and len(owner.scaner[0]) == 0:
            pass
            #stateCollectHp


        pass

class StateCollectAmmoBazooka(State):
    state = "CollecBazoka"

    def enter(self, owner):
        print( "ENTER STATE COLLECT")
        pass

    def exit(self, owner):
        print( "ENTER WANDER")
        pass

    def get_closest(self, owner):
        close = 99999999
        obj = owner.scaner[1][0]
        
        for i in owner.scaner[1]:
            if i.addings[0] == "AB":
                if i.current_position.distance_to(owner.current_position).len() < close:
                    obj   = i
                    close = i.current_position.distance_to(owner.current_position).len()

        return obj


    def path_realizer(self,owner):
        if len(owner.path) <= 0 : 
            owner.need_path = True
            if len( owner.scaner[1] ) == 0: return
            self.currently_collecting = self.get_closest(owner)
            if self.currently_collecting == None : return
            owner.destination =  self.currently_collecting.current_position
        else:
            dist = owner.current_position.distance_to(owner.path[0])
            owner.velocity = self.arrival(owner,owner.path[0]).norm() * ( POINT_DISTANCE-5 )
            owner.look_at  = (owner.look_at + ( owner.velocity.norm() - owner.look_at )).norm()
            if dist.len() - owner.velocity.len() < 0: 
                owner.velocity = owner.velocity.norm() * dist.len()
                owner.path = owner.path[1:] 

    destination = None
    currently_collecting = None   

    def execute(self, owner):
    #    print( owner.scaner[1] )

        if not owner.ammo_bazooka < 50 or len( owner.scaner[1] ) == 0:
            owner.ai.change_state( StateWander() )

        if len(owner.scaner[0]) > 0 and owner.hp > 30 and (( owner.ammo_bazooka > 0) or (owner.ammo_railgun > 0)):
            owner.ai.change_state( StateAtack() )

        self.path_realizer(owner)
        pass

class StateCollectHP(State):
    state = "CollecHp"

    def enter(self, owner):
        print( "ENTER STATE COLLECT")
        pass

    def exit(self, owner):
        print( "ENTER WANDER")
        pass

    def get_closest(self, owner):
        close = 99999999
        obj = owner.scaner[1][0]
        
        for i in owner.scaner[1]:
            if i.addings[0] == "HP":
                if i.current_position.distance_to(owner.current_position).len() < close:
                    obj   = i
                    close = i.current_position.distance_to(owner.current_position).len()

        return obj


    def path_realizer(self,owner):
        if len(owner.path) <= 0 : 
            owner.need_path = True
            if len( owner.scaner[1] ) == 0: return
            self.currently_collecting = self.get_closest(owner)
            if self.currently_collecting == None : return
            owner.destination =  self.currently_collecting.current_position
        else:
            dist = owner.current_position.distance_to(owner.path[0])
            owner.velocity = self.arrival(owner,owner.path[0]).norm() * ( POINT_DISTANCE-5 )
            owner.look_at  = (owner.look_at + ( owner.velocity.norm() - owner.look_at )).norm()
            if dist.len() - owner.velocity.len() < 0: 
                owner.velocity = owner.velocity.norm() * dist.len()
                owner.path = owner.path[1:] 

    destination = None
    currently_collecting = None   

    def execute(self, owner):
    #    print( owner.scaner[1] )

        if not owner.hp < 30 or len( owner.scaner[1] ) == 0:
            owner.ai.change_state( StateWander() )

        if len(owner.scaner[0]) > 0 and owner.hp > 30 and (( owner.ammo_bazooka > 0) or (owner.ammo_railgun > 0)):
            owner.ai.change_state( StateAtack() )

        self.path_realizer(owner)
        pass


class StateCollectAmmoRailgun(State):
    state = "CollecRailgunt"

    def enter(self, owner):
        print( "ENTER STATE COLLECT")
        pass

    def exit(self, owner):
        print( "ENTER WANDER")
        pass

    def get_closest(self, owner):
        close = 99999999
        obj = owner.scaner[1][0]
        
        for i in owner.scaner[1]:
            if i.addings[0] == "AR":
                if i.current_position.distance_to(owner.current_position).len() < close:
                    obj   = i
                    close = i.current_position.distance_to(owner.current_position).len()

        return obj


    def path_realizer(self,owner):
        if len(owner.path) <= 0 : 
            owner.need_path = True
            if len( owner.scaner[1] ) == 0: return
            self.currently_collecting = self.get_closest(owner)
            if self.currently_collecting == None : return
            owner.destination =  self.currently_collecting.current_position
        else:
            dist = owner.current_position.distance_to(owner.path[0])
            owner.velocity = self.arrival(owner,owner.path[0]).norm() * ( POINT_DISTANCE-5 )
            owner.look_at  = (owner.look_at + ( owner.velocity.norm() - owner.look_at )).norm()
            if dist.len() - owner.velocity.len() < 0: 
                owner.velocity = owner.velocity.norm() * dist.len()
                owner.path = owner.path[1:] 

    destination = None
    currently_collecting = None   

    def execute(self, owner):
    #    print( owner.scaner[1] )

        if not owner.ammo_railgun < 50 or len( owner.scaner[1] ) == 0:
            owner.ai.change_state( StateWander() )

        if len(owner.scaner[0]) > 0 and owner.hp > 30 and (( owner.ammo_bazooka > 0) or (owner.ammo_railgun > 0)):
            owner.ai.change_state( StateAtack() )

        self.path_realizer(owner)
        pass

class StateCollect(State):
    state = "Collec"

    def enter(self, owner):
        print( "ENTER STATE COLLECTRailgun")
        pass

    def exit(self, owner):
        pass

    def get_closest(self, owner):
        close = 99999999
        obj = owner.scaner[1][0]
        
        for i in owner.scaner[1]:
            if i.current_position.distance_to(owner.current_position).len() < close:
                obj   = i
                close = i.current_position.distance_to(owner.current_position).len()

        return obj


    def path_realizer(self,owner):
        if len(owner.path) <= 0 : 
            owner.need_path = True
            if len( owner.scaner[1] ) == 0: return
            self.currently_collecting = self.get_closest(owner)
            owner.destination =  self.currently_collecting.current_position
        else:
            dist = owner.current_position.distance_to(owner.path[0])
            owner.velocity = self.arrival(owner,owner.path[0]).norm() * ( POINT_DISTANCE-5 )
            owner.look_at  = (owner.look_at + ( owner.velocity.norm() - owner.look_at )).norm()
            if dist.len() - owner.velocity.len() < 0: 
                owner.velocity = owner.velocity.norm() * dist.len()
                owner.path = owner.path[1:] 

    destination = None
    currently_collecting = None   

    def have_in_space(self,owner, kind):
        for i in owner.scaner[1]:
            if i.addings[0] == kind:
                return True
        return False


    def execute(self, owner):
    #    print( owner.scaner[1] )
        if len( owner.scaner[1] ) == 0 or ( self.have_in_space(owner, "AB") and owner.ammo_bazooka < 50 ) or ( self.have_in_space(owner, "AR") and owner.ammo_railgun < 50 ):
            owner.ai.change_state( StateWander() )

        if len(owner.scaner[0]) > 0 and owner.hp > 30 and (( owner.ammo_bazooka > 0) or (owner.ammo_railgun > 0)):
            owner.ai.change_state( StateAtack() )

        self.path_realizer(owner)

        pass

class StateAtack(State):
    state = "Collec"

    def enter(self, owner):
        print( "ENTER STATE Atack")
        self.shoot_railgun = time.time()
        self.shoot_bazooka = time.time()
        pass

    def exit(self, owner):
        pass

    def get_closest(self, owner):
        close = 99999999
        obj = owner.scaner[0][0]
        
        for i in owner.scaner[0]:
            if i.current_position.distance_to(owner.current_position).len() < close:
                obj   = i
                close = i.current_position.distance_to(owner.current_position).len()

        return obj


    def path_realizer(self,owner):
        if len(owner.path) <= 0 : 
            owner.need_path = True
        #    if len( owner.scaner[0] ) == 0: return
            self.currently_collecting = self.get_closest(owner)
            owner.destination =  Vector( int(self.currently_collecting.current_position.x/POINT_DISTANCE) * POINT_DISTANCE,
                                         int(self.currently_collecting.current_position.y/POINT_DISTANCE) * POINT_DISTANCE )   #+ #Vector( randint(-3,3)*POINT_DISTANCE, randint(-3,3)*POINT_DISTANCE )
            owner.look_at  = (self.currently_collecting.current_position - owner.current_position).norm()
        else:
            dist = owner.current_position.distance_to(owner.path[0])
            owner.velocity = self.arrival(owner,owner.path[0]).norm() * ( POINT_DISTANCE-5 )

            if self.currently_collecting == None:
                owner.look_at = owner.velocity.norm()
            else:
                owner.look_at  = (self.currently_collecting.current_position - owner.current_position).norm()
            #(owner.look_at + ( owner.velocity.norm() - owner.look_at )).norm()
            if dist.len() - owner.velocity.len() < 0: 
                owner.velocity = owner.velocity.norm() * dist.len()
                owner.path = owner.path[1:] 

    destination = None
    currently_collecting = None   

    def have_in_space(self,owner, kind):
        for i in owner.scaner[1]:
            if i.addings[0] == kind:
                return True
        return False


    time_out_railgun = 5
    time_out_bazooka = 2
    shoot_railgun    = 0
    shoot_bazooka    = 0

    def execute(self, owner):
    #    print( owner.scaner[1] )
        if len( owner.scaner[0] ) == 0 or ( owner.ammo_bazooka < 20  and owner.ammo_railgun < 50 ):
            owner.ai.change_state( StateWander() )

        if owner.hp < 30:
            owner.ai.change_state( StateWander() )

        self.path_realizer(owner)
        

        if self.currently_collecting == None: return

     #   print( owner.ammo_railgun > 50 and self.shoot_railgun - time.time() > self.time_out_railgun,  owner.ammo_railgun > 50, self.shoot_railgun - time.time() > self.time_out_railgun, self.shoot_railgun )

        if self.currently_collecting.current_position.distance_to(owner.current_position).len() < 300 :
            if owner.ammo_railgun > 50 and  time.time() - self.shoot_railgun > self.time_out_railgun : 
                owner.railgun_shot()
                self.shoot_railgun = time.time()

        if owner.ammo_bazooka > 50 and time.time() - self.shoot_bazooka  > self.time_out_bazooka : 
                owner.bazooka_shot()
                self.shoot_bazooka = time.time()

            


        pass