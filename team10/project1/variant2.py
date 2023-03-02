# This is necessary to find the main code
import sys
sys.path.insert(0, '/home/cb/RBE470x-project/Bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.stupid_monster import StupidMonster

# TODO This is your code!
sys.path.insert(1, '/home/cb/RBE470x-project/team10')
from testcharacter import TestCharacter

# Create the game
random.seed(4320) # TODO Change this if you want different random choices
g = Game.fromfile('/home/cb/RBE470x-project/team10/project1/map.txt')
g.add_monster(StupidMonster("stupid", # name
                            "S",      # avatar
                            3, 9      # position
))
my_character = TestCharacter("me", # name
                              "C",  # avatar
                              0, 0  # position
)
# TODO Add your character
g.add_character(my_character)

# Run!
g.go(1)
# my_character.get_reward(g.world) UNCOMMENT FOR TRAINING PURPOSES
