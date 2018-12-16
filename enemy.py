import pygame

from events import Events, rise_event
from random import randint
from colors import Colors, get_color
from vector import Vector
from ai     import *

class Enemy2:
	THICKNESS = 6
	RADIUS    = 6
	COLOR     = get_color(Colors.LIGHT_BLUE)

	current_screen    = None
	current_position  = Vector(0,0)
	velocity          = Vector(0,0)
	ai                = None
	max_speed         = Vector(50,50)
	m                 = 1
	closest_obstacle  = None

	ahead             = Vector(0,0)

	priorities        = [0.05, 0.7, 0.5]
	state 			 = "E"
	triggered         = False
	visible			  = True
	is_dead           = False

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

		
	def update(self,delta):
		self.previous_position = self.current_position	
		self.current_position += self.velocity * delta

	def draw(self):
		if self.visible and not self.is_dead and not self.triggered :
			pygame.draw.circle(self.current_screen, self.COLOR, self.current_position.to_table(), self.RADIUS, self.THICKNESS )
		elif not self.visible:
			pass
	#		pygame.draw.circle(self.current_screen, get_color(Colors.DARK_YELLOW), self.current_position.to_table(), self.RADIUS, self.THICKNESS )
		elif self.triggered:
			pygame.draw.circle(self.current_screen, get_color(Colors.YELLOW), self.current_position.to_table(), self.RADIUS, self.THICKNESS )
		else :
			pygame.draw.circle(self.current_screen, get_color(Colors.RED), self.current_position.to_table(), self.RADIUS, self.THICKNESS )

	#	pygame.draw.line(self.current_screen, get_color(Colors.RED),self.current_position.to_table(), ( self.current_position + self.velocity).to_table(), 2 )
	#	pygame.draw.line(self.current_screen, get_color(Colors.BLUE),Vector(512,0).to_table(), Vector(512,720).to_table(), 2 )