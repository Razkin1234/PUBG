import pygame , sys
from settings import *
from tile import Tile
from player import Player
from debug import debug
from YsortCameraGroup import *
from support import *

class Level:
    def __init__(self):
        #get the display surface
        self.display_surface = pygame.display.get_surface()

        #sprite groups setup
        self.visble_sprites = YsortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # sprite setup
        self.create_map()

    #here we will print every detail on the map (obstacles, players...)
    def create_map(self):
        layouts = {
            'boundary': import_csv_layout('graphics/map/map_FloorBlocks.csv')
        }
        for style,layout in layouts.items():
            for row_index , row in enumerate(layout):
                for col_index , col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE #checks the location
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x,y),self.obstacle_sprites,'invisible')
        #         if col == 'x':
        #             Tile((x,y),[self.visble_sprites, self.obstacle_sprites]) #prints a tile
        #         if col == 'p':
        self.player = Player((2000,1430),[self.visble_sprites], self.obstacle_sprites) #creating the player


    def run(self):  #update and draw the game
     self.visble_sprites.custom_draw(self.player)
     self.visble_sprites.update()
     debug(self.player.status)






