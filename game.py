import pygame


#from obstacle  import Obstacle as Ob 
from vector    import Vector 
from physics   import UnitManager
from generator import ObjectsGenerator
from colors    import Colors, get_color
#from hud       import HUD


NUMBER_OF_ENEMIES   = 5
NUMBER_OF_OBSTACLES = 20

START_POSITION      = Vector(512,360)

class Game:
	screen      = None
	state       = None
	resolution  = None
	name        = None

	def __init_pygame(self, resolution, name):
		pygame.init()
		pygame.mouse.set_visible(False)
		pygame.display.set_caption(name)
		self.screen = pygame.display.set_mode(resolution)

	def __init__(self, resolution, name):
		self.__init_pygame(resolution,name)
		self.running    = True
		self.state      = StateGame(resolution, name, self.screen)
		self.resolution = resolution
		self.name       = name

	def is_running(self):
		return self.running
	
	def process_input(self):
		while True:
			event = pygame.event.poll()
			if event.type == pygame.NOEVENT:
				return
			if event.type == pygame.QUIT:
				self.running = False
				return
			self.state.process_input(event)

	def update(self,delta):
		if self.state.is_simulation_end(): self.state = StateOver(self.resolution, self.name, self.screen)
		if self.state.restart()          : self.state = StateGame(self.resolution, self.name, self.screen)
		self.state.update(delta)
	
	def draw(self):
		self.state.draw()
		if self.state.state_name == "GAME" : pygame.display.flip()

class Stete:
	need_restart = False

	def restart(self):
		return self.need_restart

	def is_player_dead(self):
		return False

	def no_more_zombie(self):
		return False

	def draw(self):
		return

	def update(self, delta):
		return

	def is_simulation_end(self):
		return False

class StateOver(Stete):
	state_name   = "WIN"
	
	def fill_screen(self, screen):
		screen.fill(get_color(Colors.NAVYBLUE))
		return

	def render_text(self, screen, color, size, text, position):
		font = pygame.font.SysFont("consolas", size)

		text = font.render(text, True, color)
		text_rect = text.get_rect(center=(position.x, position.y))

		screen.blit(text, text_rect)

	
	def draw_label_with_text(self, screen):

		self.render_text(
			screen,
			get_color(Colors.WHITE),
			40,
			"YOU WON",
			START_POSITION
		)

		self.render_text(
			screen,
			get_color(Colors.WHITE),
			20,
			"press space to restart",
			Vector(START_POSITION.x, START_POSITION.y + 60)
		)

		pygame.draw.rect(screen, get_color(Colors.LIGHT_BLUE), [150,170,724,420], 2)	

	def __init__(self, resolution, name, screen):
		
		self.fill_screen(screen)
		self.draw_label_with_text(screen)
		pygame.display.flip()

	def process_input(self,event):
		if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
			if event.scancode == 57:
				self.need_restart = True


class StateGame(Stete):    
	generator   = None
	unitManager = None
	running     = True 
	HUD			= None

	state_name   = "GAME"

	delta_time_ticks      = 0.0
	delta_time_seconds    = 0.0
	
	obj_on_screen = []
	
	def __init_screen_objects(self,resolution,screen):
		self.obj_on_screen = self.generator.create_objects()
	#	self.player        = self.generator.get_spawned_player(START_POSITION, 100)
		self.unitManager   = UnitManager(self.obj_on_screen, screen, resolution)
	#	self.HUD 		   = HUD(screen, self.player)		
	
	def __init__(self, resolution, name, screen):
		self.generator     = ObjectsGenerator(screen, NUMBER_OF_ENEMIES, NUMBER_OF_OBSTACLES,Vector(resolution[0],resolution[1]))
		self.__init_screen_objects(resolution, screen)
		
	def draw(self):
		self.unitManager.draw()



	#	self.HUD.draw() 

	def process_input(self,event):
		self.unitManager.process_input(event)
	#	self.HUD.process_event(event)
			


	def restart(self):
		return False 

	#def is_player_dead(self):
	#	return self.HUD.HP() == 0

	def no_more_zombie(self):
		return len(self.unitManager.enemy_list) == 0

		
	def update(self,delta):
		self.unitManager.process_physics(delta)
	#	self.HUD.update(delta)

