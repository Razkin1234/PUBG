
import pygame , sys
from settings import *
from tile import Tile
from player import Player
from debug import debug
import itertools

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
            offset_position = sprite.rect.topleft - camera + self.screen_center
            self.display_surface.blit(sprite.image, offset_position)

    """""""""
    getting a rectangle and a axis (0 or 1), making the sprite group lusing all the items with the rect 
    we got
    """""
    def remove_sprites_in_rect(self, rect, axis):
        for sprite in sorted(self.sprites(), key=lambda x: (x.rect.centery)):
            if sprite.rect.topleft[axis] == rect:
                sprite.kill()

    def earase_non_relevant_sprites(self,player):
        for sprite in self.sprites():
            if player.rect[0]-(COL_LOAD_TILE_DISTANCE*TILESIZE)> sprite.rect[0] or sprite.rect[0] > player.rect[0]+(COL_LOAD_TILE_DISTANCE*TILESIZE):
                sprite.kill()
            if player.rect[1]-(ROW_LOAD_TILE_DISTANCE*TILESIZE)> sprite.rect[1] or sprite.rect[1] > player.rect[1]+(ROW_LOAD_TILE_DISTANCE*TILESIZE):
                sprite.kill()


    def enemy_update(self,player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and  sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)

    def item_picking(self,player):
        copy_items = self.sprites().copy()
        if player.can_pick_item:
            for sprite in copy_items:
                if sprite.rect.colliderect(player.hitbox):
                    if 'backpack' in player.items_on:
                        count = 13
                    else: count = 10
                    for i in range(1,count):
                        flag = True
                        for item , item_value in player.items_on.items():
                            if item_value['ui'] == i:
                                flag = False
                                break
                        if flag: #we will put the item in this slott
                            if sprite.sprite_type != "backpack" and sprite.sprite_type != 'boots':
                                temp_dict = items_add_data[sprite.sprite_type].copy()
                                temp_dict['ui'] = i
                                counter = 0#for the loop that gives the dict name in player.itmes (can't have the same names)
                                while True:
                                    if not str(counter) in player.items_on:
                                        player.items_on[str(counter)] = temp_dict.copy()
                                        temp_dict.clear()
                                        sprite.kill()
                                        break
                                    counter+=1
                                break
                            elif sprite.sprite_type == 'backpack':
                                if 'backpack' in player.items_on:
                                    break
                                else:
                                    temp_dict = items_add_data[sprite.sprite_type].copy()
                                    temp_dict['ui'] = i
                                    player.items_on['backpack'] = temp_dict.copy()
                                    temp_dict.clear()
                                    sprite.kill()
                            elif sprite.sprite_type == 'boots':
                                if 'boots' in player.items_on:
                                    break
                                else:
                                    temp_dict = items_add_data[sprite.sprite_type].copy()
                                    temp_dict['ui'] = i
                                    player.items_on['boots'] = temp_dict.copy()
                                    temp_dict.clear()
                                    sprite.kill()





