# This is necessary to find the main code
import sys
sys.path.insert(0, '/home/alemoslee/RBE470x-project/Bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.stupid_monster import StupidMonster

# TODO This is your code!
sys.path.insert(1, '/home/alemoslee/RBE470x-project/team10')
from testcharacter import TestCharacter

# Create the game
<<<<<<< HEAD
random.seed(123) # TODO Change this if you want different random choices
g = Game.fromfile('/home/alemoslee/RBE470x-project/team10/project1/map.txt')
=======
random.seed(487) # TODO Change this if you want different random choices
g = Game.fromfile('/home/cb/RBE470x-project/team10/project1/map.txt')
>>>>>>> ba3fb8abc0f5d86febc849fd8368d67b34ce09ea
g.add_monster(StupidMonster("stupid", # name
                            "S",      # avatar
                            3, 9      # position
))

# TODO Add your character
g.add_character(TestCharacter("me", # name
                              "C",  # avatar
                              0, 0  # position
))

# Run!
g.go(1)
