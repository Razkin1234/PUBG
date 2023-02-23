
import pygame
from settings import *
from support import import_folder
from entity import Entity
from debug import debug
import math


class Player(Entity):
    def __init__(self,pos,groups,obstacle_sprites,create_attack,destroy_attack,create_magic):
        super().__init__(groups)
        self.animations = None
        self.image = pygame.image.load('../graphics/ninjarobot/down/down_0.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0,-26) #if i want to overlap itemes

        # graphics setup
        self.import_player_assets()
        self.status = 'down'

        # movement
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        self.place_to_go = None
        self.obstacle_sprites = obstacle_sprites

        #weapon
        self.create_attack = create_attack
        self.weapon_index = 0 #the offset of the weapons
        self.weapon = list(weapon_data.keys())[self.weapon_index] #the weapon we are using
        self.destroy_attack = destroy_attack #the function that unprinting the weapon

        self.can_switch_weapon = True #that we will switch only one weapon every time we press {
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200 #}

        self.objects_on = {'sword': {'ui': 1, 'cooldown': 100, 'damage': 15, 'graphic': '../graphics/weapons/sword/full.png'}}#max valeus = 6
        self.items_on = {} #for all of the items we will have

        #magic
        self.create_magic = create_magic
        self.magic_index = 0 #the magic index we will use
        self.magic = list(magic_data.keys())[self.magic_index] #the magic we are using
        self.can_switch_magic = True
        self.magic_switch_time = None
        self.shield_timer = None
        self.can_shield = True
        self.shield_duration = 2000
        self.run_timer = None
        self.can_run = True
        self.run_duration = 2000
        self.can_teleport = False


        #stats
        self.stats = {'health' : 100, 'energy' : 60, 'attack' : 10, 'magic': 4, 'speed': 6}  #ma health , max energy
        self.health = self.stats['health'] #our current health
        self.energy = self.stats['energy'] #our current energy
        self.exp = 100
        self.speed = self.stats['speed'] #the speed of the player

        #damage timer
        self.vulnerable =True
        self.hurt_time =None
        self.invulnerability_duration =500

        self.i_pressed = False


    def import_player_assets(self):
        character_path = '../graphics/ninjarobot/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []}
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def stop(self):  # chack if the character in the place the player prassed on
        if self.place_to_go is not None:
            if abs(self.place_to_go[0]-self.hitbox.center[0]) < 64 and abs(self.place_to_go[1]-self.hitbox.center[1]) <64:
                self.direction.x = 0
                self.direction.y = 0
                self.status = 'down'

    def inputm(self):  # checks the input from the player, mouse

        if pygame.mouse.get_pressed()[2]:
            print("aaaaa")


        if pygame.mouse.get_pressed()[0]:  # chack if the player prassed the mouse and insert the place on the screen in
            self.place_to_go = pygame.mouse.get_pos()  # "self.place_to_go"
            if self.can_teleport == True: #teleport
                self.can_teleport = False
                self.hitbox.x -= (MIDDLE_SCREEN[0] - self.place_to_go[0])
                self.hitbox.y -=(MIDDLE_SCREEN[1] - self.place_to_go[1])
                self.direction.x=0
                self.direction.y =0
            else:
                # chack where the player prassed in relation to the middle of the screen
                if MIDDLE_SCREEN[0] >= self.place_to_go[0]:  # chack if its behaind the middle or else it's after the middle
                    self.direction.x = -(MIDDLE_SCREEN[0] - self.place_to_go[0])
                    self.status = 'left'
                else:
                    self.direction.x = (self.place_to_go[0] - MIDDLE_SCREEN[0])
                    self.status = 'right'
                x_in_place_to_go = self.hitbox.center[0] + self.direction.x  # the x of 'place_to_go' in relation to map

                if MIDDLE_SCREEN[1] >= self.place_to_go[1]:
                    # chack if it's higher than the middle or else its lower than the middle
                    self.direction.y = -(MIDDLE_SCREEN[1] - self.place_to_go[1])
                else:
                    self.direction.y = (self.place_to_go[1] - MIDDLE_SCREEN[1])
                y_in_place_to_go = self.hitbox.center[1] + self.direction.y  # the y of 'place_to_go' in relation to map

                self.place_to_go = (x_in_place_to_go, y_in_place_to_go)
        #debug(self.place_to_go)
        #debug2(self.hitbox.center)
        keys = pygame.key.get_pressed()
         #attack input
        if keys[pygame.K_SPACE] and not self.attacking:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            self.create_attack()

        #magic input
        if keys[pygame.K_LCTRL] and not self.attacking:
            #the magic we will use:
            style = list(magic_data.keys())[self.magic_index]
            strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic'] #the strength of the magic + our player power
            cost = list(magic_data.values())[self.magic_index]['cost']
            self.create_magic(style,strength,cost)


        if keys[pygame.K_q] and self.can_switch_weapon:
            self.can_switch_weapon = False
            self.weapon_switch_time = pygame.time.get_ticks()

            if self.weapon_index < len(list(self.objects_on.keys())) - 1:
                self.weapon_index += 1 #new weapon
            else:
                self.weapon_index = 0
            self.weapon = list(self.objects_on.keys())[self.weapon_index]  # the weapon we are using

        #for the ui screen
        if keys[pygame.K_i]:
            self.i_pressed = True
        else: self.i_pressed =False


        if keys[pygame.K_e] and self.can_switch_magic:
            self.can_switch_magic = False
            self.magic_switch_time = pygame.time.get_ticks()

            if self.magic_index < len(list(magic_data.keys())) - 1:
                self.magic_index += 1 #new weapon
            else:
                self.magic_index = 0
            self.magic = list(magic_data.keys())[self.magic_index]  # the weapon we are using

    def input(self):  # checks the input from the player, for now it is the arrows
        keys = pygame.key.get_pressed()
        # movement input
        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN]:
            self.direction.y = +1
            self.status = 'down'
        else:
            self.direction.y = 0
        if keys[pygame.K_RIGHT]:
            self.direction.x = +1
            self.status = 'right'
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = 'left'
        else:
            self.direction.x = 0
        #attack input
        if keys[pygame.K_SPACE] and not self.attacking:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            self.create_attack()

        #magic input
        if keys[pygame.K_LCTRL] and not self.attacking:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            #the magic we will use:
            style = list(magic_data.keys())[self.magic_index]
            strength =  list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic'] #the strength of the magic + our player power
            cost = list(magic_data.values())[self.magic_index]['cost']
            self.create_magic(style,strength,cost)


        if keys[pygame.K_q] and self.can_switch_weapon:
            self.can_switch_weapon = False
            self.weapon_switch_time = pygame.time.get_ticks()

            if self.weapon_index < len(list(weapon_data.keys())) - 1:
                self.weapon_index += 1 #new weapon
            else:
                self.weapon_index = 0
            self.weapon = list(weapon_data.keys())[self.weapon_index]  # the weapon we are using



        if keys[pygame.K_e] and self.can_switch_magic:
            self.can_switch_magic = False
            self.magic_switch_time = pygame.time.get_ticks()

            if self.magic_index < len(list(magic_data.keys())) - 1:
                self.magic_index += 1 #new weapon
            else:
                self.magic_index = 0
            self.magic = list(magic_data.keys())[self.magic_index]  # the weapon we are using

    def get_status(self):

        #idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'
        if self.attacking:
            self.direction.x = 0 #the player cannot move while attacking
            self.direction.y = 0 #the player cannot move while attacking
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('idle','attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        # attacking cooldown
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()

        # weapon switching cooldown
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        #magic switching cooldown
        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True

        #hit cooldown
        if not self.vulnerable:
          if current_time - self.hurt_time >= self.invulnerability_duration:
              self.vulnerable = True

        #shiled cooldown
        if not self.can_shield:
            if current_time - self.shield_timer >= self.shield_duration:
                self.can_shield = True

        if not self.can_run:
            if current_time - self.run_timer >= self.run_duration:
                self.can_run = True
                self.speed = 5
            else:
                self.speed = 10
                print('sprrd')


    def animate(self): #shows us the animations
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        #flicker
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)



    def get_full_weapon_damege(self):
        """
        the damage the player do
        :return: base_damage + weapon_damage
        """
        base_damage = self.stats['attack']
        weapon_damage = weapon_data[self.weapon]['damage']
        return base_damage + weapon_damage


    def update(self):

        self.inputm() #checking the input diraction
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)  # making the player move
        self.stop()

