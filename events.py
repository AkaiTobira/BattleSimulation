import pygame

from enum import IntEnum

# jak uzywac :
# Dopisac kolejny event do Enuma Events 
# wywolac rise_event() tam gdzie zaczelo sie zdarzenie 
# dscription to slownik
# w odpowiednim process_event dodac if-a pasujacego do enuma
# prztworzyc ... tyle



class Events(IntEnum):
	COLLIDE         = 25
	SHOOT           = 26
	IS_READY	    = 27
	INTERSECTION    = 28
	HIT_ENEMY_CHECK = 29
	
def rise_event(event_type, description):
	pygame.event.post(pygame.event.Event(int(event_type), description))