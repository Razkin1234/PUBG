import pygame
from settings import *

class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player

    def shield(self,player,strength,cost,groups):
        if player.exp >= cost and player.can_shield:
            player.can_shield = False
            player.exp -= cost
            self.animation_player.create_particles('aura',player.rect.center,groups)
            player.shield_timer = pygame.time.get_ticks()


    def highspeed(self,player,cost):
        if player.exp >= cost and player.can_run:
            player.can_run = False
            player.exp -= cost
            player.run_timer = pygame.time.get_ticks()

   # def flame(self):

