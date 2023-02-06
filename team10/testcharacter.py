# This is necessary to find the main code
import sys
import math
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from world import World
import priority_queue
from enum import Enum


class variation(Enum):
    VARIANT_1 = 1
    VARIANT_2 = 2
    VARIANT_3 = 3
    VARIANT_4 = 4
    VARIANT_5 = 5

class character_mode(Enum):
    pursuit = 0
    retreat = 1

class TestCharacter(CharacterEntity):
    def __init__(self, name, avatar, x, y):
        super().__init__(name, avatar, x, y)
        self.blacklist = set()
        self.retreat_from = (0, 0)
    
    def is_cell_walkable(self,wrld, x, y, recursive=bool):
        if wrld.monsters_at(x, y):
            return False
        if x > wrld.width() -1 or y > wrld.height() - 1:
            return False
        if x < 0 or y < 0:
            return False
        if wrld.wall_at(x,y):
            return False
        if wrld.monsters_at(x,y):
            return False
        if recursive:
            for next in self.neighbors_of_8(wrld, x, y, False):
                if next in self.blacklist:
                    return False
        # if (x,y) in self.blacklist: ## we dont want to get within one space of the monster so leave this out
        #     return False
        
        return True

    def neighbors_of_4(self, wrld, x, y, recursive):
        """
        Returns the walkable 4-neighbors cells of (x,y) in the grid.
        :param x       [int]           The X coordinate in the grid.
        :param y       [int]           The Y coordinate in the grid.
        :return        [(int,int)]   A list of walkable 4-neighbors.
        """
        return_list = list()
        # Never
        if(self.is_cell_walkable(wrld, x, y+1, recursive)):
            return_list.append((x,y+1))
        # Eat
        if(self.is_cell_walkable(wrld, x+1, y, recursive)):
            return_list.append((x+1,y))
        # Soggy
        if(self.is_cell_walkable(wrld, x, y-1, recursive)):
            return_list.append((x,y-1))
        # Watermelons
        if(self.is_cell_walkable(wrld, x-1, y, recursive)):
            return_list.append((x-1,y))
        
        return return_list

    def neighbors_of_8(self, wrld, x, y, recursive):
        """
        Returns the walkable 8-neighbors cells of (x,y) in the grid.
        :param x       [int]           The X coordinate in the grid.
        :param y       [int]           The Y coordinate in the grid.
        :return        [[(int,int)]]   A list of walkable 8-neighbors.
        """
        return_list = list()
        # add the list of walkable neighbor of 4 grid coordinates
        return_list.extend(self.neighbors_of_4(wrld, x, y, recursive)) 
        #  Quadrant 1
        if(self.is_cell_walkable(wrld, x+1, y+1, recursive)):
            return_list.append((x+1,y+1))
        #  Quadrant 3
        if(self.is_cell_walkable(wrld, x-1, y-1, recursive)):
            return_list.append((x-1,y-1))
        #  Quadrant 2
        if(self.is_cell_walkable(wrld, x-1, y+1, recursive)):
            return_list.append((x-1,y+1))
        #  Quadrant 4
        if(self.is_cell_walkable(wrld, x+1, y-1, recursive)):
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

    def euclidean_distance(self, x1, y1, x2, y2):
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

    def a_star(self, wrld, start, goal, recursive):
        path = []

        frontier = priority_queue.PriorityQueue()
        start_point = (start[0], start[1])
        came_from = {}
        cost_so_far = {}
        came_from[start_point] = None
        cost_so_far[start_point] = 0
        flag = True
        frontier.put(start_point, 0)
        # for cell in self.neighbors_of_8(wrld, start[0], start[1]):
        #     h = abs(goal[0] - cell[0]) + abs(goal[1] - cell[1])
        #     frontier.put(cell, h)

        while not frontier.empty():

            current = frontier.get()
            x = current[0]
            y = current[1]
            

            for next in self.neighbors_of_8(wrld, x, y, recursive):
                new_cost = cost_so_far[current] + self.euclidean_distance(current[0], current[1], next[0], next[1])
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
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

    def look_for_monster(self, wrld, rnge):
        for dx in range(-rnge, rnge+1):
            # Avoid out-of-bounds access
            if ((self.x + dx >= 0) and (self.x + dx < wrld.width())):
                for dy in range(-rnge, rnge+1):
                    # Avoid out-of-bounds access
                    if ((self.y + dy >= 0) and (self.y + dy < wrld.height())):
                        # Is a character at this position?
                        if (wrld.monsters_at(self.x + dx, self.y + dy)):
                            return (True, dx, dy)
        # Nothing found
        return (False, 0, 0)
    
    # def minimax(self, wrld, dx, dy):
    #     start = (self.x, self.y)
    #     end = wrld.exitcell

        
    #     monster_move = (0 , 0)
    #     weight = 100 # set some high number so the first distance measurement is always less
    #     for next in self.neighbors_of_8(wrld, self.x + dx, self.y + dy, False): # find all of the monsters next possible moves
    #         d = self.euclidean_distance(self.x, self.y, next[0], next[1])
    #         if d < weight: # expect the monster will pick the move with the shortest distance to the character
    #             weight = d
    #             monster_move = next
    #     self.blacklist.add(monster_move)
    #     path = self.a_star(wrld, start, end, True)
    #     return path

    def minimax(self, wrld, character, monster, depth, is_maximizing):
        if depth == 0:
            return self.heuristic((self.x,self.y), monster)
        moves = self.neighbors_of_8(wrld, )
        if is_maximizing:
            best_value = float('-inf')
            for move in moves:
                character_move = (move[0] - character[0], move[1] - character[1])
                value = self.minimax(wrld, character_move, monster, depth - 1, False)
                best_value = max(best_value, value)
            return best_value
        else:
            best_value = float('inf')
            for move in moves:
                monster_move = (move[0] - monster[0], move[1] - monster[1])
                value = self.minimax(wrld, character, monster_move, depth - 1, True)
                best_value = min(best_value, value)
            return best_value
    
    def get_best_move(friendly, enemy):
        best_value = float('-inf')
        best_move = None
        for move in MOVES:
            new_friendly = move_position(friendly, move)
            value = minimax(new_friendly, enemy, DEPTH, False)
            if value > best_value:
                best_value = value
                best_move = move
        return best_move

    def heuristic(self, wrld, friendly, enemy):
        friendly_distance = self.manhattan_distance(friendly, wrld.exitcell)
        enemy_distance = self.manhattan_distance(enemy, friendly)
        return friendly_distance - enemy_distance

    def manhattan_distance(position1, position2):
        x1, y1 = position1
        x2, y2 = position2
        return abs(x1 - x2) + abs(y1 - y2)


    def do(self, wrld):
        # Your code here
        # If there are no monsters on the field just path plan and execute
        var = variation.VARIANT_3
        # if self.mode == character_mode.pursuit:
        if not wrld.monsters:
            start = (self.x, self.y)
            end = wrld.exitcell
            path = self.a_star(wrld, start, end, False)
            # for cell in path:
            cell = path[0]
            dx = cell[0] - self.x
            dy = cell[1] - self.y
            self.move(dx,dy)
        else: #there are monsters here, change this based on how smart they are
            ## DUMB monsters we treat as normal, Variant 2\
            start = (self.x, self.y)
            end = wrld.exitcell
            monsters_at = self.look_for_monster(wrld, 2)
            path = []
            if monsters_at[0] is True:
                path = self.minimax(wrld, monsters_at[1], monsters_at[2])
            else:
                path = self.a_star(wrld, start, end, False)
            # for cell in path:
            cell = path[0]
            dx = cell[0] - self.x
            dy = cell[1] - self.y
            self.move(dx,dy)
            self.blacklist.clear()
        # if self.mode == character_mode.retreat:
        #     start = (self.x, self.y)
        #         end = wrld.exitcell
        #     self.a_star(wrld, )




