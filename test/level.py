import pygame , sys
from settings import *
from tile import Tile
from player import Player
from debug import debug
from YsortCameraGroup import *

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
        for row_index , row in enumerate(WORLD_MAP): #creating the visual map
            for col_index , col in enumerate(row):
                x = col_index * TILESIZE #checks the location
                y = row_index * TILESIZE
                if col == 'x':
                    Tile((x,y),[self.visble_sprites, self.obstacle_sprites]) #prints a tile
                if col == 'p':
                    self.player = Player((x,y),[self.visble_sprites], self.obstacle_sprites) #creating the player


    def run(self):  #update and draw the game
     self.visble_sprites.custom_draw(self.player)
     self.visble_sprites.update()






