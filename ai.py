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

    start = False

    walls           = [ 
            [ Vector(0    ,   0), Vector(1024,0), Vector( 0 , 1)],
            [ Vector(0    ,   0), Vector(0, 720), Vector( 1 , 0)],
            [ Vector(1024,0),    Vector(1024 , 720),  Vector( -1 , 0 )],
            [  Vector(0, 720),   Vector(1024 , 720), Vector( 0, -1)]
            ]

    def have_in_space(self,owner, kind):
        for i in owner.scaner[1]:
            if i.addings[0] == kind:
                return True
        return False

    def get_closest(self, owner, what):
        close = 99999999
        obj = None
        
        for i in owner.scaner[1]:
            if i.addings[0] == what or what == None:
                if i.current_position.distance_to(owner.current_position).len() < close:
                    obj   = i
                    close = i.current_position.distance_to(owner.current_position).len()

        return obj

    def has_enemy( self, owner):
        return len( owner.scaner[0] ) != 0

    def have_ammo( self, owner):
        if owner.ammo_bazooka <= 20 and owner.ammo_railgun <= 50: return False
        return True

    def look_at(self, owner, target):
        if target != None: 
            owner.look_at    = (owner.look_at.norm() + ( owner.look_at.norm() + (target.current_position - owner.current_position).norm() ).norm() ).norm()
        else: owner.look_at  = (owner.look_at.norm() + ( owner.look_at.norm() + owner.velocity.norm() ) ).norm()

    def follow_path(self, owner):
        multipler = 0.6 * ( 1 + (1 - owner.hp/owner.hp_max) ) * ( POINT_DISTANCE-5 )

        if self.state == "CollecRun": multipler =  1.65 * ( POINT_DISTANCE-5 )
        if len(owner.path) == 0 : return

        dist = owner.current_position.distance_to(owner.path[0])
        owner.velocity = self.arrival(owner,owner.path[0]).norm() * multipler

        if len(owner.path) == 1 or dist.len() - owner.velocity.len() <= 0: 
            owner.velocity = owner.velocity.norm() * dist.len()
            owner.path = owner.path[1:]
            return 

        dist = owner.current_position.distance_to(owner.path[1])

     #   interpolation = owner.path[0] + (3/dist.len()) * (owner.path[1] - owner.path[0])
        interpolation  = owner.path[1]
        owner.velocity = ((interpolation- owner.current_position).norm() * owner.max_speed- owner.velocity).norm() * multipler
        if dist.len() - owner.velocity.len() <= 0:
            owner.velocity = owner.velocity.norm() * dist.len()
            owner.path = owner.path[1:] 
        
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
    current_hp = 0
    def enter(self, owner):
        self.start = time.time()
        self.duration = randint(2, 4)
        self.current_hp = owner.hp
        pass


    def exit(self, owner):
        pass

    def path_realizer(self,owner):
        if len(owner.path) <= 0 : 
            owner.need_path = True
            owner.destination = Vector( randint
            (0,50) * POINT_DISTANCE, randint(0,40)* POINT_DISTANCE)
            
        else:
            self.follow_path(owner)

    def have_in_space(self,owner, kind):
        for i in owner.scaner[1]:
            if i.addings[0] == kind:
                return True
        return False

    destination = None
    def execute(self, owner):
        self.path_realizer(owner)
        self.look_at(owner, None)

        if len(owner.scaner[0]) > 0 and owner.hp > 30 and (( owner.ammo_bazooka > 15) or (owner.ammo_railgun > 50)):
            owner.ai.change_state( StateAtack() )
            owner.path = owner.path[:1]

        if len(owner.scaner[1]) > 0 and randint(0,1000) < 30 and len(owner.scaner[0]) == 0:
            owner.ai.change_state( StateCollect() )

        #if self.current_hp != owner.hp :
           # if len(owner.scaner[0]) > 0 and owner.hp > 30 and (( owner.ammo_bazooka > 15) or (owner.ammo_railgun > 50)):
          #      owner.ai.change_state( StateAtack() )
          #      owner.path = owner.path[:1]
         #   else:
        #        owner.ai.change_state( StateRun() )
          #      owner.path = owner.path[:1]
                
            

        pass

class StateRun(State):
    state = "CollecRun"

    start = 0

    def enter(self, owner):
        owner.need_path = True
        owner.destination =  owner.current_position - (( owner.scaner[0][0].current_position - owner.current_position ).norm() * 300 )

        self.start = time.time()
        pass

    def exit(self, owner):
        pass

    def path_realizer(self,owner):
        if len(owner.path) <= 0 :
            owner.ai.change_state( StateCollect() )
        else:
            self.follow_path(owner)
#            self.start = True

    destination = None
    currently_collecting = None   

    def execute(self, owner):

        if not self.has_enemy(owner) and  time.time() - self.start > 1 : owner.ai.change_state( StateCollect() )

        self.path_realizer(owner)
        self.look_at(owner, None)
        pass

class StateCollectArmour(State):
    state = "CollecArmour"

    start = False

    def enter(self, owner):
        owner.need_path = True
        self.currently_collecting = self.get_closest(owner, "AA")
        if self.currently_collecting == None : return
        owner.destination =  self.currently_collecting.current_position
        self.start = False
        pass

    def exit(self, owner):
        pass

    def path_realizer(self,owner):
        if len(owner.path) <= 0 :# and self.start:
            owner.ai.change_state( StateWander() )
        else:
            self.follow_path(owner)
        #    self.start = True

    destination = None
    currently_collecting = None   

    def execute(self, owner):

        if self.has_enemy(owner) and owner.hp < 30 and  not self.have_ammo(owner) : owner.ai.change_state( StateRun() )

        self.path_realizer(owner)
        self.look_at(owner, None)
        pass

class StateCollectAmmoBazooka(State):
    state = "CollecBazooka"

    start = False

    def enter(self, owner):
        owner.need_path = True
        self.currently_collecting = self.get_closest(owner, "AB")
        if self.currently_collecting == None : return
        owner.destination =  self.currently_collecting.current_position
        self.start = False
        pass

    def exit(self, owner):
        pass

    def path_realizer(self,owner):
        if len(owner.path) <= 0 :# and self.start:
            owner.ai.change_state( StateWander() )
        else:
            self.follow_path(owner)
        #    self.start = True

    destination = None
    currently_collecting = None   

    def execute(self, owner):

        if self.has_enemy(owner) and owner.hp < 30 and  not self.have_ammo(owner) : owner.ai.change_state( StateRun() )

        self.path_realizer(owner)
        self.look_at(owner, None)
        pass

class StateCollectHP(State):
    state = "CollecHP"

    start = False

    def enter(self, owner):
        owner.need_path = True
        self.currently_collecting = self.get_closest(owner, "HP")
        if self.currently_collecting == None : return
        owner.destination =  self.currently_collecting.current_position
        self.start = False
        pass

    def exit(self, owner):
        pass

    def path_realizer(self,owner):
        if len(owner.path) <= 0:#  and self.start:
            owner.ai.change_state( StateWander() )
        else:
            self.follow_path(owner)
        #    self.start = True

    destination = None
    currently_collecting = None   

    def execute(self, owner):

        if self.has_enemy(owner) and owner.hp < 30 and  not self.have_ammo(owner) : owner.ai.change_state( StateRun() )

        self.path_realizer(owner)
        self.look_at(owner, None)
        pass

class StateCollectAmmoRailgun(State):
    state = "CollectRailgun"

    start = False

    def enter(self, owner):
        owner.need_path = True
        self.currently_collecting = self.get_closest(owner, "AR")
        if self.currently_collecting == None : return
        owner.destination =  self.currently_collecting.current_position
        self.start = False
        pass

    def exit(self, owner):
        pass

    def path_realizer(self,owner):
        if len(owner.path) <= 0: # and self.start:
            owner.ai.change_state( StateWander() )
        else:
            self.follow_path(owner)
        #    self.start = True

    destination = None
    currently_collecting = None   

    def execute(self, owner):

        if self.has_enemy(owner) and owner.hp < 30 and  not self.have_ammo(owner) : owner.ai.change_state( StateRun() )

        self.path_realizer(owner)
        self.look_at(owner, None)
        pass

class StateCollectEverything(State):
    state = "CollecEverything"

    start = False

    def enter(self, owner):
        owner.need_path = True
        self.currently_collecting = self.get_closest(owner, None)
        if self.currently_collecting == None : return
        owner.destination =  self.currently_collecting.current_position
        self.start = False
        pass

    def exit(self, owner):
        pass

    def path_realizer(self,owner):
        if len(owner.path) <= 0:#  and self.start:
            owner.ai.change_state( StateWander() )
        else:
            self.follow_path(owner)
        #    self.start = True

    destination = None
    currently_collecting = None   

    def execute(self, owner):

        if self.has_enemy(owner) and owner.hp < 30 and  not self.have_ammo(owner) : owner.ai.change_state( StateRun() )

        self.path_realizer(owner)
        self.look_at(owner, None)
        pass

class StateCollect(State):
    state = "Collect"

    def enter(self, owner):
        pass

    def exit(self, owner):
        pass

    destination = None
    currently_collecting = None   

    def execute(self, owner):

        if owner.hp < 40:
            if self.has_enemy(owner):
                owner.ai.change_state( StateRun() ) #RUN
            elif self.have_in_space(owner, "HP"):
                owner.ai.change_state( StateCollectHP() )
            elif self.have_in_space(owner, "AA"):
                owner.ai.change_state( StateCollectArmour())
            else:
                owner.ai.change_state( StateWander() )
        elif owner.hp >= 40:
            if self.has_enemy(owner) :
                if not self.have_ammo(owner): owner.ai.change_state( StateRun() ) #RUN
                else: owner.ai.change_state( StateAtack() )
            if self.have_in_space(owner, "AB") and owner.ammo_bazooka < 30:
                owner.ai.change_state( StateCollectAmmoBazooka() )
            elif self.have_in_space(owner, "AR") and owner.ammo_railgun < 50:
                owner.ai.change_state( StateCollectAmmoRailgun() )

        if len(owner.scaner[1]) == 0: owner.ai.change_state( StateWander() )
        else:                         owner.ai.change_state( StateCollectEverything() )

class StateAtack(State):
    state = "Atack"

    def enter(self, owner):
        self.shoot_railgun = time.time()
        self.shoot_bazooka = time.time()

        owner.need_path           = True
        self.currently_collecting = self.get_closest(owner)
        owner.destination         = Vector( self.currently_collecting.current_position.x + (randint(-3,3)*POINT_DISTANCE),
                                            self.currently_collecting.current_position.y + (randint(-3,3)*POINT_DISTANCE))

    def exit(self, owner):
        pass

    def get_closest(self, owner):
        close = 99999999
        obj   = None
        
        for i in owner.scaner[0]:
            if i.current_position.distance_to(owner.current_position).len() < close:
                obj   = i
                close = i.current_position.distance_to(owner.current_position).len()

        return obj

    def path_realizer(self,owner):
        if len(owner.path) < 1 : 
            owner.need_path = True
            self.currently_collecting = self.get_closest(owner)
            if self.currently_collecting == None: return
            owner.destination  = Vector( self.currently_collecting.current_position.x + randint(-3,3)*POINT_DISTANCE,
                                         self.currently_collecting.current_position.y + randint(-3,3)*POINT_DISTANCE)
        else:
            self.follow_path(owner)



    destination          = None
    currently_collecting = None   

    def have_in_space(self,owner, kind):
        for i in owner.scaner[1]:
            if i.addings[0] == kind:
                return True
        return False


    time_out_railgun = randint(3,5)
    time_out_bazooka = 2
    shoot_railgun    = 0
    shoot_bazooka    = 0

    def launch_bazooka(self, owner):
        if owner.ammo_bazooka > 10 and time.time() - self.shoot_bazooka  > self.time_out_bazooka : 
                owner.bazooka_shot(self.currently_collecting.current_position - owner.current_position + Vector( uniform( -15, 15 ), uniform( -15, 15 )) )
                self.shoot_bazooka = time.time()

    def launch_railgun(self, owner):
        if self.currently_collecting.current_position.distance_to(owner.current_position).len() < 300 :
            if owner.ammo_railgun > 30 and  time.time() - self.shoot_railgun > self.time_out_railgun : 
                owner.railgun_shot(self.currently_collecting.current_position - owner.current_position + Vector( uniform( -15, 15 ), uniform( -15, 15 )))
                self.shoot_railgun = time.time()
                self.time_out_railgun = randint(3,5)

    def execute(self, owner):

        if not self.has_enemy(owner)  : owner.ai.change_state( StateWander()  )
        if self.has_enemy(owner) and ( not self.have_ammo(owner) or owner.hp <= 30 ) : owner.ai.change_state( StateRun()     )

        self.path_realizer(owner)
        self.look_at(owner, self.currently_collecting)
        
        if self.currently_collecting == None: return

        if self.currently_collecting.hp < 0: owner.ai.change_state(StateWander() )


        self.launch_railgun(owner)
        self.launch_bazooka(owner)
