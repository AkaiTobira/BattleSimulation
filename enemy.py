import pygame

from events import Events, rise_event
from random import randint
from colors import Colors, get_color
from vector import Vector
from ai     import *

class Triangle:
	vertices = []
	basic    = [] 
	
	def __init__(self, size):
		self.vertices = [Vector(0.0,-1.5)*size, Vector(-1.0,1.0)*size, Vector(1.0,1.0)*size]
		self.basic = self.vertices.copy()
		
	def rotate(self, angle):
		for i in range(len(self.vertices)):
			self.vertices[i] = self.basic[i].rotate(angle)
		
	def to_draw(self, position):
		return [ (position + self.vertices[0]).to_touple(),
				 (position + self.vertices[1]).to_touple(),
				 (position + self.vertices[2]).to_touple()]


class EnemyRotateBehavior:

	position 		  = Vector(0,0)
	face              = Vector(0,0)
	rotation_angle    = 0.0
	rotation_change   = False

	facing            = None

	def __init__(self, position):
		self.position = position

	def update_position(self, position, velocity):
		self.position = position
		self.face 	  = Vector(position.x, position.y - 200)
		self.facing   = velocity
		self.process_rotattion()

	def process_rotattion(self):
		self.rotation_angle = (self.face - self.position).norm().angle_between((self.facing).norm())
		self.rotation_change = True

	def print_rotation_angle(self):
		print("rotate angle: [ " + str(round(self.rotation_angle * 180 / math.pi)) + " ] degrees")

	def get_rotation_angle(self):
		self.rotation_change = False
		return self.rotation_angle	

	def get_rotation_change(self):
		return self.rotation_change

	def set_rotation_change(self, change):
		self.rotation_change = change

class Enemy2:
	THICKNESS = 2
	RADIUS    = 8
	COLOR     = get_color(Colors.LIGHT_BLUE)

	current_screen    = None
	current_position  = Vector(0,0)
	velocity          = Vector(0,0)
	ai                = None
	max_speed         = Vector(50,50)
	m                 = 1
	closest_obstacle  = None

	rotate_behaviour  = None

	ahead             = Vector(0,0)

	priorities        = [0.05, 0.7, 0.5]
	state 			 = "E"
	triggered         = False
	visible			  = True
	is_dead           = False

	representation    = None 

	hp           = 100
	hp_max       = 100
	armour       = 100
	ammo_railgun = 100
	ammo_bazooka = 100

	def __init__(self,  screen, screen_size, id):

		self.current_screen   = screen
		self.screen_size      = screen_size
		self.current_position = Vector(randint(0,self.screen_size.x), randint(0,self.screen_size.y))
		self.previous_position= self.current_position
		
		self.destination      = self.current_position
		self.id               = id
		
		self.distance         = Vector(0.0,0.0)
		self.accumulate       = Vector(0.0,0.0)

		self.ai 			  = FiniteStateMachine(self)
		self.ai.set_current_state(StateWander())
		self.need_target       = True
		self.can_react         = True
		self.mouse_point      = Vector(0,0)
		self.closest_hideout  = None

		self.representation   = Triangle(self.RADIUS)
		self.rotate_behaviour = EnemyRotateBehavior(self.current_position)

		self.triggered         = False
		self.visible		   = True
		self.is_dead           = False

	def check_intersection(self, shoot_from, shoot_to):
		v_shoot = shoot_to - shoot_from
		v_enemy = self.current_position - shoot_from
		dot = v_shoot.norm().dot(v_enemy.norm())

		point = None
		if dot > 0 : 
			v_len = v_enemy.len()
			if v_len > v_shoot.len() : return point
			angle = math.acos(dot)
			distance = 2 * math.tan(angle/2) * v_len
			if distance <= self.RADIUS:
				v = v_shoot.norm() * v_len
				point = shoot_from + v

		return point			

	def process_event(self, event):
		if event.type == pygame.MOUSEMOTION:
			self.mouse_point = Vector(event.pos[0], event.pos[1])

		if event.type == Events.HIT_ENEMY_CHECK:
			point = self.check_intersection(event.pt_from, event.pt_to)

			if point is not None:
				self.is_dead = True

	def bazooka_shot(self):
		rise_event( Events.SHOOT2, {  "atack_type" : "Baz",  "fro" : self.current_position, "direction" : self.velocity })

	def railgun_shot(self):
		rise_event( Events.SHOOT2, {  "atack_type" : "Rai",  "fro" : self.current_position, "to" : self.current_position + ( self.velocity.norm() * 125 ) })

	def update(self,delta):
		self.previous_position = self.current_position	
		self.current_position += self.velocity * delta
		self.handle_rotation()
	
	def handle_rotation(self):
		self.rotate_behaviour.update_position(self.current_position, self.velocity)
		if self.rotate_behaviour.get_rotation_change() :
			self.representation.rotate(self.rotate_behaviour.get_rotation_angle())

	def draw(self):
		#HP & Armor simulation Begin

		self.hp = self.hp - 1
		if ( self.hp == 0) : 
			self.hp = self.hp_max 
			self.bazooka_shot()

		percent = self.hp / self.hp_max

		low_hp_color = get_color(Colors.RED)
		hig_hp_color = get_color(Colors.GREEN)

		self.COLOR = ( low_hp_color[0] * (1 - percent) + hig_hp_color[0] * percent, 
		               low_hp_color[1] * (1 - percent) + hig_hp_color[1] * percent,
					   low_hp_color[2] * (1 - percent) + hig_hp_color[2] * percent )

		self.armour = self.armour + 3

		#HP & Armor simulation End

		pygame.draw.line(self.current_screen, get_color(Colors.KHAKI) ,self.current_position.to_table(), ( self.current_position + (self.velocity.norm() * 50 ) ).to_table() , 2 )

		if self.visible and not self.is_dead and not self.triggered :
			pygame.draw.polygon(self.current_screen,  get_color(Colors.BLACK), self.representation.to_draw(self.current_position), 5 * int(self.armour / 1000) )
			pygame.draw.polygon(self.current_screen, self.COLOR, self.representation.to_draw(self.current_position), self.THICKNESS )
		elif not self.visible:
			pass
	#		pygame.draw.circle(self.current_screen, get_color(Colors.DARK_YELLOW), self.current_position.to_table(), self.RADIUS, self.THICKNESS )
		elif self.triggered:
			pygame.draw.polygon(self.current_screen, get_color(Colors.YELLOW), self.representation.to_draw(self.current_position),  self.THICKNESS )
		else :
			pygame.draw.polygon(self.current_screen, get_color(Colors.RED), self.representation.to_draw(self.current_position),  self.THICKNESS )

	#	pygame.draw.line(self.current_screen, get_color(Colors.RED),self.current_position.to_table(), ( self.current_position + self.velocity).to_table(), 2 )
	#	pygame.draw.line(self.current_screen, get_color(Colors.BLUE),Vector(512,0).to_table(), Vector(512,720).to_table(), 2 )