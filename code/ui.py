import pygame
from settings import *
from player import Player

class UI:
    def __init__(self,objects_on,items_on):
        #general
        self.display_surface = pygame.display.get_surface()
        self.font =pygame.font.Font(UI_FONT,UI_FONT_SIZE) #our font

        self.objects_on = dict(objects_on)

        #bar setup
        self.health_bar_rect = pygame.Rect(10,10,HEALTH_BAR_WIDTH,BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(10,34,ENERGY_BAR_WIDTH,BAR_HEIGHT)

        #convert weapon dictionary
        self.weapon_graphics = []
        for weapon in weapon_data.values(): #putting the weapon visuals in a list {
            path = weapon['graphic']
            weapon = pygame.image.load(path).convert_alpha()
            self.weapon_graphics.append(weapon) #}

        #convert magic dictionary
        self.magic_graphics = []
        for magic in magic_data.values():  # putting the magic visuals in a list {
            path = magic['graphic']
            magic = pygame.image.load(path).convert_alpha()
            self.magic_graphics.append(magic)  # }


    def ui_screen(self,player):
        self.items_weapons_box()
        #weapons:
        self.selection_box(1190, 45, False, True)  # box 3
        self.selection_box(1105, 45, False, True)  # box 2
        self.selection_box(1020, 45, False, True)  # box 1

        self.selection_box(1190, 130, False, True)  # box 6
        self.selection_box(1105, 130, False, True)  # box 5
        self.selection_box(1020, 130, False, True)  # box 4

        #items:
        self.selection_box(1190, 260, False, True)  # box 3
        self.selection_box(1105, 260, False, True)  # box 2
        self.selection_box(1020, 260, False, True)  # box 1

        self.selection_box(1190, 345, False, True)  # box 6
        self.selection_box(1105, 345, False, True)  # box 5
        self.selection_box(1020, 345, False, True)  # box 4

        self.selection_box(1190, 430, False, True)  # box 9
        self.selection_box(1105, 430, False, True)  # box 8
        self.selection_box(1020, 430, False, True)  # box 7

        if 'sword' in self.objects_on:
            if self.objects_on['sword']['ui'] == 1:
                bg_rect = pygame.Rect(1020, 45, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
                weapon_surf = self.weapon_graphics[0]
                weapon_rect = weapon_surf.get_rect(center=bg_rect.center)
                if player.weapon == 'sword':
                    self.selection_box(1020, 45, True, True)  # box 1
                self.display_surface.blit(weapon_surf, weapon_rect)

    def items_weapons_box(self):
        #the weapon box
        text_surf = self.font.render('Weapons:', False, TEXT_COLOR)
        x = 1162  # where we put the abr
        y = 32
        text_rect = text_surf.get_rect(bottomright=(x, y))  # the bar

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate((45, 15)))  # filling the exp bar box
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate((45, 15)),  3)  # borders to the exp bar

        self.display_surface.blit(text_surf, text_rect)

        #the items box
        text_surf = self.font.render('Items:', False, TEXT_COLOR)
        x = 1148  # where we put the abr
        y = 247
        text_rect = text_surf.get_rect(bottomright=(x, y))  # the bar

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate((75, 15)))  # filling the exp bar box
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate((75, 15)), 3)  # borders to the exp bar

        self.display_surface.blit(text_surf, text_rect)


    def show_bar(self,current,max_amount,bg_rect,color): #the printing of the bars
        #draw the backround
        pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect)

        #converting stats to pixels
        ratio = current / max_amount #the amount of life we have
        current_width = bg_rect.width * ratio #the amount of pixels that we need to print
        current_rect = bg_rect.copy() #to print in the same location
        current_rect.width = current_width #the cuurent health width

        #drawing the bar
        pygame.draw.rect(self.display_surface,color,current_rect)
        pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,3)

    def show_exp(self,exp):
        text_surf = self.font.render(str(int(exp)),False,TEXT_COLOR)
        x = self.display_surface.get_size()[0] - 20 #where we put the abr
        y = self.display_surface.get_size()[1] - 20
        text_rect = text_surf.get_rect(bottomright = (x,y))#the bar

        pygame.draw.rect(self.display_surface,UI_BG_COLOR,text_rect.inflate((20,20))) #filling the exp bar box
        pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,text_rect.inflate((20,20)),3) #borders to the exp bar

        self.display_surface.blit(text_surf,text_rect)

    def selection_box(self,left,top,has_switched,player_shield_on): #the box for our weapon visual
        bg_rect = pygame.Rect(left,top,ITEM_BOX_SIZE,ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect)
        if not has_switched: #the border color will be different if we had swap weapon
            pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,3)
        else:
            pygame.draw.rect(self.display_surface,UI_BORDER_COLOR_ACTIVE,bg_rect,3)

        if not player_shield_on:
            pygame.draw.rect(self.display_surface, ENERGY_COLOR, bg_rect)
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def weapon_overlay(self,weapon_index,has_switched,player_shield_on ): #printing the weapon image
        bg_rect = self.selection_box(10, 630,has_switched,player_shield_on)  # box backround
        weapon_surf = self.weapon_graphics[weapon_index]
        weapon_rect = weapon_surf.get_rect(center = bg_rect.center)

        self.display_surface.blit(weapon_surf,weapon_rect)


    def magic_overlay(self,magic_index,has_switched,player_shield_on): #printing the magic image
        bg_rect = self.selection_box(80,635,has_switched,player_shield_on)  # box backround
        magic_surf = self.magic_graphics[magic_index]
        magic_rect = magic_surf.get_rect(center = bg_rect.center)

        self.display_surface.blit(magic_surf,magic_rect)

    def display(self,player):
      self.show_bar(player.health,player.stats['health'],self.health_bar_rect,HEALTH_COLOR) #to print the health bar
      self.show_bar(player.energy,player.stats['energy'],self.energy_bar_rect,ENERGY_COLOR) #to print the energy bar

      self.show_exp(player.exp)
      self.weapon_overlay(player.weapon_index, not player.can_switch_weapon,True)
      self.magic_overlay(player.magic_index, not player.can_switch_magic,player.can_shield)


