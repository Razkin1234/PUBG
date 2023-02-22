import pygame
from settings import *

class ItemEffect:
    def __init__(self, animation_player):
        self.animation_player = animation_player

    def medkit(self,player,strength,cost,groups): # need to be shild
        """

        :return:shiled is still on
        """
        if player.energy >= cost:
            pass
