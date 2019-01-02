import pygame

from random import randint
from vector import *
from colors import Colors, get_color, POINT_DISTANCE
from queue  import PriorityQueue, Queue

class Node:
    neighbours = []
    position   = None

    def __init__(self, position):
        self.position   = position
        self.neighbours = []


    def __lt__(self, other):
        return self.position.len() > other.position.len()

    def set_neighbours(self, llist):
        self.neighbours = llist       

class Graph:
    serc       = {}
    nodes  = None
    def __init__(self, x_size, y_size):
        self.nodes = []
        self.serc       = {}
        for i in range( x_size + 2 ):
            self.nodes.append([])
            for j in range( y_size + 2):
                self.nodes[i].append(Node(Vector(i * POINT_DISTANCE, j *POINT_DISTANCE)))


    def get_closeset_node(self, position):
        index_curr = Vector(int(position.x/POINT_DISTANCE), int(position.y/POINT_DISTANCE))

        distance  = 9999999999
        increment = 0
        node      = None
        while distance > 9999999998:
            for i in range( (index_curr.x - increment     if ( index_curr.x - increment > 0)                            else 0 ), 
                            ( index_curr.x + increment + 2 if ( index_curr.x + increment + 2 < len( self.nodes ) -1  ) else len( self.nodes ) - 1), 1 ):            
                for j in range( (index_curr.y - increment if ( index_curr.y - increment > 0)                                else 0) , 
                                (index_curr.y + increment + 2 if ( index_curr.y + increment + 2 < len( self.nodes[0]) -1  ) else len( self.nodes[0] ) -1), 1 ):
                    if self.nodes[i][j] == None: continue
                    if distance > position.distance_to(self.nodes[i][j].position).len() :
                        distance = position.distance_to(self.nodes[i][j].position).len()
                        node     = self.nodes[i][j]
            increment += 1
        return node 

#        que.put()


#        closest 
#        for i in range( index_curr.x, index_curr.x + 2, 1 ):
#            for j in range( index_curr.x, index_curr + 2, 1):        




    def remove_node(self, node_position):
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes[i])):
                if self.nodes[i][j] != None and self.nodes[i][j].position == node_position:
                    self.nodes[i][j] = None

    def remove_nodes(self, nodes_position_list):
        for node in nodes_position_list:
            self.remove_node(node)

    def __is_valid(self, i, j):
        if i >= 0 and i < len(self.nodes):
            if j >= 0 and j < len(self.nodes):
                if self.nodes[i][j] != None:
                    return True
        return False

    def generate_neighbour_net(self):
        possible_neighbours = [ (-1,0), (1,0), (0,1), (0,-1), (-1,-1), (1,1), (-1,1), (1,-1)]

        for i in range( len(self.nodes) -1):
            for j in range( len(self.nodes[i])-1):
                if self.nodes[i][j] == None :continue
                for neighbour in possible_neighbours:
                    if self.__is_valid(i + neighbour[0], j + neighbour[1]) :
                        self.nodes[i][j].neighbours.append(self.nodes[i + neighbour[0]][j + neighbour[1]])

    def get_random_node(self):
        node = self.nodes[randint(1,len(self.nodes)-2)][randint(1, len(self.nodes[0])-2)]
        while node == None:
            node = self.nodes[randint(1,len(self.nodes)-2)][randint(1, len(self.nodes[0])-2)]
        return node

    def get_node(self,i,j):
        return self.nodes[i][j]

    def draw(self, screen):
        for i in range(len(self.nodes)):
            for j in range( len(self.nodes[i])):
                if self.nodes[i][j] is None : continue
                pygame.draw.circle(screen, (255,255,255), self.nodes[i][j].position.to_table(), 1 )
                if self.nodes[i][j].neighbours is None : continue
                for neighbour in self.nodes[i][j].neighbours:
                    pygame.draw.line(screen, get_color(Colors.RED),self.nodes[i][j].position.to_table(), neighbour.position.to_table(), 1 )

        if len( self.serc.keys() ) == 0: return 
       # for p in self.serc.keys():
       #     pygame.draw.circle(screen, get_color(Colors.GOLD), p.position.to_table(), 3 )
        #    if self.nodes[i][j] is None : continue
        #        pygame.draw.circle(screen, (255,255,255), self.nodes[i][j].position.to_table(), 1 )
        #        if self.nodes[i][j].neighbours is None : continue
        #        for neighbour in self.nodes[i][j].neighbours:
        #            pygame.draw.line(screen, get_color(Colors.RED),self.nodes[i][j].position.to_table(), neighbour.position.to_table(), 1 )

    def show_structure(self):
        for i in range(len(self.nodes)):
            for j in range( len(self.nodes[i])):
                print( i, j, self.nodes[i][j].position, self.nodes[i][j].neighbours )

        

    def get_path(self, c_pos, d_pos):

        start_pos = self.get_closeset_node(c_pos).position/POINT_DISTANCE
        end_pos   = self.get_closeset_node(d_pos).position

    #    print( "ASTAR : Finding Path beetween : ", start_pos, start_pos*POINT_DISTANCE, " : ", end_pos/POINT_DISTANCE, end_pos )

        openQue = PriorityQueue()
        closedSet = {}

        openQue.put( (0, self.nodes[int(start_pos.x)][int(start_pos.y)] ) )
        
        closedSet[self.nodes[int(start_pos.x)][int(start_pos.y)]] = [ 0, None, False, True ]

        if self.nodes[int(start_pos.x)][int(start_pos.y)] == None: return []

        number = 0

        while( not openQue.empty() ):
            s = openQue.get()[1]
            closedSet[s][2] = True  # add to closedSet
            closedSet[s][3] = False # remove form openset

            if s.position == end_pos: 
                t = []
                k = s
                while not closedSet[k][1] == None:
                    t.append(k.position)
                    k = closedSet[k][1]
                t.append(k.position)
                t.reverse()
                self.serc = closedSet
                return t

            number += 1

            for n in s.neighbours:
                tgs = closedSet[s][0] + self.__distance(n, s.position)
                if not n in closedSet.keys():
                    closedSet[n] = [ tgs , s, False, True ]
                    openQue.put(  ( (tgs  + self.__heuresitc(end_pos, n)), n )  )
                if n in closedSet.keys():
                    if closedSet[n][2]: continue
                    if closedSet[n][3]:
                        if tgs < closedSet[n][0]:                
                            closedSet[n] = [ tgs , s, closedSet[n][2], closedSet[n][3] ]

            #    if not neighbour in closedSet.keys():
            #        closedSet[ neighbour ] = [ p, n[1], False ] # lowest, previous, is_closed
            #        openQue.put( (p, neighbour) )
            #    else:
            #        if closedSet[ neighbour ][0] >= p :
            #            closedSet[ neighbour ] = [ p, n[1], closedSet[ neighbour ][2] ]
            #            openQue.put( (p, neighbour) )
                    #elif closedSet[ neighbour ][2]:
                    #    if closedSet[ neighbour ][0] >= p :
                    #        closedSet[ neighbour ] = [ p, n[1], closedSet[ neighbour ][2] ]
                    #        openQue.put( (p, neighbour) )

#            closedSet[n[1]][2] = True
    #    print( " PATH NOT FOUND ", number, " ELEMENETS CHANGED ")
        return []

    def __distance(self, n, pos):
        return n.position.distance_to(pos).len()

    def __heuresitc(self,  pos, n):
        dx = abs( pos.x - n.position.x)
        dy = abs( pos.y - n.position.y)
        return dx + dy 