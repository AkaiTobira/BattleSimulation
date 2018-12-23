import pygame

from random import randint
from vector import *
from colors import Colors, get_color, POINT_DISTANCE

class Node:
    neighbours = []
    position   = None

    def __init__(self, position):
        self.position   = position
        self.neighbours = []

    def set_neighbours(self, llist):
        self.neighbours = llist       

class Graph:
    nodes  = None
    def __init__(self, x_size, y_size):
        self.nodes = []
        for i in range( x_size ):
            self.nodes.append([])
            for j in range( y_size):
                self.nodes[i].append(Node(Vector(i * POINT_DISTANCE, j *POINT_DISTANCE)))

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
        possible_neighbours = [ (-1,0), (1,0), (-1,-1), (1,1), (-1,1), (1,-1), (0,1), (0,-1)]

        for i in range( len(self.nodes) -1):
            for j in range( len(self.nodes[i])-1):
                if self.nodes[i][j] == None :continue
                for neighbour in possible_neighbours:
                    if self.__is_valid(i + neighbour[0], j + neighbour[1]) :
                        self.nodes[i][j].neighbours.append(self.nodes[i + neighbour[0]][j + neighbour[1]])

    def get_random_node(self):
        return self.nodes[randint(0,len(self.nodes)-1)][randint(0, len(self.nodes[0])-1)]

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

    def show_structure(self):
        for i in range(len(self.nodes)):
            for j in range( len(self.nodes[i])):
                print( i, j, self.nodes[i][j].position, self.nodes[i][j].neighbours )
