import pygame

class Weapon_other(pygame.sprite.Sprite):
    def __init__(self,player_weapon,player_status,player_rect,groups):
        super().__init__(groups)
        direction = player_status.split('_')[0]
        self.sprite_type ='weapon'
        #graphics
        full_path = f'../graphics/weapons/{player_weapon}/{direction}.png'
        self.image = pygame.image.load(full_path).convert_alpha()

        #placement
        if direction == 'right':
            self.rect = self.image.get_rect(midleft = player_rect.midright + pygame.math.Vector2(0,5))#where the weapon sprite will be
        elif direction == 'left':
            self.rect = self.image.get_rect(midright = player_rect.midleft + pygame.math.Vector2(0,5))
        elif direction =='down':
            self.rect = self.image.get_rect(midtop = player_rect.midbottom + pygame.math.Vector2(-10,0))
        else: #for up status
            self.rect = self.image.get_rect(midbottom = player_rect.midtop + pygame.math.Vector2(-18,0))
