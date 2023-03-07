import pygame
from entity import Entity
from settings import MIDDLE_SCREEN
class Bullets(Entity):

    def __init__(self, pos):
        super.__init__()
        self.image = pygame.surface((50, 10))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect(center= pos)

    def update(self,mouse_pos):
        if MIDDLE_SCREEN[0] >= self.place_to_go[0]:  # chack if its behaind the middle or else it's after the middle
            self.direction.x = -(MIDDLE_SCREEN[0] - self.place_to_go[0])
        else:
            self.direction.x = (self.place_to_go[0] - MIDDLE_SCREEN[0])
        if MIDDLE_SCREEN[1] >= self.place_to_go[1]:
            self.direction.y = -(MIDDLE_SCREEN[1] - self.place_to_go[1])
        else:
            self.direction.y = (self.place_to_go[1] - MIDDLE_SCREEN[1])

        self.move(4)
        if self.rect
