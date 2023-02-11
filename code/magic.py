import pygame
from settings import *

class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player

    def heal(self,player,strength,cost,groups): # need to be shild
        """

        :return:shiled is still on
        """
        if player.energy >= cost:
            pass

    def shield(self,player,strength,cost,groups):
        if player.energy >= cost and player.can_shield:
            player.can_shield = False
            player.energy -= cost

    def flame(self):
        pass
