import pygame
from settings import *

class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player

    def heal(self,player,strength,cost,groups,shield_on): # need to be shild
        """

        :return:shiled is still on
        """
        if player.energy >= cost and shield_on:
            shiled_on = False
            player.energy -= cost



    def flame(self):
        pass
