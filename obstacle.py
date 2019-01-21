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
	vertices = [] # tak naprawde wektory, trzeba dodac pozycje - get_vertices() zwraca zsumowane
	basic    = [] 
	position = None
	covered  = []

	def __init__(self, shape_vectors):
		
		self.vertices = shape_vectors
		self.basic = self.vertices.copy()	


	def rotate(self, angle):
		for i in range(len(self.vertices)):
			self.vertices[i] = self.basic[i].rotate(angle)


	def sign(self, p1, p2, p3):
		return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)


	def vertices_to_draw(self):
		vertices_list = []
		for v in self.vertices:
			vertices_list.append((v + self.position).to_touple()) 
			
		return vertices_list

	def get_vertices(self):
		vertices_list = []
		for v in self.vertices:
			vertices_list.append(v + self.position) 
			
		return vertices_list


	def wrapping_square_border_values(self):
		vertex = self.vertices[0] + self.position
		x_min = vertex.x
		y_min = vertex.y
		x_max = vertex.x
		y_max = vertex.y

		for v in self.vertices:
			v += self.position
			if v.x < x_min : x_min = v.x
			if v.x > x_max : x_max = v.x
			if v.y < y_min : y_min = v.y
			if v.y > y_max : y_max = v.y

		return [x_min, x_max, y_min, y_max]


	def wrapping_square(self):
		values = self.wrapping_square_border_values()
		
		return [(values[0],values[2]), (values[1],values[2]), (values[1],values[3]), (values[0],values[3])]

	def is_in_wrapping_square(self, point):
		square = self.wrapping_square_border_values()
		if point.x >= square[0] and point.x <= square[1] and point.y >= square[2] and point.y <= square[3]: 
			return True
		return False
	
class Triangle ( Shape ):

	def __init__(self):
		Shape.__init__(self, self.generate_vertices())

	def generate_vertices(self):
		vertices = []
		vectors = [	Vector(0,1), Vector(-1,-1), Vector(1,-1)]
		for v in range(3):
			vertices.append(vectors[v] * POINT_DISTANCE * randint(MIN_DISTANCE, MAX_DISTANCE))
		return vertices		

	def is_in_figure(self, point):

		d1 = self.sign(point, self.position + self.vertices[0], self.position + self.vertices[1] )
		d2 = self.sign(point, self.position + self.vertices[1], self.position + self.vertices[2] )
		d3 = self.sign(point, self.position + self.vertices[2], self.position + self.vertices[0] )
		
		has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
		has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

		return not (has_neg and has_pos)
		
#	def scale_back_line(self, number):
#		temp        = basic[0] 

#		basic[0] = basic[0] * number
#		basic[1] = basic[1] * number
#		basic[2] = basic[2] * number

#		correction       = basic[0] - temp 

#		for i in range(len(vertices)):
#			basic[i] = basic[i]-correction

class Quadrangle ( Shape ):

	def __init__(self):
		Shape.__init__(self, self.generate_vertices())

	def generate_vertices(self):
		vertices = []
		vectors = [	Vector(0,1), Vector(1,0), Vector(0,-1), Vector(-1,0)]

		for v in range(4):
			vertices.append(vectors[v] * POINT_DISTANCE * randint(MIN_DISTANCE, MAX_DISTANCE))
		return vertices		


	def is_in_figure(self, point):

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


	def is_in_figure(self, point):

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

	representation   = None

	
	
	def __init__(self, screen, screen_size, id, obs_list):
		self.RADIUS = randrange(0 * POINT_DISTANCE, 10 * POINT_DISTANCE, 2 * POINT_DISTANCE) 
		
		if self.RADIUS == 0 : self.RADIUS += 1

		self.current_screen = screen
		self.screen_size = screen_size
		
		self.id = id
		self.generate_square()

		fig = randint(1,3)
		if 	 fig == 1 : self.representation = Triangle()
		elif fig == 2 : self.representation = Quadrangle()
		elif fig == 3 : self.representation = Pentagon()

		self.set_position(obs_list, screen_size)

		self.color = (randint(0,255), randint(0,255), randint(0,255))
	#	self.color = get_color(Colors.GRAY)

		self.representation.covered = self.generate_covered_space()
		points = self.representation.get_vertices()


	def generate_covered_space(self):

		covered_space = []
		square = self.representation.wrapping_square_border_values()

		for x in range( square[0], square[1] + 1, POINT_DISTANCE ):
			for y in range( square[2], square[3] + 1, POINT_DISTANCE ):
				if self.representation.is_in_figure(Vector(x,y) + self.current_position):
					covered_space.append(Vector(x,y) + self.current_position)

	#	print(covered_space)

		return covered_space			
		

	def set_position(self, obs_list, screen_size):
		positionsX = list(range(0, screen_size.x, POINT_DISTANCE ) )
		positionsY = list(range(0, screen_size.y, POINT_DISTANCE ) )
		self.representation.position = Vector( positionsX[randint(0, len(positionsX)-1)], positionsY[randint(0, len(positionsY)-1)])

		overlap = False
		for i in obs_list:
			if self.is_colliding(i):
				overlap = True

		while overlap:
			overlap = False
			self.representation.position = Vector( positionsX[randint(0, len(positionsX)-1)], positionsY[randint(0, len(positionsY)-1)] )
			for i in obs_list:
				if self.is_colliding(i):
					overlap = True


	def is_colliding(self, other):

		for v in self.representation.get_vertices():
			if other.representation.is_in_wrapping_square(v) : return True	

		for v in self.representation.covered:
			if other.representation.is_in_wrapping_square(v) : return True		

		return False

	def generate_square(self):
		
		self.rect = pygame.Rect(   self.RADIUS, 
								 - self.RADIUS,
								 - self.RADIUS, 
								   self.RADIUS)
		self.rect.center = self.current_position.to_touple()

		#self.covered_space = self.representation.covered
		#for x in range( self.rect.right,  self.rect.left + 1, POINT_DISTANCE ):
		#	for y in range( self.rect.top, self.rect.bottom + 1, POINT_DISTANCE ):
		#		self.covered_space.append(Vector(x,y))

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
			return self.representation.covered


	def draw_id_number(self):
		font = pygame.font.SysFont("consolas", int(self.RADIUS/5) )

		text = font.render(str(self.RADIUS ) + " X " + str(self.RADIUS ) , True, self.color)
		text_rect = text.get_rect(center=(self.current_position.x, self.current_position.y))
		self.current_screen.blit(text, text_rect)

	def draw(self):
	#	pygame.draw.rect( self.current_screen, get_color(Colors.GRAY),  self.rect  )	

		pygame.draw.polygon(self.current_screen, self.color, self.representation.vertices_to_draw())
		pygame.draw.polygon(self.current_screen, self.color, self.representation.wrapping_square(), 1)



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