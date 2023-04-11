import pygame
from entity import Entity



class OtherBullets(Entity):

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

        if mouse_pos is not None and self.rect.center is not None:
            pos_vector = pygame.math.Vector2(self.rect.center[0], self.rect.center[1])
            target_pos_vector = pygame.math.Vector2(mouse_pos[0], mouse_pos[1])
            self.direction = target_pos_vector - pos_vector

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

