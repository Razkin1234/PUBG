import pygame
from settings import *
from player import Player

class UI:
    def __init__(self,objects_on,items_on):
        #general
        self.display_surface = pygame.display.get_surface()
        self.font =pygame.font.Font(UI_FONT,UI_FONT_SIZE) #our font

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

        #the boxes will be printed if we will press i
        self.box_on = ['weapon',1]
        self.ui_weapon_boxes = {
            '1': {'left': 1020, 'top': 45, 'onit': False , 'rep': True },
            '2': {'left': 1105, 'top': 45, 'onit': False, 'rep': True},
            '3': {'left': 1190, 'top': 45, 'onit': False, 'rep': True},
            '4': {'left': 1020, 'top': 130, 'onit': False, 'rep': True},
            '5': {'left': 1105, 'top': 130, 'onit': False, 'rep': True},
            '6': {'left': 1190, 'top': 130, 'onit': False, 'rep': True}
        }

        self.ui_item_boxes = {
            '1': {'left': 1020, 'top': 260, 'onit': False, 'rep': True},
            '2': {'left': 1105, 'top': 260, 'onit': False, 'rep': True},
            '3': {'left': 1190, 'top': 260, 'onit': False, 'rep': True},
            '4': {'left': 1020, 'top': 345, 'onit': False, 'rep': True},
            '5': {'left': 1105, 'top': 345, 'onit': False, 'rep': True},
            '6': {'left': 1190, 'top': 345, 'onit': False, 'rep': True},
            '7': {'left': 1020, 'top': 430, 'onit': False, 'rep': True},
            '8': {'left': 1105, 'top': 430, 'onit': False, 'rep': True},
            '9': {'left': 1190, 'top': 430, 'onit': False, 'rep': True}
        }

        self.replace_first_one = []

        #cooldowns
        self.can_press_w = True
        self.w_pressed_time = None
        self.w_pressed_cooldown = 150

        self.can_press_s = True
        self.s_pressed_time = None
        self.s_pressed_cooldown = 150

        self.can_press_a = True
        self.a_pressed_time = None
        self.a_pressed_cooldown = 150

        self.can_press_d = True
        self.d_pressed_time = None
        self.d_pressed_cooldown = 150

        self.can_press_z = True
        self.z_pressed_time = None
        self.z_pressed_cooldown = 150

        self.can_press_x = True
        self.x_pressed_time = None
        self.x_pressed_cooldown = 150

    def ui_screen(self,player):
        self.items_weapons_box()
        self.ui_input(player)
        if self.box_on[0] == 'weapon':
            self.ui_weapon_boxes[f'{self.box_on[1]}']['onit'] = True
        else: self.ui_item_boxes[f'{self.box_on[1]}']['onit'] = True

        #weapons:
        for box,box_value in self.ui_weapon_boxes.items():
            self.selection_box(box_value['left'],box_value['top'],box_value['onit'],box_value['rep'])
        #items:
        for box,box_value in self.ui_item_boxes.items():
            self.selection_box(box_value['left'],box_value['top'],box_value['onit'],box_value['rep'])

        for weapon , weapon_value in player.objects_on.items():
            temp_dict = self.ui_weapon_boxes[str(player.objects_on[weapon]['ui'])]
            bg_rect = pygame.Rect(temp_dict['left'],temp_dict['top'],ITEM_BOX_SIZE,ITEM_BOX_SIZE)
            weapon_surf = self.weapon_graphics[weapon_value['graphics_num']]
            weapon_rect = weapon_surf.get_rect(center=bg_rect.center)
            self.display_surface.blit(weapon_surf, weapon_rect)

        self.cooldown() #for the cooldown

    def ui_input(self,player):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            if self.can_press_w:
                self.can_press_w = False
                self.w_pressed_time = pygame.time.get_ticks()
                if not (1<=self.box_on[1]<=3):
                    if self.box_on[0] == 'weapon':
                        self.ui_weapon_boxes[f'{self.box_on[1]}']['onit'] = False
                    else: self.ui_item_boxes[f'{self.box_on[1]}']['onit'] = False
                    self.box_on[1] = self.box_on[1]-3
                else:
                    if self.box_on[0] == 'item':
                        self.ui_item_boxes[f'{self.box_on[1]}']['onit'] = False
                        self.box_on[0] = 'weapon'
                        self.box_on[1] += 3
        if keys[pygame.K_s]:
            if self.can_press_s:
                self.can_press_s = False
                self.s_pressed_time = pygame.time.get_ticks()
                if self.box_on[0] == 'weapon':
                    self.ui_weapon_boxes[f'{self.box_on[1]}']['onit'] = False
                    if not (4 <= self.box_on[1] <= 6):
                        self.box_on[1] = self.box_on[1] + 3
                    else:
                        self.box_on[0] = 'item'
                        self.box_on[1] = self.box_on[1]-3
                else:
                    self.ui_item_boxes[f'{self.box_on[1]}']['onit'] = False
                    if not (7 <= self.box_on[1] <= 9):
                        self.box_on[1] = self.box_on[1] + 3

        if keys[pygame.K_a]:
            if self.can_press_s:
                self.can_press_s = False
                self.s_pressed_time = pygame.time.get_ticks()
                if (self.box_on[1]-1) % 3 != 0:
                    if self.box_on[0] == 'weapon':
                        self.ui_weapon_boxes[f'{self.box_on[1]}']['onit'] = False
                    else: self.ui_item_boxes[f'{self.box_on[1]}']['onit'] = False
                    self.box_on[1] -= 1

        if keys[pygame.K_d]:
            if self.can_press_d:
                self.can_press_d = False
                self.d_pressed_time = pygame.time.get_ticks()
                if self.box_on[1] % 3 != 0:
                    if self.box_on[0] == 'weapon':
                        self.ui_weapon_boxes[f'{self.box_on[1]}']['onit'] = False
                    else: self.ui_item_boxes[f'{self.box_on[1]}']['onit'] = False
                    self.box_on[1] += 1

        if keys[pygame.K_z]: #remove the item or weapon from the player
            if self.can_press_z:
                self.can_press_z = False
                self.z_pressed_time = pygame.time.get_ticks()
                if self.box_on[0] == 'weapon':
                    objects_copy = player.objects_on.copy()
                    for weapon, weapon_value in objects_copy.items():
                        if weapon_value['ui'] == self.box_on[1]:
                            del player.objects_on[weapon]
        if keys[pygame.K_x]:
            if self.can_press_x:
                self.x_pressed_time = pygame.time.get_ticks()
                self.can_press_x = False
                if self.box_on[0] == 'weapon':
                    if len(self.replace_first_one) == 0:
                        self.replace_first_one = self.box_on.copy()
                        self.ui_weapon_boxes[f'{self.replace_first_one[1]}']['rep'] = False
                    else:
                        print(self.replace_first_one)
                        print(self.box_on)
                        item_to_replace = None
                        second_item_to_replace = None
                        for weapon , weapon_value in player.objects_on.items():
                            if self.replace_first_one[1] == weapon_value['ui']:
                                item_to_replace = weapon
                            if self.box_on[1] == weapon_value['ui']:
                                second_item_to_replace = weapon
                        if item_to_replace != None and second_item_to_replace != None:
                            temp = player.objects_on[item_to_replace]['ui']
                            player.objects_on[item_to_replace]['ui'] = player.objects_on[second_item_to_replace]['ui']
                            player.objects_on[second_item_to_replace]['ui'] = temp
                        elif item_to_replace != None and second_item_to_replace == None:
                            player.objects_on[item_to_replace]['ui'] = self.box_on[1]
                        elif item_to_replace == None and second_item_to_replace != None:
                            player.objects_on[second_item_to_replace]['ui'] = self.replace_first_one[1]
                        self.ui_weapon_boxes[f'{self.replace_first_one[1]}']['rep'] = True
                        self.replace_first_one.clear()




    def cooldown(self):
        current_time = pygame.time.get_ticks()
        if not self.can_press_w:
            if current_time - self.w_pressed_time >= self.w_pressed_cooldown:
                self.can_press_w = True
        if not self.can_press_s:
            if current_time - self.s_pressed_time >= self.s_pressed_cooldown:
                self.can_press_s = True
        if not self.can_press_a:
            if current_time - self.a_pressed_time >= self.a_pressed_cooldown:
                self.can_press_a = True
        if not self.can_press_d:
            if current_time - self.d_pressed_time >= self.d_pressed_cooldown:
                self.can_press_d = True
        if not self.can_press_z:
            if current_time - self.z_pressed_time >= self.z_pressed_cooldown:
                self.can_press_z = True
        if not self.can_press_x:
            if current_time - self.x_pressed_time >= self.x_pressed_cooldown:
                self.can_press_x = True

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


