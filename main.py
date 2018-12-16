import pygame
 
 
from time     import sleep
from game     import Game 
 
def main():

	game = Game((1024,720), "Zombie2D")
	clock = pygame.time.Clock()

	while game.is_running():
		delta = clock.tick()/1000
		game.process_input()
		game.update(delta)
		game.draw()
		
if __name__=="__main__":
	main()