# This is necessary to find the main code
import sys
sys.path.insert(0, '/home/cb/RBE470x-project/Bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '/home/cb/RBE470x-project/team10')
from testcharacter import TestCharacter

# Create the game
random.seed(357) # TODO Change this if you want different random choices
g = Game.fromfile('/home/cb/RBE470x-project/team10/project1/map.txt')
g.add_monster(SelfPreservingMonster("aggressive", # name
                                    "A",          # avatar
                                    3, 13,        # position
                                    2             # detection range
))

# TODO Add your character
g.add_character(TestCharacter("me", # name
                              "C",  # avatar
                              0, 0  # position
))

# Run!
g.go(1)
# my_character.get_reward(g.world) UNCOMMENT FOR TRAINING PURPOSES

