from support import *
from Connection_to_server import Connection_to_server
import pygame
from entity import Entity

class Players(Entity):

    def __init__(self, image, pos, groups, obstacle_sprites, hit, id):
        super().__init__(groups)
        # server conection
        self.id = id  # need to get id

        self.animations = None
        self.image = pygame.image.load('../graphics/ninjarobot/down/down_0.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)  # if i want to overlap itemes

        # graphics setup
        self.import_player_assets()
        self.status = image

        # movement

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

    def update(self):

        self.inputm()  # checking the input diraction
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)  # making the player move

        self.stop()

        if 'boots' in self.items_on.keys():  # checks if to be faster if we have boots in inventory
            self.speed = self.stats['speed'] + 2
        else:
            self.speed = self.stats['speed']