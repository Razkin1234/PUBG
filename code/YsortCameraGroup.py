
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
        self.half_width = self.display_surface.get_size()[0] //2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # creating the floor
        self.floor_surface = pygame.display.get_surface() #the canvas
        self.floor_rect = self.floor_surface.get_rect(topleft = (0,0))

        self.screen_center: pygame.math.Vector2 = pygame.math.Vector2(self.half_width,self.half_height)#the center of the screen


    def custom_draw(self, camera):
        """
       Draws the sprites on screen according to the screen height, and then according to the position of the camera
       :return: None
       """
        # For every visible sprite, from top to bottom
        for sprite in sorted(self.sprites(), key=lambda x: (x.rect.centery)):
            # Display the sprite on screen, moving it by the calculated offset
            self.display_surface.blit(sprite.image, sprite.rect.topleft - camera + self.screen_center)

    def enemy_update(self,player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and  sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)


