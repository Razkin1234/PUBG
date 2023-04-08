import logging
from typing import Tuple

import pygame

from ConnectionToServer import ConnectionToServer
from settings import *
from entity import Entity
from support import *
import YsortCameraGroup


class Enemy(Entity):
    def __init__(self, monster_name: str, enemy_id: str, pos: Tuple[int, int], groups: YsortCameraGroup,
                 obstacle_sprites: YsortCameraGroup, damage_player, hit: str, place_to_go: Tuple[int, int]):
        # general setup
        self.sprite_type = 'enemy'
        self.id = enemy_id
        self.hit = False

        # graphics setup
        self.animations = {'idle': [], 'move': [], 'attack': []}
        self.import_graphics(monster_name)
        self.status = 'move'
        if hit != 'no':
            self.hit = True
        else:
            self.hit = False


        # movement
        self.obstacle_sprites = obstacle_sprites
        # self.direction = pygame.math.Vector2()
        self.place_to_go = place_to_go
        # stats
        self.monster_name = monster_name
        if hit != 'no':
            weapon_info = weapon_data[hit]
            self.damage = weapon_info['damage']
        monster_info = monster_data[monster_name]  # the list that will give us the following information
        self.health = monster_info['health']
        self.exp = monster_info['exp']  # how much exp we will get from killing the monster
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']  # how does the monster takes a hit
        self.attack_radius = monster_info['attack_radius']  # the radius that the monster will attack us
        self.notice_radius = monster_info['notice_radius']  # the radius that the monster will aproach us
        self.attack_type = monster_info['attack_type']  # the type of the monster's attack

        # player interaction
        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = 400
        self.damage_player = damage_player
        # self.trigger_death_particles = trigger_death_particles

        # invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300
        super().__init__(groups)
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(0, -10)

    def import_graphics(self, name):
        main_path = f'../graphics/monsters/{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)  # gives me the correct monster image

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()  # the vector between the player and the enemy converts to the distance

        if distance > 0:  # if the player is not on the exact spot as the player
            direction = (player_vec - enemy_vec).normalize()  # moving the bot towords the player
        else:
            direction = pygame.math.Vector2()  # the bot won't move

        return distance, direction

    def get_status(self, player):
        distance = self.get_player_distance_direction(player)[0]

        if distance <= self.attack_radius and self.hit != 'no':  # changing the bot to attack mode
            if self.status != 'attack':
                self.frame_index = 0  # that the enemy will attack again (animation)
                self.status = 'attack'
        elif distance <= self.notice_radius:  # changing the bot to move mode
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self, player):
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            if self.rect.colliderect(player.hitbox):
                self.damage_player(self.attack_damage, self.attack_type)
        elif self.status == 'move':
            pass
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        try:
            animation = self.animations[self.status]  # the animations photo

            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                if self.status == 'attack':
                    self.can_attack = False
                self.frame_index = 0

            self.image = animation[int(self.frame_index)]
            self.rect = self.image.get_rect(center=self.hitbox.center)

            if not self.vulnerable:
                alpha = self.wave_value()
                self.image.set_alpha(alpha)
            else:
                self.image.set_alpha(255)
        except Exception as e:
            print(e)
            print('animate')

    def cooldown(self):
        try:
            current_time = pygame.time.get_ticks()
            if not self.can_attack:
                if current_time - self.attack_time >= self.attack_cooldown:
                    self.can_attack = True

            if not self.vulnerable:  # chack if the timer is equal or higher than 'self.invincibility_duration'
                if current_time - self.hit_time >= self.invincibility_duration:
                    self.vulnerable = True
        except Exception as e:
            print(e)
            print('cooldown')

    def get_damage(self, player, attack_type, packet_to_send: ConnectionToServer):
        """

        :param player: the player
        :param attack_type: if its close weapon attack or away wepon attack
        :return:nothing
        """
        if self.vulnerable:
            if attack_type == 'weapon':
                packet_to_send.add_hit_an_enemy(self.id, player.get_full_weapon_damege())
                print(packet_to_send.get_packet())
                print('sending hit an enemy')
            else:
                pass
                # away_damage
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def chack_death(self):
        """
        check if the enemy lost all of his health and kill him if so
        :return:
        """
        try:
            if self.health <= 0:
                self.kill()
               # self.trigger_death_particles(self.rect.center, self.monster_name)
        except Exception as e:
            print(e)
            print('chack_death')

    def hit_reaction(self):
        """
        move the enemy to ather direction after a hit
        :return:
        """
        try:
            if not self.vulnerable:
                self.direction *= -self.resistance
        except Exception as e:
            print(e)
            print('hit_reaction')

    def move(self, speed):  # moves the player around
        try:
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()  # making the speed good when we are gowing 2 diractions
            self.hitbox.x += self.direction.x * speed  # making the player move horizontaly
            #self.collision('horizontal')
            self.hitbox.y += self.direction.y * speed  # making the player move verticaly
            #self.collision('vertical')
            self.rect.center = self.hitbox.center
        except Exception as e:
            print(e)
            print('move')

    def collision(self, direction):  # checking for collisions
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # when we are moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # when we are moving left
                        self.hitbox.left = sprite.hitbox.right
                    self.direction.x = 0
                    self.direction.y = 0

    def stop(self):  # chack if the character in the place the player prassed on
        try:
            if self.place_to_go is not None:
                if abs(self.place_to_go[0] - self.hitbox.center[0]) < 64 and abs(
                        self.place_to_go[1] - self.hitbox.center[1]) < 64:
                    self.direction.x = 0
                    self.direction.y = 0
                    # self.status = 'down_idle'
                    self.place_to_go = None
        except Exception as e:
            print(e)
            print('stop ')

    def moving_enemy(self):
        if self.place_to_go is not None:
            try:
                pos_vector = pygame.math.Vector2(self.rect.center[0], self.rect.center[1])
                target_pos_vector = pygame.math.Vector2(self.place_to_go[0], self.place_to_go[1])
                self.direction = target_pos_vector - pos_vector
            except Exception as e:
                print(e)
                print('pygame')

    def update(self):
        self.hit_reaction()
        self.moving_enemy()
        self.move(self.speed)
        self.animate()
        self.cooldown()
        self.chack_death()
        self.stop()

    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)
