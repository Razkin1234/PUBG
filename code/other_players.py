from support import *
from Connection_to_server import Connection_to_server
import pygame
from entity import Entity
from settings import *
class Players(Entity):

    def __init__(self, image, pos, groups, obstacle_sprites, hit, id, damage_player):
        super().__init__(groups)
        # server conection
        self.id = id  # need to get id
        self.animations = None
        self.image = pygame.image.load('../graphics/ninjarobot/down/down_0.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)  # if i want to overlap itemes
        self.hit = hit
        # graphics setup
        self.import_player_assets()
        self.damage_player = damage_player
        self.obstacle_sprites = obstacle_sprites        # movement
        if hit != 'no':
            self.weapon = hit
            self.status = image
        # stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 6}  # ma health , max energy
        self.health = self.stats['health'] - 60  # our current health
        self.energy = self.stats['energy']  # our current energy
        self.exp = 100
        self.speed = self.stats['speed']  # the speed of the player

        # damage timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

        # movement
        self.attacking = False
        self.attack_cooldown = 50
        self.attack_time = None
        self.place_to_go = None
        # ui button cooldown + is pressed
        self.can_press_i = True  # that we will switch only one weapon every time we press {
        self.i_pressed_time = None
        self.i_pressed_cooldown = 100  # }
        self.i_pressed = False

        # chat stuff:
        self.chat_input = False

    def import_player_assets(self):
        character_path = '../graphics/ninjarobot/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []}
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)


    def get_status(self):

        # idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'
        if self.attacking:
            self.direction.x = 0  # the player cannot move while attacking
            self.direction.y = 0  # the player cannot move while attacking
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('idle', 'attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def actions(self):
        if self.hit != 'no':
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_damage, self.hit)

    def animate(self):  # shows us the animations
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # flicker
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        # attacking cooldown
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False

    def update(self, player):
        self.cooldowns()
        self.actions(player)
        self.get_status()
        self.animate()
