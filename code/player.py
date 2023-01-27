import pygame
from settings import  *
from support import import_folder


class Player(pygame.sprite.Sprite):
    def __init__(self,pos,groups,obstacle_sprites,create_attack,destroy_attack):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0,-26) #if i want to overlap itemes

        #graphics setup
        self.import_player_assets()
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15

        # movement
        self.direction = pygame.math.Vector2() #default: x=0 , y=0
        self.speed = 5 #the player will move X pixels per second
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        self.obstacle_sprits = obstacle_sprites

        #weapon
        self.create_attack = create_attack
        self.weapon_index = 0 #the offset of the weapons
        self.weapon = list(weapon_data.keys())[self.weapon_index] #the weapon we are using
        self.destroy_attack = destroy_attack #the function that unprinting the weapon

        self.can_switch_weapon = True #that we will switch only one weapon every time we press {
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200 #}


    def import_player_assets(self):
        character_path = '../graphics/ninjarobot/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []}
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def input(self): #checks the input from the player, for now its the arrows
        keys = pygame.key.get_pressed()
        #movement input
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
        if keys[pygame.K_q] and self.can_switch_weapon:
            self.can_switch_weapon = False
            self.weapon_switch_time = pygame.time.get_ticks()

            if self.weapon_index < len(list(weapon_data.keys())) - 1:
                self.weapon_index += 1 #new weapon
            else:
                self.weapon_index = 0
            self.weapon = list(weapon_data.keys())[self.weapon_index]  # the weapon we are using

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

    def move(self,speed): #moves the player around
        if self.direction.magnitude() != 0:
            self.direction=self.direction.normalize() #making the speed good when we are gowing 2 diractions

        self.hitbox.x +=self.direction.x * speed #making the player move horizontaly
        self.collision('horizontal')
        self.hitbox.y +=self.direction.y * speed #making the player move verticaly
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self,direction): #checking for collisions
        if direction == 'horizontal':
            for sprite in self.obstacle_sprits:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: #when we are moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # when we are moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprits:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: #when we are moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # when we are moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attacking: #for the attcking
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()
        if not  self.can_switch_weapon: #for the weapon switching
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True




    def animate(self): #shows us the animations
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)


    def update(self):
        self.input() #checking the input diraction
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed) #making the player move