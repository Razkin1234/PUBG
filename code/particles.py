import pygame
from support import import_folder
from random import choice


class AnimationPlayer:
    def __init__(self):
        self.frames = {
            # magic
            'flame': import_folder('../graphics/particles/flame/frames'),
            'aura': import_folder('../graphics/particles/aura'),
            'heal': import_folder('../graphics/particles/heal/frames'),

            # attacks
            'claw': import_folder('../graphics/particles/claw'),
            'slash': import_folder('../graphics/particles/slash'),
            'sparkle': import_folder('../graphics/particles/sparkle'),
            'leaf_attack': import_folder('../graphics/particles/leaf_attack'),
            'thunder': import_folder('../graphics/particles/thunder'),

            # monster deaths
            'squid': import_folder('../graphics/particles/smoke_orange'),
            'raccoon': import_folder('../graphics/particles/raccoon'),
            'spirit': import_folder('../graphics/particles/nova'),
            'bamboo': import_folder('../graphics/particles/bamboo')
        }

    def create_particles(self, animation_type, pos, groups):
        """
        shows the animations
        :param groups:
        :param animation_type:
        :param pos:
        :return:
        """

        animation_frames = self.frames[animation_type]
        ParticleEffeect(pos, animation_frames, groups)


class ParticleEffeect(pygame.sprite.Sprite):
    def __init__(self,pos,animation_frames,groups):
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frames = animation_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        super().__init__(groups)

    def animate(self):
        """
        make the particals stop after 1 time
        :return:
        """
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()
