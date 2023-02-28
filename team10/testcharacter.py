# This is necessary to find the main code
import sys
import math
sys.path.insert(0, '/home/cb/RBE470x-project/Bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from world import World
import priority_queue
from enum import Enum
from events import Event

MINIMAX_DEPTH = 4
import numpy as np

learning_rate_start = 0.9
learning_rate_end = 0.1
decay_rate = 0.0001

class variation(Enum): ## use if you want to do different actions per variant
    VARIANT_1 = 1
    VARIANT_2 = 2
    VARIANT_3 = 3
    VARIANT_4 = 4
    VARIANT_5 = 5

class TestCharacter(CharacterEntity):
    def __init__(self, name, avatar, x, y): 
        super().__init__(name, avatar, x, y)
        self.bomb_placed = False
        self.bomb_at = None
        self.blacklist = set()
        self.monster_at = None
        self.weights = None
        self.game_reward = 0
        self.previous_q = None
        self.current_q = None
        self.delta = 0
        self.gamma = 0.9
        self.alpha = 0.5
        self.fe = 0
        self.fm = 0
        self.fb = 0
        self.fex = 0

    def get_learning_rate(step):
        return learning_rate_end + (learning_rate_start - learning_rate_end) * np.exp(-decay_rate * step)
    
    def is_cell_walkable(self,wrld, x, y):
        if wrld.monsters_at(x, y):
            return False
        if x > wrld.width() -1 or y > wrld.height() - 1:
            return False
        if x < 0 or y < 0:
            return False
        if wrld.wall_at(x,y):
            return False
        # if (x,y) in self.blacklist:
        #     return False
        # if self.monster_at is not None:
        #     for move in self.monster_neighbors_of_16(self.monster_at[0], self.monster_at[1]):
        #         if (x, y) == move:
        #             return False
        
        return True
    
    def get_weights(self):
        w = []
        with open("/home/cb/RBE470x-project/team10/weights1.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                w.append(float(line[:-1]))
        self.weights = w
    
    def write_weights(self):
        with open("/home/cb/RBE470x-project/team10/weights1.txt", "w") as file:
            for weight in self.weights:
                file.write(str(weight) + "\n")
        

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
        # Eatneighbors_of_8
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

    def monster_neighbors_of_16(self, x, y):
        """
        Returns the walkable 8-neighbors cells of (x,y) in the grid.
        :param x       [int]           The X coordinate in the grid.
        :param y       [int]           The Y coordinate in the grid.
        :return        [[(int,int)]]   A list of walkable 8-neighbors.
        """
        return_list = list()
        # add the list of walkable neighbor of 4 grid coordinates
        for dx in range(0, 2):
            for dy in range(0, 2):
                return_list.append((x+dx,y+dy))
                return_list.append((x-dx,y-dy)) 
        return return_list

    def bomb_escape_cells(self, wrld, x, y):
        return_list = list()
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

    def a_star(self, wrld, start, goal):
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
            

            for next in self.neighbors_of_8(wrld, x, y):
                new_cost = cost_so_far[current] + self.euclidean_distance(current[0], current[1], next[0], next[1])
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    heuristic = abs(goal[0] - next[0]) + abs(goal[1] - next[1])
                    priority = new_cost + heuristic
                    frontier.put(next, priority)
                    came_from[next] = current
        
        path_node = (goal[0], goal[1])
        while flag:
            if path_node not in came_from:
                return False
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
    
    ## PROTOTYPE MINIMAX
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
            return self.heuristic(wrld, character, monster)
        
        if is_maximizing: ## Character is the maximizing entity
            best_value = float('-inf')
            moves = self.neighbors_of_8(wrld, character[0], character[1])
            for move in moves:
                # character_move = (move[0] - character[0], move[1] - character[1])
                character_move = (move[0], move[1])
                value = self.minimax(wrld, character_move, monster, depth - 1, False)
                best_value = max(best_value, value)
            return best_value ## Return the Characters best move
        else: ## Monster is the minimizing entitiy
            best_value = float('inf')
            moves = self.neighbors_of_8(wrld, monster[0], monster[1])
            for move in moves:
                # monster_move = (move[0] - monster[0], move[1] - monster[1])
                monster_move = (move[0], move[1])
                value = self.minimax(wrld, character, monster_move, depth - 1, True)
                best_value = min(best_value, value)
            return best_value ## return the monsters best move
    
    def get_best_move(self, wrld, monster):
        best_value = float('-inf')
        best_move = None
        moves = self.neighbors_of_8(wrld, self.x, self.y)
        for move in moves:
            # new_friendly = (move[0] - self.x, move[1] - self.y)
            new_character = (move[0], move[1])
            value = self.minimax(wrld, new_character, monster, MINIMAX_DEPTH, False)
            if value > best_value:
                best_value = value
                best_move = move
        return best_move ## The best heuristic value according to the minimax algorithim

    def heuristic(self, wrld, friendly, enemy):
        friendly_distance = self.manhattan_distance(friendly, wrld.exitcell)
        enemy_distance = self.manhattan_distance(enemy, friendly)
        return friendly_distance - enemy_distance

    def manhattan_distance(self, position1, position2):
        x1, y1 = position1
        x2, y2 = position2
        return abs(x1 - x2) + abs(y1 - y2)

    def blacklist_bombsite(self, rnge):
        bomb = self.bomb_at
        self.blacklist.add(bomb)
        for buffer in range(1, rnge + 1):
            self.blacklist.add((bomb[0] + buffer, bomb[1]))
            self.blacklist.add((bomb[0] - buffer, bomb[1]))
            self.blacklist.add((bomb[0] , bomb[1] + buffer))
            self.blacklist.add((bomb[0] , bomb[1] - buffer))

    def get_reward(self, wrld=World):
        """Updates reward and manages events"""
        events = wrld.events
        reward = 0
        rewrite_weights = False
        for e in events:
            if e.tpe == Event.BOMB_HIT_WALL:
                reward += 10
            if e.tpe == Event.BOMB_HIT_MONSTER:
                reward += 50
            if e.tpe == Event.BOMB_HIT_CHARACTER:
                reward -= 1000
                rewrite_weights = True
            if e.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
                reward -= 10000
                rewrite_weights = True
            if e.tpe == Event.CHARACTER_FOUND_EXIT:
                reward += 10000
                rewrite_weights = True

        if reward == 0:
            start = (self.x, self.y)
            end = wrld.exitcell
            path = self.a_star(wrld, start, end)
            reward = wrld.time + (2*len(path))
        if rewrite_weights:
            counter = 0
            new_weights = []
            functions = [self.fe, self.fm, self.fb, self.fex]
            if self.previous_q is not None:
                prev_q = self.previous_q
                ## set new q as previous q
                self.previous_q = self.game_reward + self.gamma(self.current_q) - prev_q
                self.delta = self.previous_q - prev_q
            for weight in self.weights:
                new_weight = weight + self.alpha(self.delta)(functions[counter])
                new_weights.append(new_weight)
                counter += 1
            self.write_weights()
        self.game_reward = reward
    
    def q_learning(self, wrld, state):
        max_q = -math.inf
        best_move = None
        for action in self.neighbors_of_8(wrld, state[0], state[1]):
            next_x = action[0]
            next_y = action[1]
            # Distace to exit
            de = len(self.a_star(wrld, (next_x,next_y), wrld.exitcell))
            self.fe = 1/(1+de)
            # Distance to monster
            dm = 0
            # Distance to bomb
            db = 0
            # Distance to explosion
            dex = 0
            if wrld.monsters is not None:
                closest_monster_distance = math.inf
                for monster in wrld.monsters:
                    entity = self.monsters[monster]
                    dist_to_monster = len(self.a_star(wrld, (next_x,next_y), (entity[0].x, entity[0].y)))
                    if  dist_to_monster < closest_monster_distance:
                        closest_monster_distance = dist_to_monster
                dm = closest_monster_distance
            self.fm = 1/(1+dm)
            if wrld.bombs is not None:
                for bomb in wrld.bombs:
                    entity = wrld.bombs[bomb]
                    db = self.euclidean_distance(next_x, next_y, entity.x, entity.y)
            self.fb = 1/(1+db)
            if wrld.explosions is not None:
                closest_explosion_distance = math.inf
                for explosion in wrld.explosions:
                    entity = wrld.explosions[explosion]
                    dist_to_explosion = self.euclidean_distance(next_x, next_y, entity.x, entity.y)
                    if  dist_to_explosion < closest_explosion_distance:
                        closest_explosion_distance = dist_to_explosion
                dex = closest_explosion_distance
            self.fex = 1/(1+dex)
            q = self.weights[0]*(self.fe) + self.weights[1]*(self.fm) + self.weights[2]*(self.fb) + self.weights[3]*(self.fex)
            if q > max_q:
                max_q = q
                best_move = (next_x, next_y)
        return best_move

    # def do(self, wrld):
    #     # Your code here
    #     # If there are no monsters on the field just path plan and execute
    #     var = variation.VARIANT_3
    #     if self.bomb_placed is True and not wrld.explosions and not wrld.bombs:
    #         self.bomb_placed = False
    #         self.blacklist.clear()
    #         self.bomb_at = None
    #     if not wrld.monsters:
    #         start = (self.x, self.y)
    #         end = wrld.exitcell
    #         path = self.a_star(wrld, start, end)
    #         if path is False: ## no viable path to goal
    #             end = (0,0)
    #             path = self.a_star(wrld, start, end)
    #         if path is False: ## no viable path to start and goal
    #             best_move = None
    #             best_value = float('inf')
    #             for move in self.neighbors_of_8(wrld, start[0], start[1]):
    #                 value = self.manhattan_distance(move, end)
    #                 if value < best_value:
    #                     best_value = value
    #                     best_move = move
    #             path = [best_move]
    #         # for cell in path:
    #         cell = path[0]
    #         dx = cell[0] - self.x
    #         dy = cell[1] - self.y
    #         self.move(dx,dy)
    #     else: #there are monsters here, change this based on how smart they are
    #         ## DUMB monsters we treat as normal, Variant 2\
    #         start = (self.x, self.y)
    #         end = wrld.exitcell
    #         monsters_at = self.look_for_monster(wrld, 2) ## Checking to see if mnster exists within a range of 2
    #         path = []
    #         cell = None
    #         if monsters_at[0] is True: ## Yes monsters within range
    #             self.monster_at = (self.x + monsters_at[1], self.y + monsters_at[2])
    #             if self.bomb_placed:
    #                 start = (self.x, self.y)
    #                 end = (0,0)
    #                 if start == end:
    #                     end = (0,1)
    #                 path = self.a_star(wrld, start, end)
    #                 if path is False: ## no viable path to start
    #                     end = wrld.exitcell
    #                     path = self.a_star(wrld, start, end)
    #                 if path is False: ## no viable path to both start and end
    #                     best_move = None
    #                     best_value = float('inf')
    #                     for move in self.neighbors_of_8(wrld, start[0], start[1]):
    #                         value = self.manhattan_distance(move, end)
    #                         if value < best_value:
    #                             best_value = value
    #                             best_move = move
    #                     path = [best_move]
    #                 # for cell in path:
    #                 cell = path[0]
    #                 dx = cell[0] - self.x
    #                 dy = cell[1] - self.y
    #                 self.move(dx,dy)
    #                 return
    #             self.place_bomb()
    #             self.bomb_placed = True
    #             self.bomb_at = (self.x, self.y)
    #             cell = self.get_best_move(wrld, self.monster_at)
    #             self.blacklist_bombsite(4)
    #             start = (self.x, self.y)
    #             end = (0,0)
    #             if start == end:
    #                 end = (0,1)
    #             path = self.a_star(wrld, start, end)
    #             if path is False: ## no viable path to start
    #                 end = wrld.exitcell
    #                 path = self.a_star(wrld, start, end)
    #             if path is False: ## no viable path to both start and end
    #                 best_move = None
    #                 best_value = float('inf')
    #                 for move in self.neighbors_of_8(wrld, start[0], start[1]):
    #                     value = self.manhattan_distance(move, end)
    #                     if value < best_value:
    #                         best_value = value
    #                         best_move = move
    #                 path = [best_move]
    #                 # for cell in path:
    #                 cell = path[0]
    #                 dx = cell[0] - self.x
    #                 dy = cell[1] - self.y
    #                 self.move(dx,dy)
    #             return
    #         else: ## no monsters nearby proceed as normal
    #             self.monster_at = None
    #             path = self.a_star(wrld, start, end)
    #             if path is False: ## no viable path to goal
    #                     end = (0,0)
    #                     path = self.a_star(wrld, start, end)
    #             if path is False: ## no viable path to start and goal
    #                 best_move = None
    #                 best_value = float('inf')
    #                 for move in self.neighbors_of_8(wrld, start[0], start[1]):
    #                     value = self.manhattan_distance(move, end)
    #                     if value < best_value:
    #                         best_value = value
    #                         best_move = move
    #                 path = [best_move]
    #             cell = path[0]
    #             dx = cell[0] - self.x
    #             dy = cell[1] - self.y
    #             self.move(dx,dy)
    def do(self, wrld):
        if self.weights is None:
            self.get_weights()
        if self.look_for_monster(wrld, 2)[0] is True:
            self.place_bomb()
        best_move = self.q_learning(wrld, (self.x,self.y))
        self.get_reward(wrld)
        dx = best_move[0] - self.x
        dy = best_move[1] - self.y
        self.move(dx,dy)



