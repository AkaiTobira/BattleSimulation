import pygame

import math
from events   import Events, rise_event
from random   import randint, randrange
from vector   import Vector
from colors   import Colors, get_color, POINT_DISTANCE

# for randomize length of vectors from center of figure to the vertex
MIN_DISTANCE = 1
MAX_DISTANCE = 5

class Shape:
	vertices = []
	basic    = [] 
	position = None

	def __init__(self, shape_vectors):
		self.position = Vector(randint(0,48)*POINT_DISTANCE, randint(0,32)*POINT_DISTANCE)
		self.vertices = self.set_vertices(shape_vectors)
		self.basic = self.vertices.copy()	
		
	#	self.rotate(randint(0,360)) # CRASH, vertices outside the points of the graphh

		self.wrapping_square()

	def set_vertices(self, shape_vectors):
		vertices_list = []
		for vec in shape_vectors: 
			vertices_list.append(vec + self.position)
		return vertices_list	
		
	def rotate(self, angle):
		for i in range(len(self.vertices)):
			self.vertices[i] = self.basic[i].rotate(angle)

	def sign(self, p1, p2, p3):
		return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

	def vertices_to_draw(self):
		vertices_list = []
		for v in self.vertices:
			vertices_list.append(v.to_touple()) 
			
		return vertices_list

	def wrapping_square(self):
		x_min = self.vertices[0].x
		y_min = self.vertices[0].y
		x_max = self.vertices[0].x
		y_max = self.vertices[0].y

		for v in self.vertices:
			if v.x < x_min : x_min = v.x
			if v.x > x_max : x_max = v.x
			if v.y < y_min : y_min = v.y
			if v.y > y_max : y_max = v.y

		return [(x_min,y_min), (x_max,y_min), (x_max,y_max), (x_min,y_max)]

	

class Triangle ( Shape ):

	def __init__(self):
		Shape.__init__(self, self.generate_vertices())

	def generate_vertices(self):
		vertices = []
		vectors = [	Vector(0,1), Vector(-1,-1), Vector(1,-1)]
		for v in range(3):
			vertices.append(vectors[v] * POINT_DISTANCE * randint(MIN_DISTANCE, MAX_DISTANCE))
		return vertices		

		
#	def scale_back_line(self, number):
#		temp        = basic[0] 

#		basic[0] = basic[0] * number
#		basic[1] = basic[1] * number
#		basic[2] = basic[2] * number

#		correction       = basic[0] - temp 

#		for i in range(len(vertices)):
#			basic[i] = basic[i]-correction


	def is_in_triangle(self, point):

		d1 = self.sign(point, self.position + self.vertices[0], self.position + self.vertices[1] )
		d2 = self.sign(point, self.position + self.vertices[1], self.position + self.vertices[2] )
		d3 = self.sign(point, self.position + self.vertices[2], self.position + self.vertices[0] )
		
		has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
		has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

		return not (has_neg and has_pos)


class Quadrangle ( Shape ):

	def __init__(self):
		Shape.__init__(self, self.generate_vertices())

	def generate_vertices(self):
		vertices = []
		vectors = [	Vector(0,1), Vector(1,0), Vector(0,-1), Vector(-1,0)]

		for v in range(4):
			vertices.append(vectors[v] * POINT_DISTANCE * randint(MIN_DISTANCE, MAX_DISTANCE))
		return vertices		


	def is_in_quadrangle(self, point):

		d1 = self.sign(point, self.position + self.vertices[0], self.position + self.vertices[1] )
		d2 = self.sign(point, self.position + self.vertices[1], self.position + self.vertices[2] )
		d3 = self.sign(point, self.position + self.vertices[2], self.position + self.vertices[3] )
		d4 = self.sign(point, self.position + self.vertices[3], self.position + self.vertices[0] )
		
		has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0) or (d4 < 0)
		has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0) or (d4 > 0)

		return not (has_neg and has_pos)


class Pentagon ( Shape ):

	def __init__(self):
		Shape.__init__(self, self.generate_vertices())

	def generate_vertices(self):
		vertices = []
		vectors = [	Vector(0,1), Vector(1,0), Vector(1,-1), Vector(-1,-1), Vector(-1,0)]

		for v in range(5):
			vertices.append(vectors[v] * POINT_DISTANCE * randint(MIN_DISTANCE, MAX_DISTANCE))
		return vertices		


	def is_in_quadrangle(self, point):

		d1 = self.sign(point, self.position + self.vertices[0], self.position + self.vertices[1] )
		d2 = self.sign(point, self.position + self.vertices[1], self.position + self.vertices[2] )
		d3 = self.sign(point, self.position + self.vertices[2], self.position + self.vertices[3] )
		d4 = self.sign(point, self.position + self.vertices[3], self.position + self.vertices[4] )
		d5 = self.sign(point, self.position + self.vertices[4], self.position + self.vertices[0] )
		
		has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0) or (d4 < 0) or (d5 < 0)
		has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0) or (d4 > 0) or (d5 > 0)

		return not (has_neg and has_pos)


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

	rect             = None
	covered_space    = None

	points           = None

	triangle         = None
	quadrangle		 = None
	pentagon 		 = None
	

	
	def __init__(self, screen, screen_size, id, obs_list):
		self.RADIUS = randrange(0 * POINT_DISTANCE, 10 * POINT_DISTANCE, 2 * POINT_DISTANCE) 
		
		if self.RADIUS == 0 : self.RADIUS += 1

		self.current_screen   = screen
		self.screen_size = screen_size
		
		self.id               = id
		self.set_position(obs_list)
		self.generate_square()
	#	self.generate_figure() # comment me if you want !!!

		self.triangle = Triangle()
		self.quadrangle = Quadrangle()
		self.pentagon = Pentagon()

		self.color = (randint(0,255), randint(0,255), randint(0,255))

	def generate_square(self):
		
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
		pygame.draw.rect( self.current_screen, get_color(Colors.GRAY),  self.rect  )	

	#	pygame.draw.polygon(self.current_screen, self.color, self.triangle.vertices_to_draw())
	#	pygame.draw.polygon(self.current_screen, self.color, self.triangle.wrapping_square(), 1)

		pygame.draw.polygon(self.current_screen, self.color, self.quadrangle.vertices_to_draw())
		pygame.draw.polygon(self.current_screen, self.color, self.quadrangle.wrapping_square(), 1)

	#	pygame.draw.polygon(self.current_screen, self.color, self.pentagon.vertices_to_draw())
	#	pygame.draw.polygon(self.current_screen, self.color, self.pentagon.wrapping_square(), 1)



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