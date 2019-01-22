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
	path = []
	
	def __init__(self, units,  screen,screen_size):
		self.enemy_list       = units[0]
		self.obstacle_list    = units[1]
		self.items_list       = []
		self.zombie_counter   = len(self.enemy_list)
		self.screen           = screen
		self.graph            = Graph(int(1200/POINT_DISTANCE) ,int(800/POINT_DISTANCE) )
		self.duration         = randint(15, 20)
		self.start            = time.time()
		
		for obst in units[1]:
		#	print(obst.get_covered_space())
			self.graph.remove_nodes( obst.get_covered_space() )
		self.graph.generate_neighbour_net()

		for unit in range(len(units[0])):
			units[0][unit].current_position = self.graph.get_closeset_node( Vector( randint(0, 1024), randint(0, 720) )).position

		self.mv_system        = MoveSystem(units)
		self.cl_system        = CollisionSystem(units, screen_size)

		
	def draw(self):
		self.screen.fill(get_color(Colors.NAVYBLUE))
		for obj in ( self.enemy_list + self.obstacle_list ):
			obj.draw()

		for item in self.items_list:
			item.draw()

		self.graph.draw(self.screen)
		
	def get_enemy(self, l_id):
		for enemy in self.enemy_list:
			if l_id == enemy.m_id: return enemy 

	def process_input(self,event):
	
		if event.type == Events.SHOOT2:
			if event.atack_type == "Baz":
				self.items_list.append( BazookaMissle( self.screen, event.fro, event.direction))
				return
			if event.atack_type == "Rai":
				point = event.to
				for obstacle in self.obstacle_list:
					point_condidate = obstacle.line_square_intersection( event.fro, event.to)
					if point_condidate is None: continue
					if point_condidate.distance_to(event.fro).len() < point.distance_to(event.fro).len() : point = point_condidate
				self.get_enemy(event.enemy_id).set_to_railgun(point)
				for enemy in self.enemy_list:
					if event.enemy_id == enemy.m_id : continue
					if enemy.is_dead              : continue
					if enemy.check_intersection( event.fro, point ):
						enemy.get_hit(None, 67)
				return

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

		self.path = self.graph.get_path( Vector(0,0), self.graph.get_random_node().position )

		node = self.graph.get_random_node()
		while node == None:
			node = self.graph.get_random_node()

		item_id = randint(0,4)
		if item_id == 0 :
			self.items_list.append( ItemHp(self.screen, node.position) )
		elif item_id == 1 :
			self.items_list.append( ItemAmmoBazzoka(self.screen, node.position ))
		elif item_id == 2 :
			self.items_list.append( ItemArmour(self.screen, node.position))
		else :
			self.items_list.append( ItemAmmoRailgun(self.screen, node.position ))
		pass
		


	def check_spawn_item_time(self, delta):
		if  time.time() - self.start > self.duration:
			self.duration = randint(13, 17)
			for i in range(8):
				self.spawn_item(delta)
			self.start = time.time()

	def scan_space_for_items(self, enemy):
		in_range_objects = []
		for item in  self.items_list :
			if item.current_position.distance_to(enemy.current_position).len() < ( 250 ):
				in_range_objects.append(item)
		return in_range_objects

	def scan_space_for_enemies(self, enemy):
		in_range_enemies = []
		for enemy2 in self.enemy_list:
			if enemy == enemy2 : continue
			if enemy2.current_position.distance_to(enemy.current_position).len() < ( 250 ):
				in_range_enemies.append(enemy2)	
		return in_range_enemies

	def process_path_need(self, enemy):
		if enemy.need_path : 
			enemy.path = self.graph.get_path(enemy.current_position, enemy.destination)
		#	print( enemy.path, enemy.current_position, enemy.destination)
			if len(enemy.path) != 0: enemy.need_path = False

	def process_physics(self,delta):
		self.mv_system.update(delta)
	#	self.cl_system.update(delta)

		self.check_spawn_item_time(delta)

		for enemy in self.enemy_list:
			enemy.scaner = [ self.scan_space_for_enemies(enemy), 
							 self.scan_space_for_items(enemy) ]

			self.process_path_need(enemy)

			if enemy.is_dead: 
				print( "PLayer " + str(enemy.m_id) + " eliminated" )
				self.enemy_list.remove(enemy)
		
		for item in self.items_list:

			if item.is_missle : 
				if not item.explode : self.cl_system.missle_impact(item)
				else : self.cl_system.get_hit(item)
			else :
				for enemy in self.enemy_list:
					if item.current_position.distance_to(enemy.current_position).len() < ( 15 + item.RADIUS ):
						enemy.add_statistic( item.get_addigs() )

			if item.exist : item.update(delta) 
			else : self.items_list.remove(item)

		

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
			if enemy.is_dead: 
				print( "PLayer " + str(enemy.m_id) + " eliminated" )
				self.enemy_list.remove(enemy)

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
	

	def __send_collision_message(self, unit, unit_2, is_stuck,delta):
		rise_event(Events.COLLIDE, { "who" : unit.id, "hurt": ( False if unit_2.state == "Const" else True), "stuck" : is_stuck, "with" : unit_2.id, "where" : unit.current_position - unit.velocity*delta  } )

	def is_in_square(self, unit, delta):
		future_positon = unit.current_position + unit.velocity*delta 
	#	print(future_positon, future_positon.x > 0 or future_positon.x < self.screen_size.x,  future_positon.y > 0 or future_positon.y < self.screen_size.y)
		if future_positon.x > 0 and future_positon.x < self.screen_size.x : 
			if future_positon.y > 0 and future_positon.y < self.screen_size.y : 
				return True

		return False

	def get_hit(self, missle):
		for enemy in self.enemy_list:
			if missle.current_position.distance_to(enemy.current_position).len() < enemy.RADIUS:
				enemy.get_hit(missle) 	

	def missle_impact(self, missle):
		for obj in self.whole_objcts:
			if obj.is_in_obstacle(missle.current_position):
				if obj.is_dead : continue
#			if missle.current_position.distance_to(obj.current_position).len() < obj.RADIUS:
				missle.make_explode() 	
			if obj.state == "Const":
				if obj.representation.is_in_figure(missle.current_position):
					if obj.is_dead : continue
	#			if missle.current_position.distance_to(obj.current_position).len() < obj.RADIUS:
					missle.make_explode() 

	def update(self, delta):
		self.__predict_collisions(delta)
		for unit in self.enemy_list:
			self.__select_closest(unit)
			if unit.is_dead:
				print( "PLayer " + str(unit.m_id) + " eliminated" )
				self.enemy_list.remove(unit)

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