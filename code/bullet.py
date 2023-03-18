import pygame
from entity import Entity
from settings import MIDDLE_SCREEN


class Bullets(Entity):

    def __init__(self, pos, groups, obstacle_sprites, mouse_pos):
        super().__init__(groups)
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(0, -26)
        self.obstacle_sprites = obstacle_sprites
        self.bullet_timer = pygame.time.get_ticks()
        self.need_to_stop = True
        self.bullet_duration = 500

        if mouse_pos != None:
            if MIDDLE_SCREEN[0] >= mouse_pos[0]:  # chack if its behaind the middle or else it's after the middle
                self.direction.x = -(MIDDLE_SCREEN[0] - mouse_pos[0])
            else:
                self.direction.x = (mouse_pos[0] - MIDDLE_SCREEN[0])
            if MIDDLE_SCREEN[1] >= mouse_pos[1]:
                self.direction.y = -(MIDDLE_SCREEN[1] - mouse_pos[1])
            else:
                self.direction.y = (mouse_pos[1] - MIDDLE_SCREEN[1])


    def time_to_live(self):
        current_time = pygame.time.get_ticks()

        if self.need_to_stop:
            if current_time - self.bullet_timer >= self.bullet_duration:
                self.need_to_stop = False

    def move(self, speed):  # moves the player around
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()  # making the speed good when we are gowing 2 diractions
        self.hitbox.x += self.direction.x * speed  # making the player move horizontaly
        self.hitbox.y += self.direction.y * speed  # making the player move verticaly
        self.rect.center = self.hitbox.center

    def update(self):
        self.move(20)
        self.collision(self.direction)
        return self.time_to_live()

