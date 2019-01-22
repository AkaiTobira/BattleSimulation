import pygame

from events import Events, rise_event
from random import randint, randrange
from colors import Colors, get_color, POINT_DISTANCE
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

	def get_verticle(self, id, position):
		return (position + self.vertices[id]).to_touple()

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
	THICKNESS = 4
	RADIUS    = 9
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

	last_hit_by       = None

	representation    = None 

	hp           = 100
	hp_max       = 100
	armour       = 100
	ammo_railgun = 100
	ammo_bazooka = 100

	railgun_to = Vector(0,0)
	draw_railgun = False

	low_hp_color = get_color(Colors.RED)
	hig_hp_color = get_color(Colors.GREEN)

	need_path   = False
	destination = Vector(0,0) 
	path        = []

	scaner      = [[],[]]

	def __init__(self,  screen, screen_size, m_id):
		self.draw_railgun     = False
		self.current_screen   = screen
		self.screen_size      = screen_size
		self.current_position = Vector(randrange(0,self.screen_size.x, POINT_DISTANCE), randrange(0,self.screen_size.y, POINT_DISTANCE))
		self.previous_position= self.current_position
		
		self.destination      = self.current_position
		self.m_id               = m_id
		
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

		self.look_at           = Vector(0,0)

	def check_intersection(self, shoot_from, shoot_to):
		v_shoot = shoot_to - shoot_from
		v_enemy = self.current_position - shoot_from
		dot = v_shoot.norm().dot(v_enemy.norm())

		point = None
		if dot > 0 : 
			v_len = v_enemy.len()
			if v_len > v_shoot.len() : return point
			if dot >  1: dot = 1
			if dot < -1: dot = -1
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

	def bazooka_shot(self, direction):
		rise_event( Events.SHOOT2, {  "atack_type" : "Baz",  "fro" : self.current_position + direction.norm() * 15, "direction" : direction * self.velocity.len() })
		self.ammo_bazooka -= 10

	def railgun_shot(self, direction):
		if self.draw_railgun : return 
		self.railgun_to = self.current_position + ( direction.norm() * 400 )
		rise_event( Events.SHOOT2, {  "atack_type" : "Rai", "enemy_id" : self.m_id,  "fro" : self.current_position + direction.norm()* 15, "to" : self.current_position + ( direction.norm() * 400 ) })
		self.ammo_railgun -= 30
		self.railgun_time_to_draw = time.time()

	def update(self,delta):
		if self.hp < 0: self.is_dead = True
		self.previous_position = self.current_position	
		self.current_position += self.velocity * delta
		self.handle_rotation()
	
	def add_statistic(self, tab):
		if tab[0] == "HP": 
			self.hp += tab[1]
			if self.hp > self.hp_max : self.hp = self.hp_max
		if tab[0] == "AA":  self.armour += tab[1]
		if tab[0] == "AB":  self.ammo_bazooka += tab[1]
		if tab[0] == "AR":  self.ammo_railgun += tab[1]

		percent = (self.hp if self.hp > 0 else 0) / self.hp_max
		if percent > 1 : percent = 1

		self.COLOR = (  self.low_hp_color[0] * (1 - percent) + self.hig_hp_color[0] * percent, 
						self.low_hp_color[1] * (1 - percent) + self.hig_hp_color[1] * percent,
						self.low_hp_color[2] * (1 - percent) + self.hig_hp_color[2] * percent )
			
	def set_to_railgun( self, point):
		self.railgun_to = point
		self.draw_railgun = True

	def handle_rotation(self):
		self.rotate_behaviour.update_position(self.current_position, self.look_at)
		if self.rotate_behaviour.get_rotation_change() :
			self.representation.rotate(self.rotate_behaviour.get_rotation_angle())

	def deal_dmg(self, dmg):
		self.hp     -=  (1 - (self.armour/100)) * dmg
		self.armour -=  dmg
			
		if self.armour < 0 : self.armour = 0

		percent = (self.hp if self.hp > 0 else 0) / self.hp_max
		if percent > 1 : percent = 1

		self.COLOR = (  self.low_hp_color[0] * (1 - percent) + self.hig_hp_color[0] * percent, 
						self.low_hp_color[1] * (1 - percent) + self.hig_hp_color[1] * percent,
						self.low_hp_color[2] * (1 - percent) + self.hig_hp_color[2] * percent )

	def get_ammo(self):
		return [ self.ammo_railgun, self.ammo_bazooka ]

	def is_in_obstacle(self, point):
		if point.distance_to(self.current_position).len() < self.RADIUS: return True
		return False

	def get_hit(self, missle, dmg = 0):
		if missle == None:
			self.deal_dmg( dmg )
			return

		if self.last_hit_by != missle:
			self.last_hit_by = missle
			self.deal_dmg( missle.get_dmg() )
			return

	def draw(self):
		pygame.draw.line(self.current_screen, get_color(Colors.CRIMSON) ,self.current_position.to_table(), ( self.current_position + (self.velocity.norm() * 50 ) ).to_table() , 2 )
		if self.draw_railgun : 
			pygame.draw.line(self.current_screen, get_color(Colors.ORANGERED) , (self.current_position + (self.velocity.norm() * 5 )).to_table(), ( self.railgun_to ).to_table() , 2 )
			if time.time() - self.railgun_time_to_draw > 0.67:
				self.draw_railgun = False

		pygame.draw.circle(self.current_screen, get_color(Colors.BLUE), self.current_position.to_table(), 250, 1 )


	#	pygame.draw.line(self.current_screen, get_color(Colors.KHAKI) ,self.current_position.to_table(), ( self.destination ).to_table() , 2 )


		for p in range( len(self.path) - 1 ):
			pygame.draw.line(self.current_screen, get_color(Colors.KHAKI) , (self.path[p]).to_table(), ( self.path[p+1] ).to_table() , 2 )

		font = pygame.font.SysFont("consolas", int(10) )
		text = font.render( str(self.ammo_bazooka) + " : " + str(self.ammo_railgun) + " \n " +  self.ai.current_state.state , True, self.COLOR)
		text_rect = text.get_rect(center=(self.current_position.x, self.current_position.y - 20))
		self.current_screen.blit(text, text_rect)

		text = font.render( str(self.m_id) , True, get_color(Colors.YELLOW))
		text_rect = text.get_rect(center=(self.current_position.x, self.current_position.y - 40))
		self.current_screen.blit(text, text_rect)




#		self.armour += 1
		if self.visible and not self.is_dead and not self.triggered :
			#ARMOUR
			pygame.draw.circle(self.current_screen, get_color(Colors.WHITE), self.current_position.to_table(), int( 10 * self.armour / 100) )
			#BODY
			pygame.draw.polygon(self.current_screen, self.COLOR, self.representation.to_draw(self.current_position), self.THICKNESS )
			#BAZZOKA
			pygame.draw.circle(self.current_screen, get_color(Colors.GOLD), self.representation.get_verticle(1, self.current_position), int(0.50 * self.ammo_bazooka/10) )
			#RAILGUN
			pygame.draw.circle(self.current_screen, get_color(Colors.DARK_VIOLET), self.representation.get_verticle(2, self.current_position), int(1 * self.ammo_railgun/30) )
		elif not self.visible:
			pass
	#		pygame.draw.circle(self.current_screen, get_color(Colors.DARK_YELLOW), self.current_position.to_table(), self.RADIUS, self.THICKNESS )
		elif self.triggered:
			pygame.draw.polygon(self.current_screen, get_color(Colors.YELLOW), self.representation.to_draw(self.current_position),  self.THICKNESS )
		else :
			pygame.draw.polygon(self.current_screen, get_color(Colors.RED), self.representation.to_draw(self.current_position),  self.THICKNESS )

	#	pygame.draw.line(self.current_screen, get_color(Colors.RED),self.current_position.to_table(), ( self.current_position + self.velocity).to_table(), 2 )
	#	pygame.draw.line(self.current_screen, get_color(Colors.BLUE),Vector(512,0).to_table(), Vector(512,720).to_table(), 2 )