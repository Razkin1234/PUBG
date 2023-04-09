import pygame
from settings import *

class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player

    def shield(self,player,cost,groups):
        if player.exp >= cost and player.can_shield:
            player.can_shield = False
            player.exp -= cost
            self.animation_player.create_particles('aura',player.rect.center,groups)
            player.shield_timer = pygame.time.get_ticks()


    def highspeed(self,player,cost, packet_to_send):
        if player.exp >= cost and player.can_run:
            player.can_run = False
            player.exp -= cost
            player.speed = 16
            packet_to_send.add_header_player_place_and_image((int(player.rect.center[0]), int(player.rect.center[1])),
                                                             (int(player.place_to_go[0]), int(player.place_to_go[1])),
                                                             16, f'{player.status},no')
            player.run_timer = pygame.time.get_ticks()

    def teleport(self,player,cost): # not good need to change or to make better
        if player.exp >= cost:
            player.exp -= cost
            player.can_teleport = True



