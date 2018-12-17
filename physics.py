import pygame
import math
import time

from vector import Vector
from random import randint
from events import Events, rise_event
from colors import Colors, get_color, POINT_DISTANCE
from graph  import Graph
from objects import *
from ai     import *




class UnitManager:
	obstacle_list = []
	enemy_list    = []
	
	zombie_counter = 0
	player         = None
	screen         = None 
	mv_system      = None
	cl_system      = None
	graph          = None
	start          = 0
	duration       = 0
	items_list    = []
	
	
	def __init__(self, units,  screen,screen_size):
		self.enemy_list       = units[0]
		self.obstacle_list    = units[1]
		self.zombie_counter   = len(self.enemy_list)
		self.screen           = screen
		self.mv_system        = MoveSystem(units)
		self.cl_system        = CollisionSystem(units, screen_size)
		self.graph            = Graph(int(1024/POINT_DISTANCE) + 2,int(720/POINT_DISTANCE) + 2)
		self.duration = randint(15, 20)
		self.start = time.time()
		for obst in units[1]:
			self.graph.remove_nodes( obst.get_covered_space() )
		self.graph.generate_neighbour_net()

		
	def draw(self):
		self.screen.fill(get_color(Colors.NAVYBLUE))
		for obj in ( self.enemy_list + self.obstacle_list ):
			obj.draw()

		for item in self.items_list:
			item.draw()
		self.graph.draw(self.screen)

		
		
	def process_input(self,event):
	
		if event.type == Events.COLLIDE:
			if event.who == 0:
			#	self.player.process_event(event)
			#	if event.hurt : self.player.decrease_HP(1)
				return 
			for unit in self.enemy_list:
				if unit.id == event.who:
					unit.process_event(event)
					return

		for obj in self.obstacle_list:
			obj.process_event(event)	

		for obj in self.enemy_list:
			obj.process_event(event)
	
		#self.player.process_event(event)

	def spawn_item(self, delta):

		node = self.graph.get_random_node()
		while node == None:
			node = self.graph.get_random_node()

		item_id = randint(0,3)
		if item_id == 0 :
			self.items_list.append( ItemHp(self.screen, node.position) )
		else : #item_id == 1 :
			self.items_list.append( ItemAmmo(self.screen, node.position ))
		

					

		pass
		
	def process_physics(self,delta):
		self.mv_system.update(delta)
		self.cl_system.update(delta)

		if  time.time() - self.start > self.duration:
			self.duration = randint(15, 20)
			self.spawn_item(delta)
			self.spawn_item(delta)
			self.spawn_item(delta)
			self.start = time.time()

		for enemy in self.enemy_list:
			if enemy.is_dead: self.enemy_list.remove(enemy)

	def add_unit(self,unit):
		self.zombie_counter += 1
		self.enemy_list.append(unit)

	def has_more_zombie(self):
		return self.zombie_counter != 0

	def remove_unit(self,unit):
		self.zombie_counter -= 1
		pass		
	
class MoveSystem:
	obstacle_list = []
	enemy_list    = []
	whole_objcts  = []
	
	def __init__(self, units):
		self.obstacle_list = units[1]
		self.enemy_list    = units[0] 
		self.whole_objcts  = units[0] + units[1]
	#	self.player        = player

	def __line_intersect(self, position):
		for unit in self.obstacle_list:
			if position.distance_to(unit.current_position).len() < unit.RADIUS:
				return unit
		return None
	
	def hide_unseen_enemy(self, enemy):
		for obstacle in self.obstacle_list:
			is_hide = obstacle.is_in_shade(enemy.current_position)
			if is_hide :
				enemy.visible = False
				return
			enemy.visible = True 

	def update(self, delta):
		for obstacle in self.obstacle_list:
		#	obstacle.set_player_position(self.player.current_position)
			obstacle.update(delta)


		for enemy in self.enemy_list:
		#	self.hide_unseen_enemy(enemy)
			enemy.ai.update(delta)
			enemy.update(delta)
			if enemy.is_dead: self.enemy_list.remove(enemy)

	#	self.player.update(delta)
					
class CollisionSystem:
	enemy_list    = []
	whole_objcts  = []
	obstacle_list = []
	player      = None
	ZERO_VECTOR = Vector(0,0)
	screen_size = Vector(0,0)
	OFFSET      = 1
	start       = 0
	
	def __init__(self, units, screen_size):
		self.start         = time.time()
		self.enemy_list    =  units[0] 
		self.obstacle_list = units[1] 
	#	self.player      = player
		self.screen_size = Vector( screen_size[0], screen_size[1] ) 
		self.whole_objcts  = units[0] + units[1]
	
	def __is_colliding(self, unit, unit_2, distance):
		if unit == unit_2: return False
		if distance > 60.0: return False
		if distance <= math.fabs( unit.RADIUS + unit_2.RADIUS + self.OFFSET ) : return True

	def __is_stuck(self, unit, unit_2, distance):
		if distance <= math.fabs(unit_2.RADIUS - unit.RADIUS + self.OFFSET): return True
		return False

	def __detect_collision_with_obstacle(self, unit,delta):
		for unit_2 in self.obstacle_list:
			distance = ( unit.current_position + unit.velocity*delta ).distance_to(unit_2.current_position + unit_2.velocity*delta).len()
			if self.__is_colliding(unit,unit_2,distance):
				self.__send_collision_message(unit, unit_2, self.__is_stuck(unit,unit_2,distance),delta)

	def __detect_collision_with_unit(self, unit,delta):
		for unit_2 in self.enemy_list:
			distance = ( unit.current_position + unit.velocity*delta ).distance_to(unit_2.current_position + unit_2.velocity*delta).len()
			if self.__is_colliding(unit,unit_2,distance):
				self.__send_collision_message(unit, unit_2, self.__is_stuck(unit,unit_2,distance),delta)
				if not unit_2.velocity.is_zero_len():
					self.__send_collision_message( unit_2, unit, self.__is_stuck(unit_2,unit,distance),delta)

	def __send_collision_message(self, unit, unit_2, is_stuck,delta):
		rise_event(Events.COLLIDE, { "who" : unit.id, "hurt": ( False if unit_2.state == "Const" else True), "stuck" : is_stuck, "with" : unit_2.id, "where" : unit.current_position - unit.velocity*delta  } )

	def is_in_square(self, unit, delta):
		future_positon = unit.current_position + unit.velocity*delta 
	#	print(future_positon, future_positon.x > 0 or future_positon.x < self.screen_size.x,  future_positon.y > 0 or future_positon.y < self.screen_size.y)
		if future_positon.x > 0 and future_positon.x < self.screen_size.x : 
			if future_positon.y > 0 and future_positon.y < self.screen_size.y : 
				return True

		return False

	def __detect_collision_with_wall(self, unit,delta):
		if not self.is_in_square(unit, delta) :
			rise_event(Events.COLLIDE, { "who" : unit.id, "hurt" : False, "stuck" : False, "with" : -1, "where" : unit.current_position - unit.velocity*delta  } )

	#def __detect_collision_for_player(self,delta):
	#	self.__detect_collision_with_obstacle(self.player,delta)
	#	self.__detect_collision_with_unit(self.player,delta)
	#	self.__detect_collision_with_wall(self.player,delta)

	def __detect_collision_for_enemies(self,delta):
		for unit in self.enemy_list:
			if not unit.velocity.is_zero_len():
				self.__detect_collision_with_unit(unit,delta)
				self.__detect_collision_with_obstacle(unit,delta)
	#			self.__detect_collision_with_wall(unit)

	def update(self, delta):
	#	self.__detect_collision_for_player(delta)
		self.__predict_collisions(delta)
		for unit in self.enemy_list:
		#	self.__get_five(unit)
			self.__select_closest(unit)
		#	self.runaway(unit, self.player)
			if unit.is_dead: self.enemy_list.remove(unit)
	#	self.__detect_collision_for_enemies(delta)

	def runaway(self, unit, player):
		if unit.current_position.distance_to(player.current_position).len() < 150 and not unit.triggered and unit.can_react:
		#	unit.ai.change_state( HideBehaviour() )
			unit.can_react = False

	def __select_closest(self, unit):
		closet_one = 99999
		obst      = None 

		for e in self.obstacle_list:
			if e.current_position.distance_to(unit.current_position).len() < closet_one:
				closet_one = e.current_position.distance_to(unit.current_position).len()
				obst = e
				
		unit.closest_hideout = obst


	def __predict_collisions(self,d):
		for unit in self.enemy_list:
			unit.closest_obstacle = self.__get_clossest_obstacle(unit,d)

	def __get_clossest_obstacle(self,unit,delta):
		dist_to_the_closest     = 9999999999
		closest_obstacle        = None

		dynamic = unit.velocity.len() / unit.max_speed.len()

		ahead  = unit.current_position + unit.velocity.norm() * 30
		ahead2 = unit.current_position + unit.velocity.norm() * dynamic


		for obstacle in self.whole_objcts:
			if unit == obstacle : continue
			if obstacle.current_position.distance_to(unit.current_position).len() > 50: continue
			
			distance = ahead2.distance_to(obstacle.current_position).len()
			if distance < dist_to_the_closest:
				if distance < unit.RADIUS + obstacle.RADIUS :
					closest_obstacle    = obstacle
					dist_to_the_closest = distance
					unit.ahead = ahead2
					continue

			distance = ahead.distance_to(obstacle.current_position).len()
			if distance < dist_to_the_closest:
				if distance < unit.RADIUS + obstacle.RADIUS :
					closest_obstacle    = obstacle
					dist_to_the_closest = distance
					unit.ahead = ahead


		return closest_obstacle

	def __get_clossest_obstacle2(self,unit,delta):     
		dist_to_the_closest     = 9999999999
		closest_obstacle        = None
					
		for obstacle in self.whole_objcts:
			if unit == obstacle : continue
			if obstacle.current_position.distance_to(unit.current_position).len() > 50: continue
			
			local_position = unit.current_position.to_local_space(obstacle.current_position)
			if local_position.x < 0: continue
			
			expanded_radius = unit.RADIUS + obstacle.RADIUS
			if abs(local_position.y) > expanded_radius: continue
			
			sqrPart = math.sqrt(expanded_radius**2 - local_position.y**2)
			ip = local_position.x - sqrPart if local_position.x - sqrPart > 0 else local_position.x + sqrPart
			
			if ip < dist_to_the_closest:
				dist_to_the_closest     = ip
				closest_obstacle        = obstacle
		
		return closest_obstacle

	def __get_five(self, unit):
		print( time.time(), self.start )
		if time.time() - self.start < 3 : return  
		
		closest = []
		for enem in self.enemy_list:
			if enem.current_position.distance_to( unit.current_position ).len() < 65:
				if enem.triggered == False : 
					closest.append(enem)
					
			
			if len(closest) > 2:
				print( "NOW GO HUNT!!")
				for c in closest:
					c.triggered = True
					c.ai.set_current_state(PlayerHunt())
				self.start = time.time()
				return