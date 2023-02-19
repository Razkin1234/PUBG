
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


class Level:
    def __init__(self):
        # get the display surface
        self.display_surface = pygame.display.get_surface()
        self.camera = pygame.math.Vector2()

        # sprite groups setup
        self.visble_sprites = YsortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.floor_sprites = YsortCameraGroup()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # sprite setup
        self.create_map()

        # user interface
        self.ui = UI()

        #floor updating
        self.can_update_floor = False
        self.update_floor_cooldown = 1000
        self.floor_update_time = 0
        self.player_first_location = (22*TILESIZE,33*TILESIZE)
        self.layout :dict[str: list[list[int]]]={
            'floor': import_csv_layout('../map/map_Floor.csv'),
            'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
            'entities': import_csv_layout('../map/map_Entities.csv')
        }
        self.graphics: dict[str: dict[int: pygame.Surface]] = {
            'floor': import_folder('../graphics/tilessyber')
        }



    def cooldown(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.floor_update_time >= self.update_floor_cooldown:
            self.floor_update_time = pygame.time.get_ticks()
            self.floor_update()
    def floor_update(self):
        for style_index, (style, layout) in enumerate(self.layout.items()):
            for row_index in range(int(self.player.rect[1] - ROW_LOAD_TILE_DISTANCE),
                                   int(self.player.rect[1] + ROW_LOAD_TILE_DISTANCE)):
                if 0 <= row_index < ROW_TILES:
                    row = layout[row_index]
                    for col_index in range(int(self.player.rect[0] - COL_LOAD_TILE_DISTANCE),
                                           int(self.player.rect[0] + COL_LOAD_TILE_DISTANCE)):
                        if 0 <= col_index < COL_TILES:
                            col = row[col_index]
                            if col != '-1':  # -1 in csv means no tile, don't need to recreate the tile if it already exists
                                x: int = col_index * TILESIZE
                                y: int = row_index * TILESIZE

                                if style == 'floor':
                                    surface: pygame.Surface = f''
                                    Tile((x, y), [self.visible_sprites], 'floor')
                                elif style == 'boundary':
                                    Tile((x, y), [self.obstacle_sprites], 'barrier')

    # here we will print every detail on the map (obstacles, players...)
    def create_map(self):
        """
        Place movable tiles on the map
        :return: None
        """
        # Create player with starting position
        self.player = Player((22*64, 33*64), self.visble_sprites,
                             self.obstacle_sprites,self.create_attack,self.destroy_attack,self.create_magic)

        # Center camera
        self.camera.x = self.player.rect.centerx
        self.camera.y = self.player.rect.centery

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visble_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        pass

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

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

    def run(self):  # update and draw the game
        #self.cooldown()
        self.camera.x = self.player.rect.centerx#updating the camera location
        self.camera.y = self.player.rect.centery

        self.floor_update()
        self.floor_sprites.custom_draw(self.camera)
        self.floor_sprites.update()
        self.visble_sprites.custom_draw(self.camera)
        self.visble_sprites.update()
        self.visble_sprites.enemy_update(self.player)
        self.player_attack_logic()
        self.ui.display(self.player)
        debug(get_player_loc(self.player.rect[0:2]))


