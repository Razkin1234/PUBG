import pygame, sys
from settings import *
from tile import Tile
from player import Player
from debug import debug
from YsortCameraGroup import *
from support import *
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer


class Level:
    def __init__(self):
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups setup
        self.visble_sprites = YsortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # sprite setup
        self.create_map()

        # user interface
        self.ui = UI()

        # particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

    # here we will print every detail on the map (obstacles, players...)
    def create_map(self):
        layouts = {
            'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
            'entities': import_csv_layout('../map/map_Entities.csv')
        }
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE  # checks the location
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x, y), self.obstacle_sprites, 'invisible')
                        if style == 'entities':
                            if col == '394':  # the player number on the map
                                self.player = Player(  # creating the player
                                    (x, y),
                                    [self.visble_sprites],
                                    self.obstacle_sprites,
                                    self.create_attack,
                                    self.destroy_attack,
                                    self.create_magic)
                            else:
                                if col == '390':
                                    monster_name = 'bamboo'
                                elif col == '391':
                                    monster_name = 'spirit'
                                elif col == '392':
                                    monster_name = 'raccoon'
                                else:
                                    monster_name = 'squid'
                                Enemy(
                                    monster_name,
                                    (x, y),
                                    [self.visble_sprites, self.attackable_sprites],
                                    self.obstacle_sprites, self.damage_player, self.trigger_death_particles)

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visble_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        """

        :param style:
        :param strength:
        :param cost:
        :return:
        """
        if style == 'heal':  # need to replace with 'shield'
            self.magic_player.heal(self.player,strength,cost,[self.visble_sprites])
        if style == 'flame':  # the shots
            pass
        if style == 'shield':
            self.magic_player.shield(self.player, strength, cost, [self.visble_sprites])
            self.player.shield_timer = pygame.time.get_ticks()

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
        if self.player.vulnerable and self.player.can_shield:
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

    def run(self):  # update and draw the game
        self.visble_sprites.custom_draw(self.player)
        self.visble_sprites.update()
        self.visble_sprites.enemy_update(self.player)
        self.player_attack_logic()
        self.ui.display(self.player)
