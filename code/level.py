import time
import pygame, sys
from settings import *
from tile import Tile
from debug import debug
from YsortCameraGroup import *
from support import *
from weapon import Weapon
from weapon_item import Weapon_item
from ui import UI
from enemy import Enemy
from player import Player
from typing import Dict
from particles import AnimationPlayer
from magic import MagicPlayer
import socket
from Incoming_packets import Incoming_packets
from item import Item
import threading

from Connection_to_server import Connection_to_server

"""""
    לעשות שכשאני מקבל שחקן אחר זה לא יצור אותו מחדש ופשות יעדכן את המיקום שלו.
"""""

class Level:
    def __init__(self, place_to_start):
        # get the display surface
        self.display_surface = pygame.display.get_surface()
        self.camera = pygame.math.Vector2()
        self.place_to_start = place_to_start
        # server_things
        self.player_id = ''

        # sprite groups setup
        self.visble_sprites = YsortCameraGroup()
        self.obstacle_sprites = YsortCameraGroup()
        self.floor_sprites = YsortCameraGroup()
        self.bullet_group = YsortCameraGroup()
        self.other_bullet_group = YsortCameraGroup()
        self.item_sprites = YsortCameraGroup()
        self.weapon_sprites = YsortCameraGroup()

        self.finished_first_object_event = threading.Event()

        self.other_players = YsortCameraGroup()
        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        self.can_update_floor = False
        self.update_floor_cooldown = 1000
        self.floor_update_time = 0
        self.player_first_location = (22 * TILESIZE, 33 * TILESIZE)
        self.layout: dict[str: list[list[int]]] = {
            'floor': import_csv_layout('../map/map_Floor.csv'),
            'boundary': import_csv_layout('../map/map_FloorBlocks.csv')
            # ,'entities': import_csv_layout('../map/map_Entities.csv')
        }
        self.graphics: dict[str: dict[int: pygame.Surface]] = {
            'floor': import_folder('../graphics/tilessyber')
        }

        # particals
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

        # sprite setup
        self.create_map()

        # floor updating
        self.player_move = [0, 0]
        self.player_prev_location = self.player.rect[0:2]

        # user interface
        self.ui = UI(self.player.objects_on, self.player.items_on, self.item_sprites, self.weapon_sprites)

        self.item = Item

    def handeler_of_incoming_packets(self, visibale_sprites, player, obstecal_sprits, item_sprites, id):
         while not shut_down_event.is_set():
            if len(packets_to_handle_queue) > 0:
                packet = packets_to_handle_queue.popleft()
                self.player_id = id
                if packet.rotshild_filter():
                    lines = packet.get_packet().split('\r\n')
                    while '' in lines:
                        lines.remove('')
                    for line in lines:
                        line_parts = line.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                        # --------------
                        # in this header clients should check the moved_player_id so they wont print their own movement twice.
                        if line_parts[0] == 'player_place:':
                            # looking for image header
                            for l in lines:
                                l_parts = l.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                                if l_parts[0] == 'image:':
                                    # looking for moved player id
                                    for l2 in lines:
                                        l2_parts = l2.split()
                                        if l2_parts[0] == 'moved_player_id:':
                                            if packet.get_id() != l2_parts[1]:
                                                where_to_go = line_parts[1].split(',')
                                                packet.handle_player_place(where_to_go[0], where_to_go[1], where_to_go[2], l2_parts[1], l_parts[1],
                                                                           player.rect.center,
                                                                           self.other_players, obstecal_sprits, self.damage_player)

                                            break
                                    break
                                    # here calling the function

                        # --------------

                        # --------------
                        # in this header clients should check the shooter_id so they wont print their own shot twice (if don't hit)
                        elif line_parts[0] == 'shot_place:':
                            # looking for the hit_hp header
                            for l in lines:
                                l_parts = l.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                                if l_parts[0] == 'shooter_id:':
                                    if l_parts[1] != packet.get_id():
                                        packet.handle_shot_place(line_parts[1], self.other_bullet_group,
                                                                 self.obstacle_sprites, self.player.rect.center)
                                    break
                        # --------------


                        # --------------
                        elif line_parts[0] == 'dead:':
                            packet.handle_dead(int(line_parts[1]), visibale_sprites)
                        # --------------

                        # --------------
                        elif line_parts[0] == 'first_inventory:':
                            packet.handle_first_inventory(line_parts[1], player)
                        # --------------

                        # --------------
                        # clients will get chats of themselves too.
                        # so they should print only what comes from the server and don't print their own messages just after sending it.
                        elif line_parts[0] == 'chat:':
                            for l in lines:
                                l_parts = l.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                                if l_parts[0] == 'user_name:':
                                    message = packet.handle_chat(line_parts[1],
                                                                 l_parts[1])  # getting in answer the message to print
                                    break
                        elif line_parts[0] == 'server_shutdown:':
                            shut_down_event.set()
                            return

                        # --------------

                        # --------------
                        elif line_parts[0] == 'disconnect:':
                            packet.handle_disconnect(int(line_parts[1]), visibale_sprites)

                        # --------------
                        # --------------
                        elif line_parts[0] == 'first_objects_position:':
                            self.finished_first_object_event.clear()
                            packet.handle_first_objects_position(line_parts[1], item_sprites, self.weapon_sprites)
                            self.finished_first_object_event.set()
                        # --------------
                        # --------------
                        elif line_parts[0] == 'object_update:':
                            l_parts = line_parts[1].split('?')
                            if l_parts[0] != player.id:
                                packet.handle_object_update(l_parts[1], item_sprites, self.weapon_sprites)
                        # --------------

                        # --------------
                        elif line_parts[0] == 'dead_enemy:':
                            packet.handle_dead_enemy(line_parts[1])
                        # --------------

                        # --------------
                        elif line_parts[0] == 'enemy_update:':
                            packet.handle_enemy_player_place_type_hit(line_parts[1])

            time.sleep(0.1)

    def get_place_to_start(self, place_to_start):
        self.place_to_start = place_to_start

    def cooldown(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.floor_update_time >= self.update_floor_cooldown:
            self.floor_update_time = pygame.time.get_ticks()
            self.floor_update()

    def floor_update(self):

        player_tile: pygame.math.Vector2 = pygame.math.Vector2(int(self.player.rect.x / TILESIZE),
                                                               int(self.player.rect.y / TILESIZE))
        self.player_move[0] = (player_tile.x - self.player_prev_location[0] // TILESIZE)
        self.player_move[1] = (player_tile.y - self.player_prev_location[1] // TILESIZE)

        if self.player_move[1] != 0:
            if self.player_move[1] > 0:
                row_index_add = int(player_tile.y + (ROW_LOAD_TILE_DISTANCE - 1))
                row_index_remove = int(player_tile.y - (ROW_LOAD_TILE_DISTANCE))
            else:
                row_index_add = int(player_tile.y - (ROW_LOAD_TILE_DISTANCE - 1))
                row_index_remove = int(player_tile.y + (ROW_LOAD_TILE_DISTANCE))
            self.floor_sprites.remove_sprites_in_rect((row_index_remove * TILESIZE), 1)
            self.obstacle_sprites.remove_sprites_in_rect((row_index_remove * TILESIZE), 1)

            for style_index, (style, layout) in enumerate(self.layout.items()):
                self.floor_sprites.remove_sprites_in_rect(row_index_remove * TILESIZE, 1)
                self.obstacle_sprites.remove_sprites_in_rect(row_index_remove * TILESIZE, 1)
                if 0 <= row_index_add < ROW_TILES:
                    row_add = layout[row_index_add]
                    for col_index in range(int(player_tile.x - COL_LOAD_TILE_DISTANCE),
                                           int(player_tile.x + COL_LOAD_TILE_DISTANCE)):
                        if 0 <= col_index < COL_TILES:
                            col = row_add[col_index]
                            if col != '-1':  # -1 in csv means no tile, don't need to recreate the tile if it already exists
                                x: int = col_index * TILESIZE
                                y: int = row_index_add * TILESIZE
                                self.floor_sprites.remove_sprites_in_rect(row_index_remove * TILESIZE, 1)
                                self.obstacle_sprites.remove_sprites_in_rect(row_index_remove * TILESIZE, 1)

                                if style == 'floor':
                                    tile_path = f'../graphics/tilessyber/{col}.png'
                                    image_surf = pygame.image.load(tile_path).convert_alpha()
                                    Tile((x, y), [self.floor_sprites], 'floor', image_surf)
                                elif style == 'boundary':
                                    Tile((x, y), [self.obstacle_sprites], 'barrier')

        if self.player_move[0] != 0:
            if self.player_move[0] > 0:
                col_index_add = int(player_tile.x + (COL_LOAD_TILE_DISTANCE - 1))
                col_index_remove = int(player_tile.x - (COL_LOAD_TILE_DISTANCE))
            else:
                col_index_add = int(player_tile.x - (COL_LOAD_TILE_DISTANCE - 1))
                col_index_remove = int(player_tile.x + (COL_LOAD_TILE_DISTANCE))
            self.floor_sprites.remove_sprites_in_rect((col_index_remove * TILESIZE), 0)
            self.obstacle_sprites.remove_sprites_in_rect((col_index_remove * TILESIZE), 0)

            for style_index, (style, layout) in enumerate(self.layout.items()):
                for row_index in range(int(player_tile.y - ROW_LOAD_TILE_DISTANCE),
                                       int(player_tile.y + ROW_LOAD_TILE_DISTANCE)):
                    if 0 <= row_index < ROW_TILES:
                        row = layout[row_index]
                        if 0 <= col_index_add < COL_TILES:
                            col = row[col_index_add]
                            if col != '-1':  # -1 in csv means no tile, don't need to recreate the tile if it already exists
                                x: int = col_index_add * TILESIZE
                                y: int = row_index * TILESIZE

                                if style == 'floor':
                                    tile_path = f'../graphics/tilessyber/{col}.png'
                                    image_surf = pygame.image.load(tile_path).convert_alpha()
                                    Tile((x, y), [self.floor_sprites], 'floor', image_surf)
                                elif style == 'boundary':
                                    Tile((x, y), [self.obstacle_sprites], 'barrier')

        self.player_prev_location = self.player.rect[0:2]

    # here we will print every detail on the map (obstacles, players...)
    def create_map(self):
        """
        Place movable tiles on the map
        :return: None
        """

        # Create player with starting position
        self.player = Player(self.place_to_start, self.visble_sprites,
                             self.obstacle_sprites, self.create_attack, self.destroy_attack, self.create_magic,
                             self.bullet_group, self.player_id)
        self.player_prev_location = self.player.rect[0:2]
        # Center camera
        self.camera.x = self.player.rect.centerx
        self.camera.y = self.player.rect.centery

        # printing the area around the player:
        player_tile: pygame.math.Vector2 = pygame.math.Vector2(int(self.player.rect.x / TILESIZE),
                                                               int(self.player.rect.y / TILESIZE))
        for style_index, (style, layout) in enumerate(self.layout.items()):
            for row_index in range(int(player_tile.y - ROW_LOAD_TILE_DISTANCE),
                                   int(player_tile.y + ROW_LOAD_TILE_DISTANCE)):
                if 0 <= row_index < ROW_TILES:
                    row = layout[row_index]
                    for col_index in range(int(player_tile.x - COL_LOAD_TILE_DISTANCE),
                                           int(player_tile.x + COL_LOAD_TILE_DISTANCE)):
                        if 0 <= col_index < COL_TILES:
                            col = row[col_index]
                            if col != '-1':  # -1 in csv means no tile, don't need to recreate the tile if it already exists
                                x: int = col_index * TILESIZE
                                y: int = row_index * TILESIZE

                                if style == 'floor':
                                    tile_path = f'../graphics/tilessyber/{col}.png'
                                    image_surf = pygame.image.load(tile_path).convert_alpha()
                                    Tile((x, y), [self.floor_sprites], 'floor', image_surf)
                                elif style == 'boundary':
                                    Tile((x, y), [self.obstacle_sprites], 'barrier')

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visble_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost, packet_to_send):
        """

        :param packet_to_send:
        :param style:
        :param strength:
        :param cost:
        :return:
        """
        if style == 'heal':  # need to replace with 'teleport'
            self.magic_player.teleport(self.player, cost)
        if style == 'flame':  # highspeed

            self.magic_player.highspeed(self.player, cost, packet_to_send)
        if style == 'shield':  # shield
            self.magic_player.shield(self.player, cost, [self.visble_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def damage_player(self, amount, attack_type):
        """
        if the enemy hits the player his health goes down
        and show particals on screen
        :param amount:
        :param attack_type:
        :return:
        """
        if self.player.vulnerable and self.player.can_shield:  # chack if the player has shield on
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visble_sprites])

    def player_attack_logic(self, packet_to_send):
        """
        chack if the player hits an enemy and delete it for the screen
        :return: nothing
        """
        if self.attack_sprites:  # chack if there is somting in attack_sprites
            for attack_sprite in self.attack_sprites:  # go over all the things in attack_sprites and chack if it
                # hit somting in attackable_sprite in delete it or give it demage
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'enemy':
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type, packet_to_send)

    def trigger_death_particles(self, pos, particles_type):
        """
        if the enemy dies it show on the screen animation
        :param pos:
        :param particles_type:
        :return:
        """
        self.animation_player.create_particles(particles_type, pos, [self.visble_sprites])

    def run(self,packet_to_send, id):  # update and draw the game
        self.player_id = id

        self.cooldown()
        self.camera.x = self.player.rect.centerx  # updating the camera location
        self.camera.y = self.player.rect.centery

        # for cleaning the exeptions of the tiles that have not bean earased
        # self.visble_sprites.earase_non_relevant_sprites(self.player)
        self.obstacle_sprites.earase_non_relevant_sprites(self.player)

        self.floor_update()
        self.floor_sprites.custom_draw(self.camera)
        self.floor_sprites.update()

        self.finished_first_object_event.wait()
        self.item_sprites.custom_draw(self.camera)
        self.weapon_sprites.custom_draw(self.camera)

        self.item_sprites.item_picking(self.player, packet_to_send)
        self.weapon_sprites.weapon_picking(self.player, packet_to_send)

        self.bullet_group.custom_draw(self.camera)
        self.bullet_group.bullet_move()

        self.other_bullet_group.check_if_bullet_hit_me(self.player)

        self.other_players.update()
        self.other_players.custom_draw(self.camera)
        self.visble_sprites.custom_draw(self.camera)
        self.visble_sprites.update()
        self.player.update1(packet_to_send)
        # self.visble_sprites.enemy_update(self.player)
        self.player_attack_logic(packet_to_send)
        self.ui.display(self.player)
        if self.player.i_pressed:
            self.ui.ui_screen(self.player, packet_to_send)

        if self.player.attack_for_moment:
            image = self.player.weapon
        else:
            image = "no"
        #packet_to_send.add_header_player_place_and_image(self.player.rect.center, self.player.place_to_go, f'{self.player.status},{image}')
        self.bullet_group.bullet_record(packet_to_send)

        # packet_to_send.add_object_update(self, pick_drop, type_object, place, amount, how_many_dropped_picked)
        if self.player.health == 0:
            packet_to_send.add_header_dead(self.player.id)
            packet_to_send.for_dead_object_update(self.player)
        # print(packet_to_send.get_packet())
        return packet_to_send
