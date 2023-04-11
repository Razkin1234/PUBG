import os
import sys

import pygame


class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        try:
            super().__init__(groups)
            direction = player.status.split('_')[0]
            self.sprite_type = 'weapon'
            # graphics
            full_path = f'../graphics/weapons/{player.weapon}/{direction}.png'
            self.image = pygame.image.load(full_path).convert_alpha()
            self.attack_cooldown = 50
            self.attack_time = pygame.time.get_ticks()
            # placement
            if direction == 'right':
                self.rect = self.image.get_rect(
                    midleft=player.rect.midright + pygame.math.Vector2(0, 5))  # where the weapon sprite will be
            elif direction == 'left':
                self.rect = self.image.get_rect(midright=player.rect.midleft + pygame.math.Vector2(0, 5))
            elif direction == 'down':
                self.rect = self.image.get_rect(midtop=player.rect.midbottom + pygame.math.Vector2(-10, 0))
            else:  # for up status
                self.rect = self.image.get_rect(midbottom=player.rect.midtop + pygame.math.Vector2(-18, 0))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print("weapon" + e)
