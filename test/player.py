import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self,pos,groups,obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.image.load('graphics/remington.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)

        self.direction = pygame.math.Vector2() #default: x=0 , y=0
        self.speed = 5 #the player will move X pixels per second
        self.obstacle_sprits = obstacle_sprites

    def input(self): #checks the input from the player, for now its the arrows
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = +1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = +1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def move(self,speed): #moves the player around
        if self.direction.magnitude() != 0:
            self.direction=self.direction.normalize() #making the speed good when we are gowing 2 diractions

        self.rect.x +=self.direction.x * speed #making the player move horizontaly
        self.collision('horizontal')
        self.rect.y +=self.direction.y * speed #making the player move verticaly
        self.collision('vertical')





    def collision(self,direction): #checking for collisions
        if direction == 'horizontal':
            for sprite in self.obstacle_sprits:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.x > 0: #when we are moving right
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0:  # when we are moving left
                        self.rect.left = sprite.rect.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprits:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.y > 0: #when we are moving down
                        self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0:  # when we are moving up
                        self.rect.top = sprite.rect.bottom

    def update(self):
        self.input() #checking the input diraction
        self.move(self.speed) #making the player move