import pygame

import math
from events   import Events, rise_event
from random   import randint, randrange
from vector   import Vector
from colors   import Colors, get_color, POINT_DISTANCE

class Triangle:
	vertices = []
	basic    = [] 
	position = Vector(0,0)
	def __init__(self, size):
		self.vertices = [Vector(0.0,-1.0)*size, Vector(-0.7,1.0)*size, Vector(0.7,1.0)*size]
		self.basic = self.vertices.copy()
		
	def rotate(self, angle):
		for i in range(len(self.vertices)):
			self.vertices[i] = self.basic[i].rotate(angle)
		
	def scale_back_line(self, number):
		temp        = self.basic[0] 

		self.basic[0] = self.basic[0] * number
		self.basic[1] = self.basic[1] * number
		self.basic[2] = self.basic[2] * number

		correction       = self.basic[0] - temp 

		for i in range(len(self.vertices)):
			self.basic[i] = self.basic[i]-correction


	def __sign(self, p1, p2, p3):
		return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

	def is_in_triangle(self, point):

		d1 = self.__sign(point, self.position + self.vertices[0], self.position + self.vertices[1] )
		d2 = self.__sign(point, self.position + self.vertices[1], self.position + self.vertices[2] )
		d3 = self.__sign(point, self.position + self.vertices[2], self.position + self.vertices[0] )
		
		has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
		has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

		return not (has_neg and has_pos)

	def to_draw(self, position):
		self.position = position
		return [ (position + self.vertices[0]).to_touple(),
				 (position + self.vertices[1]).to_touple(),
				 (position + self.vertices[2]).to_touple()]


class Obstacle:
	RADIUS 			 = 0
	COLOR_OUT 		 = get_color(Colors.LIGHT_PURPLE)
	THICK  			 = 2


	is_dead          = False
	id 			 	 = -1
	state 			 = "Const"

	color 			 = (0,0,0)
	thick 			 = 0.0
	current_screen   = None
	screen_size		 = Vector(0,0) 
	current_position = Vector(0,0)
	velocity         = Vector(0,0)
	triangle         = None
	rect             = None
	covered_space    = None

	points           = None
	
	
	def __init__(self, screen, screen_size, id, obs_list):
		self.RADIUS = randrange(0 * POINT_DISTANCE, 10 * POINT_DISTANCE,2*POINT_DISTANCE) 
		
		if self.RADIUS == 0 : self.RADIUS += 1

		self.current_screen   = screen
		self.screen_size = screen_size
		
		self.id               = id
		self.set_position(obs_list)

		self.rect = pygame.Rect(   self.RADIUS, 
								 - self.RADIUS,
								 - self.RADIUS, 
								   self.RADIUS)
		self.rect.center = self.current_position.to_touple()

		self.covered_space = []
		for x in range( self.rect.right,  self.rect.left + 1, POINT_DISTANCE ):
			for y in range( self.rect.top, self.rect.bottom + 1, POINT_DISTANCE ):
				self.covered_space.append(Vector(x,y))

		self.RADIUS = self.RADIUS/2

		
		self.points = [ Vector(self.rect.right, self.rect.top   ),
				   Vector(self.rect.right, self.rect.bottom),
				   Vector(self.rect.left , self.rect.top   ),
				   Vector(self.rect.left , self.rect.bottom)
				 ]

	def is_in_obstacle(self, point):
		if point.x >= self.rect.right and point.x <= self.rect.left + 1:
			if point.y >= self.rect.top and point.y <= self.rect.bottom + 1:
				return True
		return False
		
	def get_covered_space(self):
			return self.covered_space


	def set_position(self, obs_list):
		positionsX = list(range(0,self.screen_size.x, POINT_DISTANCE ) )
		positionsY = list(range(0,self.screen_size.y, POINT_DISTANCE ) )
		self.current_position = Vector( positionsX[randint(0, len(positionsX)-1)], positionsY[randint(0, len(positionsY)-1)] )

		#overlap = False
		#for i in obs_list:
		#	if self.is_colliding(i):
		#		overlap = True

		#while overlap:
		#	overlap = False
		#	self.current_position = Vector( positionsX[randint(0, len(positionsX)-1)], positionsY[randint(0, len(positionsY)-1)] )
		#	for i in obs_list:
		#		if self.is_colliding(i):
		#			overlap = True

		self.face 	  = Vector(self.current_position.x, self.current_position.y - 200)

	def is_colliding(self, other):
		distance = (self.current_position - other.current_position).len()
		if distance > (self.RADIUS + other.RADIUS): return False
		return True

	def draw_id_number(self):
		font = pygame.font.SysFont("consolas", int(self.RADIUS/5) )

		text = font.render(str(self.RADIUS ) + " X " + str(self.RADIUS ) , True, self.COLOR_OUT)
		text_rect = text.get_rect(center=(self.current_position.x, self.current_position.y))
		self.current_screen.blit(text, text_rect)

	def draw(self):
		pygame.draw.rect( self.current_screen, get_color(Colors.LIGHT_PURPL2),  self.rect  )
		pygame.draw.rect( self.current_screen, self.COLOR_OUT                ,  self.rect, self.THICK  )
		pygame.draw.circle(self.current_screen, get_color(Colors.DARK_YELLOW), self.current_position.to_table(), int(self.RADIUS))
	#	pygame.draw.polygon (
	#		self.current_screen,  
	#		get_color(Colors.LIGHTER_RED), 
	#		self.triangle.to_draw(self.current_position),
	#		1)
		self.draw_id_number()	


	#def is_in_shade(self, point):
	#	return self.triangle.is_in_triangle(point)

	def line_square_intersection(self, begin, end):
		v_shoot = end - begin
		v_obs   = self.current_position - begin
		dot = (v_shoot.norm()).dot(v_obs.norm())
		if dot < 0: return None
		if v_shoot.len() < v_obs.len(): return None

	# General Equesion of Line
		A = begin.y - end.y
		B = end.x   - begin.x 
		C = ( begin.x - end.x)*begin.y + ( end.y - begin.y)*begin.x

		t = []
		for p in self.points:
			D = A * p.x + B * p.y + C 
			if D == 0 : return p
			t.append( self.__sign(D) )

		for i in range( len(self.points) -1 ):
			if t[i] != 0 or t[i] != t[i+1] : return None

	#	if t[0] ==  1 and t[1] ==  1 and t[2] ==  1 and t[3] ==  1: return None
	#	if t[0] == -1 and t[1] == -1 and t[2] == -1 and t[3] == -1: return None

		return (v_obs.len() * v_shoot.norm()) + begin 

	def __sign(self, n):
		if n > 0 : return 1
		if n < 0 : return -1
		return 0

	def check_intersection(self, shoot_from, shoot_to):
		v_shoot = shoot_to - shoot_from
		v_obs = self.current_position - shoot_from
		dot = v_shoot.norm().dot(v_obs.norm())

		point = None
		if dot > 0 : 
			v_len = v_obs.len()
			angle = math.acos(dot)
			distance = 2 * math.tan(angle/2) * v_len
			if distance <= self.RADIUS:
				v = v_shoot.norm() * v_len
				point = shoot_from + v

		return point		

	def process_event(self,event):

		if event.type == Events.SHOOT:

			point = self.check_intersection(event.pt_from, event.pt_to)

			if point is None:
				point = event.pt_to

			rise_event( Events.INTERSECTION, { "point" : point } )
		
	def set_player_position(self, position):
		self.angle = (self.face - self.current_position).norm().angle_between((position - self.current_position).norm()) 

	def process_physics(self):
		pass
	
	def update(self, delta):
		pass