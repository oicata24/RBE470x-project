# This is necessary to find the main code
import sys
import math
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from world import World
import priority_queue

class TestCharacter(CharacterEntity):
    # def __init__(self):
    #     self.wrld = World
    
    def is_cell_walkable(self,wrld, x, y):
        if wrld.wall_at(x,y):
            return False
        if wrld.monsters_at(x,y):
            return False
        if x < 0 or y < 0:
            return False
        return True

    def neighbors_of_4(self, wrld, x, y):
        """
        Returns the walkable 4-neighbors cells of (x,y) in the grid.
        :param x       [int]           The X coordinate in the grid.
        :param y       [int]           The Y coordinate in the grid.
        :return        [(int,int)]   A list of walkable 4-neighbors.
        """
        return_list = list()
        # Never
        if(self.is_cell_walkable(wrld, x, y+1)):
            return_list.append((x,y+1))
        # Eat
        if(self.is_cell_walkable(wrld, x+1, y)):
            return_list.append((x+1,y))
        # Soggy
        if(self.is_cell_walkable(wrld, x, y-1)):
            return_list.append((x,y-1))
        # Watermelons
        if(self.is_cell_walkable(wrld, x-1, y)):
            return_list.append((x-1,y))
        
        return return_list

    def neighbors_of_8(self, wrld, x, y):
        """
        Returns the walkable 8-neighbors cells of (x,y) in the grid.
        :param x       [int]           The X coordinate in the grid.
        :param y       [int]           The Y coordinate in the grid.
        :return        [[(int,int)]]   A list of walkable 8-neighbors.
        """
        return_list = list()
        # add the list of walkable neighbor of 4 grid coordinates
        return_list.extend(self.neighbors_of_4(wrld, x, y)) 
        #  Quadrant 1
        if(self.is_cell_walkable(wrld, x+1, y+1)):
            return_list.append((x+1,y+1))
        #  Quadrant 3
        if(self.is_cell_walkable(wrld, x-1, y-1)):
            return_list.append((x-1,y-1))
        #  Quadrant 2
        if(self.is_cell_walkable(wrld, x-1, y+1)):
            return_list.append((x-1,y+1))
        #  Quadrant 4
        if(self.is_cell_walkable(wrld, x+1, y-1)):
            return_list.append((x+1,y-1))
        
        return return_list

    def grid_to_index(self, wrld, x, y):
        """
        Returns the index corresponding to the given (x,y) coordinates in the occupancy grid.
        :param x [int] The cell X coordinate.
        :param y [int] The cell Y coordinate.
        :return  [int] The index.
        """
        return (y * wrld.width()) + x

    def euclidean_distance(x1, y1, x2, y2):
        """
        Calculates the Euclidean distance between two points.
        :param x1 [int or float] X coordinate of first point.
        :param y1 [int or float] Y coordinate of first point.
        :param x2 [int or float] X coordinate of second point.
        :param y2 [int or float] Y coordinate of second point.
        :return   [float]        The distance.
        """
        ### REQUIRED CREDIT
        return math.sqrt( pow((x2 - x1), 2) + pow((y2 - y1), 2))

    def a_star(self, wrld, start, goal):
        expanded_indices = []
        path = []

        frontier = priority_queue.PriorityQueue()
        start_point = (start[0], start[1])
        came_from = {}
        cost_so_far = {}
        came_from[start_point] = None
        cost_so_far[start_point] = 0
        flag = True
        for cell in self.neighbors_of_8(wrld, start[0], start[1]):
            h = abs(goal[0] - cell[0]) + abs(goal[1] - cell[1])
            frontier.put(cell, h)

        while not frontier.empty():
            print("looping")

            current = frontier.get()
            x = current[0]
            y = current[1]
            

            curr_index = self.grid_to_index(wrld, x, y)
            # print("current index=")
            # print(curr_index)
            expanded_indices.append(curr_index)

            for next in self.neighbors_of_8(wrld, x, y):
                new_cost = cost_so_far[current] + self.euclidean_distance(current[0], current[1], next[0], next[1])
                if next[0] not in cost_so_far or new_cost < cost_so_far[next[0]]:
                    cost_so_far[next[0]] = new_cost
                    heuristic = abs(goal[0] - next[0]) + abs(goal[1] - next[1])
                    priority = new_cost + heuristic
                    frontier.put(next, priority)
                    came_from[next] = current
        
        path_node = (goal[0], goal[1])
        while flag:
            if came_from[path_node] is None :
                flag = False
            else:
                path.insert(0, path_node)
                path_node = came_from[path_node]
        return path

    def do(self, wrld):
        # Your code here
        # If there are no monsters on the field just path plan and execute
        if not wrld.monsters:
            start = (self.x, self.y)
            end = wrld.exitcell
            path = self.a_star(wrld, start, end)
            for cell in path:
                dx = cell[0] - self.x
                dy = cell[1] - self.y
                self.move(dx,dy)

