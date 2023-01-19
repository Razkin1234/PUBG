import pygame , sys
from settings import *
from tile import Tile
from player import Player
from debug import debug

class YsortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        # general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()


def custom_draw(self):
    for sprite in self.sprites():
        self.display_surface.blit(sprite.image , sprite.rect)
