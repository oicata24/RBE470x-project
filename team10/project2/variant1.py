# This is necessary to find the main code
import sys

from colorama import Fore, Back
sys.path.insert(0, '/home/cb/RBE470x-project/Bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game
from entity import CharacterEntity

# TODO This is your code!
sys.path.insert(1, '/home/cb/RBE470x-project/team10')

# Uncomment this if you want the empty test character
from testcharacter import TestCharacter

# Uncomment this if you want the interactive character
# from interactivecharacter import InteractiveCharacter

# Create the game
g = Game.fromfile('/home/cb/RBE470x-project/team10/project2/map.txt')

# TODO Add your character
my_character = TestCharacter("me", # name
                              "C",  # avatar
                              0, 0  # position
)
# TODO Add your character
g.add_character(my_character)

# Use this if you want to proceed automatically
g.go(1)
# my_character.get_reward(g.world) UNCOMMENT FOR TRAINING PURPOSES
