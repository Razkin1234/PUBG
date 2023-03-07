import pygame, sys
from settings import *
from tile import Tile
from debug import debug
from YsortCameraGroup import *
from support import *
from weapon import Weapon
from ui import UI
from enemy import Enemy
from player import Player
from typing import Dict
from particles import AnimationPlayer
from magic import MagicPlayer
import socket
from Incoming_packets import Incoming_packets



"""""
    לעשות שכשאני מקבל שחקן אחר זה לא יצור אותו מחדש ופשות יעדכן את המיקום שלו.
"""""
def handeler_of_incoming_packets(packet,visibale_sprites,player):
    lines = packet.get_packet.split('\r\n')
    lines.remove('')
    for line in lines:
        line_parts = line.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]

        if line_parts[0] == 'register_status:':
            answer = packet.handle_register_status(line_parts[1])
            if not answer[0]:
                pass
            # here print to the screen like what is in the value answer[1]
            else:
                pass
        # go back to opening page
        # --------------

        # --------------
        # in this header clients should check the moved_player_id so they wont print their own movement twice.
        elif line_parts[0] == 'player_place:':
            # looking for image header
            for l in lines:
                l_parts = l.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                if l_parts[0] == 'image:':
                    # looking for moved player id
                    for l2 in lines:
                        l2_parts = l2.split()
                        if l2_parts[0] == 'moved_player_id:':
                            if packet.get_id != '# add player id':
                                packet.handle_player_place(line_parts[1], l2_parts[1], l_parts[1], player.rect,
                                                           visibale_sprites)

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
                    if l_parts[1] != '# id of client':
                        packet.handle_shot_place(line_parts[1])
                    break
        # --------------

        # --------------
        elif line_parts[0] == 'dead:':
            packet.handle_dead(line_parts[1])
        # --------------

        # --------------
        elif line_parts[0] == 'first_inventory:':
            packet.handle_first_inventory(line_parts[1],player)
        # --------------

        # --------------
        # clients will get chats of themselves too.
        # so they should print only what comes from the server and don't print their own messages just after sending it.
        elif line_parts[0] == 'chat:':
            for l in lines:
                l_parts = l.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                if l_parts[0] == 'user_name:':
                    message = packet.handle_chat(line_parts[1], l_parts[1])  # getting in answer the message to print
                    break
        elif line_parts[0] == 'server_shutdown:':
            pass


class Level:
    def __init__(self):
        # get the display surface
        self.display_surface = pygame.display.get_surface()
        self.camera = pygame.math.Vector2()

        # sprite groups setup
        self.visble_sprites = YsortCameraGroup()
        self.obstacle_sprites = YsortCameraGroup()
        self.floor_sprites = YsortCameraGroup()
        self.bullet_group = YsortCameraGroup()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        self.can_update_floor = False
        self.update_floor_cooldown = 1000
        self.floor_update_time = 0
        self.player_first_location = (22*TILESIZE,33*TILESIZE)
        self.layout :dict[str: list[list[int]]]={
            'floor': import_csv_layout('../map/map_Floor2.csv'),
            'boundary': import_csv_layout('../map/map_FloorBlocks2.csv')
            #,'entities': import_csv_layout('../map/map_Entities.csv')
        }
        self.graphics: dict[str: dict[int: pygame.Surface]] = {
            'floor': import_folder('../graphics/tilessyber')
        }

        #particals
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)


        # sprite setup
        self.create_map()

        # floor updating
        self.player_move = [0, 0]
        self.player_prev_location = self.player.rect[0:2]

        # user interface
        self.ui = UI(self.player.objects_on,self.player.items_on)




    def cooldown(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.floor_update_time >= self.update_floor_cooldown:
            self.floor_update_time = pygame.time.get_ticks()
            self.floor_update()

    def floor_update(self):

        player_tile: pygame.math.Vector2 = pygame.math.Vector2(int(self.player.rect.x / TILESIZE),
                                                               int(self.player.rect.y / TILESIZE))
        self.player_move[0] = (player_tile.x - self.player_prev_location[0]//TILESIZE)
        self.player_move[1] = (player_tile.y - self.player_prev_location[1]//TILESIZE)

        if self.player_move[1] !=0:
            if self.player_move[1] > 0:
                row_index_add = int(player_tile.y + (ROW_LOAD_TILE_DISTANCE-1))
                row_index_remove = int(player_tile.y - (ROW_LOAD_TILE_DISTANCE))
            else:
                row_index_add = int(player_tile.y - (ROW_LOAD_TILE_DISTANCE-1))
                row_index_remove = int(player_tile.y + (ROW_LOAD_TILE_DISTANCE))
            self.floor_sprites.remove_sprites_in_rect((row_index_remove * TILESIZE), 1)
            self.obstacle_sprites.remove_sprites_in_rect((row_index_remove * TILESIZE) , 1)

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
                                self.floor_sprites.remove_sprites_in_rect(row_index_remove*TILESIZE, 1)
                                self.obstacle_sprites.remove_sprites_in_rect(row_index_remove*TILESIZE, 1)

                                if style == 'floor':
                                    tile_path = f'../graphics/tilessyber/{col}.png'
                                    image_surf = pygame.image.load(tile_path).convert_alpha()
                                    Tile((x, y), [self.floor_sprites], 'floor', image_surf)
                                elif style == 'boundary':
                                    Tile((x, y), [self.obstacle_sprites], 'barrier')


        if self.player_move[0] !=0:
            if self.player_move[0] > 0:
                col_index_add = int(player_tile.x + (COL_LOAD_TILE_DISTANCE-1))
                col_index_remove = int(player_tile.x - (COL_LOAD_TILE_DISTANCE ))
            else:
                col_index_add = int(player_tile.x - (COL_LOAD_TILE_DISTANCE-1))
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
        self.player = Player((1000, 1000), self.visble_sprites,
                             self.obstacle_sprites,self.create_attack,self.destroy_attack,self.create_magic)
        self.player_prev_location = self.player.rect[0:2]
        # Center camera
        self.camera.x = self.player.rect.centerx
        self.camera.y = self.player.rect.centery



        #printing the area around the player:
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

    def create_magic(self, style, strength, cost):
        """

        :param style:
        :param strength:
        :param cost:
        :return:
        """
        if style == 'heal':  # need to replace with 'teleport'
            self.magic_player.teleport(self.player,cost)
        if style == 'flame':  #highspeed
            self.magic_player.highspeed(self.player,cost)
        if style == 'shield': #shield
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
        if self.player.vulnerable and self.player.can_shield:# chack if the player has shield on
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visble_sprites])

    def player_attack_logic(self):
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
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def trigger_death_particles(self, pos, particles_type):
        """
        if the enemy dies it show on the screen animation
        :param pos:
        :param particles_type:
        :return:
        """
        self.animation_player.create_particles(particles_type, pos, [self.visble_sprites])

    def run(self,server_ip,user_name,passward,packet):  # update and draw the game

       # if packet.rotshild_filter():
       #     handeler_of_incoming_packets(packet, self.visble_sprites, self.player)
       # # ------------------- Socket
       # my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       # # -------------------
       #
       # my_socket.connect((server_ip, SERVER_PORT))
       # server_reply, addres = my_socket.recv(1024)
       # packet = Incoming_packets(server_reply,addres,server_ip,None)
       


       #self.cooldown()
        self.camera.x = self.player.rect.centerx#updating the camera location
        self.camera.y = self.player.rect.centery

        #for cleaning the exeptions of the tiles that have not bean earased
        self.visble_sprites.earase_non_relevant_sprites(self.player)
        self.obstacle_sprites.earase_non_relevant_sprites(self.player)


        self.floor_update()
        self.floor_sprites.custom_draw(self.camera)
        self.floor_sprites.update()


        self.visble_sprites.custom_draw(self.camera)
        self.visble_sprites.update()
        self.visble_sprites.enemy_update(self.player)
        self.player_attack_logic()
        self.ui.display(self.player)

        if self.player.i_pressed:
            self.ui.ui_screen(self.player)