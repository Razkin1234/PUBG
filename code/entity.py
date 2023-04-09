import pygame
from math import sin
from debug import debug


class Entity(pygame.sprite.Sprite):
    def __init__(self, groups: pygame.sprite.Group):
        super().__init__(groups)

        self.frame_index = 0
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2()

    def move(self, speed):  # moves the player around
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()  # making the speed good when we are gowing 2 diractions
        self.hitbox.x += self.direction.x * speed  # making the player move horizontaly
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed  # making the player move verticaly
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction: str):  # checking for collisions
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # when we are moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # when we are moving left
                        self.hitbox.left = sprite.hitbox.right
                    self.direction.x = 0
                    self.direction.y = 0

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # when we are moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # when we are moving up
                        self.hitbox.top = sprite.hitbox.bottom
                    self.direction.y = 0
                    self.direction.x = 0

    @staticmethod
    def wave_value():
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        else:
            return  0
