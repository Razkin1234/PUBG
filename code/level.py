import pygame , sys
from settings import *
from tile import Tile
from player import Player
from debug import debug
from YsortCameraGroup import *
from support import *
from weapon import Weapon
from  ui import UI
from enemy import Enemy

class Level:
    def __init__(self):
        #get the display surface
        self.display_surface = pygame.display.get_surface()

        #sprite groups setup
        self.visble_sprites = YsortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        #attack sprites
        self.current_attack = None

        # sprite setup
        self.create_map()

        #user interface
        self.ui = UI()

    #here we will print every detail on the map (obstacles, players...)
    def create_map(self):
        layouts = {
            'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
            'entities': import_csv_layout('../map/map_Entities.csv')
        }
        for style,layout in layouts.items():
            for row_index , row in enumerate(layout):
                for col_index , col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE #checks the location
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x,y),self.obstacle_sprites,'invisible')
                        if style == 'entities':
                            if col == '394': #the player number on the map
                                self.player = Player(  # creating the player
                                    (x, y),
                                    [self.visble_sprites],
                                    self.obstacle_sprites,
                                    self.create_attack,
                                    self.destroy_attack,
                                    self.create_magic)
                            else:
                                if col == '390': monster_name = 'bamboo'
                                elif col == '391': monster_name = 'spirit'
                                elif col == '392': monster_name = 'raccoon'
                                else: monster_name = 'squid'
                                Enemy(monster_name,(x,y),[self.visble_sprites],self.obstacle_sprites)




    def create_attack(self):
        self.current_attack = Weapon(self.player,[self.visble_sprites])

    def create_magic(self,style,strength,cost):
        pass

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None


    def run(self):  #update and draw the game
     self.visble_sprites.custom_draw(self.player)
     self.visble_sprites.update()
     self.visble_sprites.enemy_update(self.player)
     self.ui.display(self.player)






