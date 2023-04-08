import logging
from typing import Tuple

import pygame, sys

from enemy import Enemy
from settings import *
from tile import Tile
from player import Player
from debug import debug
from bullet import Bullets
from entity import Entity
import itertools
from Players import Players
from ConnectionToServer import ConnectionToServer
import threading


class YsortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        # general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # creating the floor
        self.floor_surface = pygame.display.get_surface()  # the canvas
        self.floor_rect = self.floor_surface.get_rect(topleft=(0, 0))

        self.screen_center: pygame.math.Vector2 = pygame.math.Vector2(self.half_width,
                                                                      self.half_height)  # the center of the screen

    def custom_draw(self, camera):
        """
       Draws the sprites on screen according to the screen height, and then according to the position of the camera
       :return: None
       """
        # For every visible sprite AT THE MOMENT!!!, from top to bottom
        current_frame_sprites = self.sprites()
        for sprite in sorted(current_frame_sprites, key=lambda x: x.rect.centery):
            # print(f'{sprite=}')
            # print('hello')
            # Display the sprite on screen, moving it by the calculated offset
            offset_position = sprite.rect.topleft - camera + self.screen_center
            self.display_surface.blit(sprite.image, offset_position)

    """""""""
    getting a rectangle and a axis (0 or 1), making the sprite group lusing all the items with the rect 
    we got
    """""

    def other_player_motion(self, player):
        for sprite in self.sprites():
            sprite.animation()

    def remove_sprites_in_rect(self, rect, axis):
        for sprite in sorted(self.sprites(), key=lambda x: x.rect.centery):
            if sprite.rect.topleft[axis] == rect:
                sprite.kill()

    def earase_non_relevant_sprites(self, player):
        for sprite in self.sprites():
            if player.rect[0] - (COL_LOAD_TILE_DISTANCE * TILESIZE) > sprite.rect[0] or sprite.rect[0] > player.rect[0]\
                    + (COL_LOAD_TILE_DISTANCE * TILESIZE):
                sprite.kill()
            if player.rect[1] - (ROW_LOAD_TILE_DISTANCE * TILESIZE) > sprite.rect[1] or sprite.rect[1] > player.rect[1]\
                    + (ROW_LOAD_TILE_DISTANCE * TILESIZE):
                sprite.kill()

    def erase_dead_sprites(self, id: str):
        for sprite in self.sprites():
            if sprite.id == id:
                sprite.kill()

    def bullet_move(self):
        for sprite in self.sprites():
            if sprite.need_to_stop:
                sprite.update()
            else:
                sprite.kill()

    def bullet_record(self, packet_to_send):
        for sprite in self.sprites():
            packet_to_send.add_header_shot_place_and_hit_hp(sprite.rect.center, 300)

    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if
                         hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)

    def enemy_check_exists(self, enemy_id, hit, place_to_go: Tuple[int, int]):  # need to change
        for sprite in self.sprites():
            if sprite.id == enemy_id:
                if hit != 'no':
                    sprite.hit = True
                    sprite.status = 'attack'
                else:
                    sprite.hit = False
                    sprite.status = 'move'
                sprite.place_to_go = place_to_go
                return True
        return False

    def other_player_update(self, player):

        for sprite in self.sprites():
            sprite: Players
            sprite.update(player)
        # attributes = dir(Players)
        # print(f"attributes: {attributes}")
        # doesnt_have = 0
        # parent_classes = Players.__bases__
        # for parent in parent_classes:
        #     print(f'parent : {dir(parent)}')
        # for sprite in self.sprites():
        #     #print(f'the object: {sprite}')
        #     for attribute in attributes:
        #         if not hasattr(sprite, attribute):
        #             #print(f'dont have this attribute: {attribute}')
        #             doesnt_have = 1
        #     if doesnt_have == 0:
        #         print('did update')
        #         sprite.update()

    def check_existines(self, player_id, pos, image, hit, place_to_go,visibale_sprites, attack_sprites):  # need to change
        for sprite in self.sprites():
            sprite: Players
            if sprite.id == player_id:

                sprite.weapon_index = 0  # the offset of the weapons
                sprite.place_to_go = place_to_go
                sprite.hit = False
                if hit != 'no':
                    sprite.hit = True
                    sprite.attacking = True
                    sprite.direction.x = 0
                    sprite.direction.y = 0
                    sprite.place_to_go = None
                    sprite.attack_time = pygame.time.get_ticks()
                    for i in list(weapon_data.keys()):
                        if hit == i:
                            break
                        sprite.weapon_index += 1
                    sprite.weapon = list(weapon_data.keys())[sprite.weapon_index]  # the weapon we are using
                    print(f'weapon {sprite.weapon}')
                    sprite.create_attack(sprite, visibale_sprites=visibale_sprites, attack_sprites=attack_sprites)
                sprite.status = image
                # sprite.rect.center = pos
                # sprite.hitbox.center = pos

                return True
        return False

    def check_if_bullet_hit_me(self, player):
        for sprite in self.sprites():
            if sprite.rect.colliderect(player.hitbox):
                player.health = - 7

    def check_if_bullet_hit_enemy(self, visibal_sprites, packet_to_send: ConnectionToServer):
        for sprite in self.sprites():
            for enemies in visibal_sprites:
                if sprite.rect.colliderect(enemies.hitbox):
                    packet_to_send.add_hit_an_enemy(enemies.id, 7)

    def delete_every_bullet(self):
        for sprite in self.sprites():
            sprite.kill()

    def item_picking(self, player, packet_to_send):
        copy_items = self.sprites().copy()
        if player.can_pick_item:
            for sprite in copy_items:
                if sprite.rect.colliderect(player.hitbox):
                    # only for the ammo:
                    if 'ammo' in player.items_on:
                        if sprite.sprite_type == 'ammo':
                            if player.items_on['ammo']['amount'] < 200:
                                player.items_on['ammo']['amount'] += 1
                                packet_to_send.add_header_inventory_update("+ ammo", 1)
                                # pick_drop, type_object, place, amount
                                packet_to_send.add_object_update('pick', 'ammo', sprite.rect.center, 1)
                                sprite.kill()
                    if sprite.sprite_type == 'exp':
                        packet_to_send.add_object_update('pick', 'exp', sprite.rect.center, 1)
                        player.exp += 20
                        sprite.kill()

                    if 'backpack' in player.items_on:
                        count = 13
                    else:
                        count = 10
                    for i in range(1, count):
                        flag = True
                        for item, item_value in player.items_on.items():
                            if item_value['ui'] == i:
                                flag = False
                                break
                        if flag:  # we will put the item in this slott
                            if sprite.sprite_type != "backpack" and sprite.sprite_type != 'boots' and sprite.sprite_type != 'ammo' and sprite.sprite_type != 'exp':
                                temp_dict = items_add_data[sprite.sprite_type].copy()
                                temp_dict['ui'] = i
                                counter = 0  # for the loop that gives the dict name in player.itmes (can't have the same names)
                                while True:
                                    if not str(counter) in player.items_on:
                                        player.items_on[str(counter)] = temp_dict.copy()
                                        temp_dict.clear()
                                        if player.items_on[str(counter)]['name'] == 'backpack':
                                            packet_to_send.add_header_inventory_update('+ backpack', 1)
                                            packet_to_send.add_object_update('pick', 'backpack', sprite.rect.center, 1)
                                        if player.items_on[str(counter)]['name'] == 'boots':
                                            packet_to_send.add_object_update('pick', 'boots', sprite.rect.center, 1)
                                            packet_to_send.add_header_inventory_update('+ boots', 1)
                                        if player.items_on[str(counter)]['name'] == 'medkit':
                                            packet_to_send.add_object_update('pick', 'med_kit', sprite.rect.center, 1)
                                            packet_to_send.add_header_inventory_update('+ med_kits', 1)
                                        if player.items_on[str(counter)]['name'] == 'bendage':
                                            packet_to_send.add_object_update('pick', 'bandage', sprite.rect.center, 1)
                                            packet_to_send.add_header_inventory_update('+ bandages', 1)
                                        sprite.kill()
                                        break
                                    counter += 1
                                break
                            elif sprite.sprite_type == 'backpack':
                                if 'backpack' in player.items_on:
                                    break
                                else:
                                    temp_dict = items_add_data[sprite.sprite_type].copy()
                                    temp_dict['ui'] = i
                                    player.items_on['backpack'] = temp_dict.copy()
                                    temp_dict.clear()
                                    packet_to_send.add_object_update('pick', 'backpack', sprite.rect.center, 1)
                                    packet_to_send.add_header_inventory_update("+ backpack", 1)
                                    sprite.kill()
                            elif sprite.sprite_type == 'boots':
                                if 'boots' in player.items_on:
                                    break
                                else:
                                    temp_dict = items_add_data[sprite.sprite_type].copy()
                                    temp_dict['ui'] = i
                                    player.items_on['boots'] = temp_dict.copy()
                                    packet_to_send.add_header_player_place_and_image(
                                        (int(player.rect.center[0]), int(player.rect.center[1])),
                                        (int(player.place_to_go[0]), int(player.place_to_go[1])),
                                        player.speed, f'{player.status},no')
                                    packet_to_send.add_object_update('pick', 'boots', sprite.rect.center, 1)
                                    packet_to_send.add_header_inventory_update("+ boots", 1)
                                    temp_dict.clear()
                                    sprite.kill()
                            elif sprite.sprite_type == 'ammo':
                                if 'ammo' in player.items_on:
                                    pass
                                    # player.items_on['ammo']['amount'] += 1
                                    # sprite.kill()
                                else:
                                    temp_dict = items_add_data[sprite.sprite_type].copy()
                                    temp_dict['ui'] = i
                                    player.items_on['ammo'] = temp_dict.copy()
                                    player.items_on['ammo']['amount'] = 1
                                    packet_to_send.add_object_update('pick', 'ammo', sprite.rect.center, 1)
                                    packet_to_send.add_header_inventory_update("+ ammo", 1)
                                    temp_dict.clear()
                                    sprite.kill()

    def weapon_picking(self, player, packet_to_send):
        copy_items = self.sprites().copy()
        if player.can_pick_item:
            for sprite in copy_items:
                if sprite.rect.colliderect(player.hitbox):
                    if sprite.sprite_type not in player.objects_on:
                        count = 6
                        for i in range(1, count):
                            flag = True
                            for item, item_value in player.objects_on.items():
                                if item_value['ui'] == i:
                                    flag = False
                                    break
                            if flag:  # we will put the item in this slott
                                temp_dict = weapon_data[sprite.sprite_type].copy()
                                temp_dict['ui'] = i
                                player.objects_on[str(sprite.sprite_type)] = temp_dict.copy()
                                packet_to_send.add_object_update('pick', str(sprite.sprite_type), sprite.rect.center, 1)
                                packet_to_send.add_header_inventory_update("+ weapons", str(sprite.sprite_type))
                                temp_dict.clear()
                                sprite.kill()
                                break
