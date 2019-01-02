from enum import Enum

POINT_DISTANCE = 25

class Colors(Enum):
	LIGHT_BLUE   = (24,191,158)
	LIGHT_PURPLE = (159,133,188)
	LIGHT_PURPL2 = (26,34,53)	
	LIGHT_RED    = (255,21,82)
	LIGHTER_RED  = (74,28,55)
	RED          = (255,0,0)
	GREEN        = (0,255,0)
	YELLOW       = (255,255,0)
	DARK_YELLOW  = (44,53,42)
	BLUE         = (0,0,255)
	BLACK        = (0,0,0)
	NAVYBLUE	 = (20,30,47)
	WHITE		 = (255,255,255)
	BLUE_BAR	 = (50,160,255)
	KHAKI        = (240,230,140)
	ORANGERED    = (255,69,0)
	GOLD         = (255,215,0)
	GRAY         = (128,128,128)
	CRIMSON      = (220,20,60)
	DARK_VIOLET  = (148,0,211)
	
def get_color( color ):
	if color == Colors.DARK_VIOLET:
		return (148,0,211)
	if color == Colors.GRAY:
		return (128,128,128)
	if color == Colors.CRIMSON:
		return (220,20,60)
	if color == Colors.GOLD:
		return (255,215,0)
	if color == Colors.WHITE:
		return (255,255,255)
	if color == Colors.ORANGERED:
		return (255,69,0)
	if color == Colors.KHAKI:
		return (240,230,140)
	if color == Colors.LIGHT_BLUE:
		return (24,191,158)
	if color == Colors.LIGHT_PURPLE:
		return (159,133,188)
	if color == Colors.LIGHT_RED:
		return (255,21,82)
	if color == Colors.RED:
		return (255,0,0)
	if color == Colors.GREEN:
		return (0,255,0)
	if color == Colors.BLUE:         
		return (0,0,255)
	if color == Colors.BLACK:         
		return (0,0,0)
	if color == Colors.YELLOW:         
		return (255,255,0)	
	if color == Colors.DARK_YELLOW:         
		return (44,53,42)		
	if color == Colors.NAVYBLUE:
		return (20,30,47)	
	if color == Colors.WHITE:
		return (255,255,255)
	if color == Colors.BLUE_BAR:
		return (50,160,255)		
	if color == Colors.LIGHTER_RED:
		return (74,28,55)	
	if color == Colors.LIGHT_PURPL2:
		return (26,34,53)					
