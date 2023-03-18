import pygame
from settings import *
from item import Item
from weapon_item import Weapon_item
class UI:
    def __init__(self,objects_on,items_on,item_sprites,weapon_sprites):
        #general
        self.display_surface = pygame.display.get_surface()
        self.font =pygame.font.Font(UI_FONT,UI_FONT_SIZE) #our font
        self.item_sprites = item_sprites
        self.weapon_sprites = weapon_sprites

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

        self.weapon_graphics_dict = {} #a dict that contains the image of evevry weapon
        for magic , magic_value in weapon_data.items():
            path = magic_value['graphic']
            image = pygame.image.load(path).convert_alpha()
            self.weapon_graphics_dict[magic] = image

        self.item_graphics_dict = {}  # a dict that contains the image of evevry weapon
        for magic, magic_value in item_data.items():
            path = magic_value['graphic']
            image = pygame.image.load(path).convert_alpha()
            self.item_graphics_dict[magic] = image

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
        self.backpack_items_box = {
            '1': {'left': 1020, 'top': 515, 'onit': False, 'rep': True},
            '2': {'left': 1105, 'top': 515, 'onit': False, 'rep': True},
            '3': {'left': 1190, 'top': 515, 'onit': False, 'rep': True}
        }

        self.replace_first_one = []
        self.replace_first_item = []

        self.plus_health = self.plus_health
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

        self.can_press_c = True
        self.c_pressed_time = None
        self.c_pressed_cooldown = 150

        # chat:
        self.user_text = ''  # the text that the user has used
        self.chat_messages = [
        'guy is fat'
        ]  # the mesagges that we will show on the screen

        # for the letters cooldown
        self.can_write_letter = True
        self.letter_pressed_time = None
        self.letter_pressed_cooldown = 115

        self.writing = False #for the graphics☺

    def ui_screen(self,player):
        self.items_weapons_box()
        self.ui_input(player)
        if self.box_on[0] == 'weapon':
            self.ui_weapon_boxes[f'{self.box_on[1]}']['onit'] = True
        elif self.box_on[0]=='item': self.ui_item_boxes[f'{self.box_on[1]}']['onit'] = True
        else: self.backpack_items_box[f'{self.box_on[1]}']['onit'] = True

        #chat:
        self.chat_display()

        #weapons:
        for box,box_value in self.ui_weapon_boxes.items():
            self.selection_box(box_value['left'],box_value['top'],box_value['onit'],box_value['rep'])
        #items:
        for box,box_value in self.ui_item_boxes.items():
            self.selection_box(box_value['left'],box_value['top'],box_value['onit'],box_value['rep'])
        #backpack
        if 'backpack' in player.items_on:
            for box, box_value in self.backpack_items_box.items():
                self.selection_box(box_value['left'], box_value['top'], box_value['onit'], box_value['rep'])

        for weapon , weapon_value in player.objects_on.items():
            temp_dict = self.ui_weapon_boxes[str(player.objects_on[weapon]['ui'])]
            bg_rect = pygame.Rect(temp_dict['left'],temp_dict['top'],ITEM_BOX_SIZE,ITEM_BOX_SIZE)
            weapon_surf = self.weapon_graphics_dict[weapon]
            weapon_rect = weapon_surf.get_rect(center=bg_rect.center)
            self.display_surface.blit(weapon_surf, weapon_rect)

        for item , item_value in player.items_on.items():
            if 1 <= player.items_on[item]['ui'] <= 9:
                temp_dict = self.ui_item_boxes[str(player.items_on[item]['ui'])]
            else:
                temp_dict = self.backpack_items_box[str(player.items_on[item]['ui']-9)]
            bg_rect = pygame.Rect(temp_dict['left'],temp_dict['top'],ITEM_BOX_SIZE,ITEM_BOX_SIZE)
            item_surf = self.item_graphics_dict[player.items_on[item]['name']]
            item_rect = item_surf.get_rect(center=bg_rect.center)
            self.display_surface.blit(item_surf, item_rect)

        self.cooldown() #for the cooldown

    def chat_display(self):
        #chat box
        bg_rect = pygame.Rect(7, 65, 400, 200)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        #player input box
        bg_rect = pygame.Rect(7, 262, 400, 35)
        pygame.draw.rect(self.display_surface, 'gray', bg_rect)

        #for the border of the chat box
        if self.writing:
            pygame.draw.rect(self.display_surface, 'blue', bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

        #printing the messages:
        y = 70
        x = 14
        font = pygame.font.Font(None, 32)
        for message in self.chat_messages:
            text = font.render(message, True, (255, 255, 255))
            self.display_surface.blit(text,(x,y))
            y+= 27

        #for the user text box
        text = font.render(self.user_text, True, (0, 0, 0))
        self.display_surface.blit(text, (17, 267))

    def ui_input(self,player,packet_to_send):
        keys = pygame.key.get_pressed()
        if not player.chat_input: #if the chat is not on
            if keys[pygame.K_v]: #making the chat value on
                player.chat_input = True
                self.letter_pressed_time = pygame.time.get_ticks()
                self.can_write_letter = False
            if keys[pygame.K_w]:
                if self.can_press_w:
                    self.can_press_w = False
                    self.w_pressed_time = pygame.time.get_ticks()
                    if not (1<=self.box_on[1]<=3):
                        if self.box_on[0] == 'weapon':
                            self.ui_weapon_boxes[f'{self.box_on[1]}']['onit'] = False
                        elif self.box_on[0]== 'item': self.ui_item_boxes[f'{self.box_on[1]}']['onit'] = False
                        self.box_on[1] = self.box_on[1]-3
                    else:
                        if self.box_on[0] == 'item':
                            self.ui_item_boxes[f'{self.box_on[1]}']['onit'] = False
                            self.box_on[0] = 'weapon'
                            self.box_on[1] += 3
                        elif self.box_on[0] == 'backpack':
                            self.backpack_items_box[f'{self.box_on[1]}']['onit'] = False
                            self.box_on[0] = 'item'
                            self.box_on[1] += 6

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
                    elif self.box_on[0] == 'item':
                        self.ui_item_boxes[f'{self.box_on[1]}']['onit'] = False
                        if not (7 <= self.box_on[1] <= 9):
                            self.box_on[1] = self.box_on[1] + 3
                        else:
                            if 'backpack' in player.items_on:
                                self.box_on[0] = 'backpack'
                                self.box_on[1] -= 6




            if keys[pygame.K_a]:
                if self.can_press_s:
                    self.can_press_s = False
                    self.s_pressed_time = pygame.time.get_ticks()
                    if (self.box_on[1]-1) % 3 != 0:
                        if self.box_on[0] == 'weapon':
                            self.ui_weapon_boxes[f'{self.box_on[1]}']['onit'] = False
                        elif self.box_on[0] == 'item':
                            self.ui_item_boxes[f'{self.box_on[1]}']['onit'] = False
                        else:
                            self.backpack_items_box[f'{self.box_on[1]}']['onit'] = False
                        self.box_on[1] -= 1

            if keys[pygame.K_d]:
                if self.can_press_d:
                    self.can_press_d = False
                    self.d_pressed_time = pygame.time.get_ticks()
                    if self.box_on[1] % 3 != 0:
                        if self.box_on[0] == 'weapon':
                            self.ui_weapon_boxes[f'{self.box_on[1]}']['onit'] = False
                        elif self.box_on[0]=='item': self.ui_item_boxes[f'{self.box_on[1]}']['onit'] = False
                        else: self.backpack_items_box[f'{self.box_on[1]}']['onit'] = False
                        self.box_on[1] += 1

            if keys[pygame.K_z]: #remove the item or weapon from the player
                if self.can_press_z:
                    self.can_press_z = False
                    self.z_pressed_time = pygame.time.get_ticks()
                    if self.box_on[0] == 'weapon':
                        objects_copy = player.objects_on.copy()
                        for weapon, weapon_value in objects_copy.items():
                            if weapon_value['ui'] == self.box_on[1]:
                                if len(list(player.objects_on.keys()))> 1:
                                    player.can_pick_item = False
                                    player.drop_item_time = pygame.time.get_ticks()
                                    Weapon_item((player.rect[0:2]), self.weapon_sprites, weapon)  # item create
                                    packet_to_send.add_header_inventory_update("- weapon", weapon)
                                    del player.objects_on[weapon]


                                    if player.weapon_index < len(list(player.objects_on.keys())) - 1:
                                        player.weapon_index += 1  # new weapon
                                    else:
                                        player.weapon_index = 0
                                    player.weapon = list(player.objects_on.keys())[player.weapon_index]  # the weapon we are using
                    elif self.box_on[0]=='item':
                        objects_copy = player.items_on.copy()
                        for weapon, weapon_value in objects_copy.items():
                            if weapon_value['ui'] == self.box_on[1]:
                                if weapon != 'backpack':
                                    player.can_pick_item = False
                                    player.drop_item_time = pygame.time.get_ticks()
                                    Item((player.rect[0:2]), self.item_sprites, weapon_value['name'])  # item create
                                    packet_to_send.add_header_inventory_update(f"- {weapon_value['name']}", 1)
                                    del player.items_on[weapon]
                                else: #only for the backpack erasing
                                    items_copy = player.items_on.copy()
                                    del_flag = True
                                    for item , item_data in items_copy.items():
                                        if 10 <= item_data['ui'] <= 12:
                                            del_flag = False
                                    if del_flag:
                                        player.can_pick_item = False
                                        player.drop_item_time = pygame.time.get_ticks()
                                        Item((player.rect[0:2]), self.item_sprites, weapon_value['name'])  # item create
                                        del player.items_on[weapon]

                    else: #for the backpack items
                        objects_copy = player.items_on.copy()
                        for weapon, weapon_value in objects_copy.items():
                            if weapon_value['ui'] - 9 == self.box_on[1]:
                                if weapon != 'backpack':
                                    player.can_pick_item = False
                                    player.drop_item_time = pygame.time.get_ticks()
                                    Item((player.rect[0:2]), self.item_sprites, weapon_value['name'])  # item create
                                    del player.items_on[weapon]
                                else:  # only for the backpack erasing
                                    items_copy = player.items_on.copy()
                                    del_flag = True
                                    for item, item_data in items_copy.items():
                                        if 9 <= item_data['ui'] <= 12:
                                            del_flag = False
                                    if del_flag:
                                        player.can_pick_item = False
                                        player.drop_item_time = pygame.time.get_ticks()
                                        Item((player.rect[0:2]), self.item_sprites, weapon_value['name'])  # item create
                                        del player.items_on[weapon]
                                        self.box_on[0] = 'item'
                                        self.box_on[1] += 6

            if keys[pygame.K_c]: #to use an item
                if self.can_press_c:
                    self.c_pressed_time = pygame.time.get_ticks()
                    self.can_press_c = False
                    if self.box_on[0] == 'item':
                        items_copy = player.items_on.copy()
                        for item , item_data in items_copy.items():
                            if item_data['ui'] == self.box_on[1]:
                                if item_data['name'] == 'medkit':
                                    self.plus_health(50,player)
                                    objects_copy = player.items_on.copy() #deletes the medkit after the use
                                    for weapon, weapon_value in objects_copy.items():
                                        if weapon_value['ui'] == self.box_on[1]:
                                            if len(list(player.items_on.keys())) > 0:
                                                del player.items_on[weapon]
                                if item_data['name'] == 'bendage':
                                    self.plus_health(10,player)
                                    objects_copy = player.items_on.copy() #deletes the medkit after the use
                                    for weapon, weapon_value in objects_copy.items():
                                        if weapon_value['ui'] == self.box_on[1]:
                                            if len(list(player.items_on.keys())) > 0:
                                                del player.items_on[weapon]
                    elif self.box_on[0] == 'backpack': #for the backpack
                        items_copy = player.items_on.copy()
                        for item, item_data in items_copy.items():
                            if item_data['ui'] == self.box_on[1] + 9:
                                if item_data['name'] == 'medkit':
                                    self.plus_health(50, player)
                                    objects_copy = player.items_on.copy()  # deletes the medkit after the use
                                    for weapon, weapon_value in objects_copy.items():
                                        if weapon_value['ui'] == self.box_on[1] + 9:
                                            if len(list(player.items_on.keys())) > 0:
                                                del player.items_on[weapon]
                                if item_data['name'] == 'bendage':
                                    self.plus_health(10, player)
                                    objects_copy = player.items_on.copy()  # deletes the medkit after the use
                                    for weapon, weapon_value in objects_copy.items():
                                        if weapon_value['ui'] == self.box_on[1] + 9:
                                            if len(list(player.items_on.keys())) > 0:
                                                del player.items_on[weapon]



            if keys[pygame.K_x]:
                if self.can_press_x:
                    self.x_pressed_time = pygame.time.get_ticks()
                    self.can_press_x = False
                    if self.box_on[0] == 'weapon':
                        if len(self.replace_first_one) == 0:
                            self.replace_first_one = self.box_on.copy()
                            self.ui_weapon_boxes[f'{self.replace_first_one[1]}']['rep'] = False
                        else:
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
                    else:
                        if len(self.replace_first_item) == 0:
                            self.replace_first_item = self.box_on.copy()
                            if self.replace_first_item[0] == 'item':
                                self.ui_item_boxes[f'{self.replace_first_item[1]}']['rep'] = False
                            else:
                                self.backpack_items_box[f'{self.replace_first_item[1]}']['rep'] = False
                        else:
                            item_to_replace = None
                            second_item_to_replace = None
                            for weapon , weapon_value in player.items_on.items():
                                if self.replace_first_item[0] == 'item':
                                    if self.replace_first_item[1] == weapon_value['ui']:
                                        item_to_replace = weapon
                                else:
                                    if self.replace_first_item[1] == weapon_value['ui'] - 9:
                                        item_to_replace = weapon
                                if self.box_on[0] == 'item':
                                    if self.box_on[1] == weapon_value['ui']:
                                        second_item_to_replace = weapon
                                else:
                                    if self.box_on[1] == weapon_value['ui'] - 9:
                                        second_item_to_replace = weapon


                            if item_to_replace != None and second_item_to_replace != None:
                                temp = player.items_on[item_to_replace]['ui']
                                player.items_on[item_to_replace]['ui'] = player.items_on[second_item_to_replace]['ui']
                                player.items_on[second_item_to_replace]['ui'] = temp
                            elif item_to_replace != None and second_item_to_replace == None:
                                if self.box_on[0] == 'item':
                                    player.items_on[item_to_replace]['ui'] = self.box_on[1]
                                else:  player.items_on[item_to_replace]['ui'] = self.box_on[1] + 9

                            elif item_to_replace == None and second_item_to_replace != None:
                                if self.replace_first_item[0] == 'item':
                                    player.items_on[second_item_to_replace]['ui'] = self.replace_first_item[1]
                                else: player.items_on[second_item_to_replace]['ui'] = self.replace_first_item[1]+9
                            if self.replace_first_item[0] == 'item':
                                self.ui_item_boxes[f'{self.replace_first_item[1]}']['rep'] = True
                            else: self.backpack_items_box[f'{self.replace_first_item[1]}']['rep'] = True
                            self.replace_first_item.clear() #if n
        else: #if the chat is on:
            self.writing = True
            if self.can_write_letter:
                key_pressed = False
                # it will send the message if we pass the letter limmit or pressed enter:
                if keys[pygame.K_RETURN] or len(self.user_text) >= 22:
                    key_pressed = True #for the cooldown
                    self.writing = False
                    player.chat_input = False
                    self.chat_messages.append(self.user_text)
                    self.user_text = ''
                    #checking if we display to much messages:
                    if len(self.chat_messages) > 7:
                        self.chat_messages.pop(0)

                elif keys[pygame.K_SPACE]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + ' '
                elif keys[pygame.K_BACKSPACE]:
                    key_pressed = True
                    self.user_text = self.user_text[:-1]

                elif keys[pygame.K_a]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'a'
                elif keys[pygame.K_b]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'b'
                elif keys[pygame.K_c]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'c'
                elif keys[pygame.K_d]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'd'
                elif keys[pygame.K_e]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'e'
                elif keys[pygame.K_f]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'f'
                elif keys[pygame.K_g]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'g'
                elif keys[pygame.K_h]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'h'
                elif keys[pygame.K_i]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'i'
                elif keys[pygame.K_j]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'j'
                elif keys[pygame.K_k]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'k'
                elif keys[pygame.K_l]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'l'
                elif keys[pygame.K_m]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'm'
                elif keys[pygame.K_n]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'n'
                elif keys[pygame.K_o]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'o'
                elif keys[pygame.K_p]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'p'
                elif keys[pygame.K_q]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'q'
                elif keys[pygame.K_r]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'r'
                elif keys[pygame.K_s]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 's'
                elif keys[pygame.K_t]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 't'
                elif keys[pygame.K_u]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'u'
                elif keys[pygame.K_v]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'v'
                elif keys[pygame.K_w]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'w'
                elif keys[pygame.K_x]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'x'
                elif keys[pygame.K_y]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'y'
                elif keys[pygame.K_z]:
                    key_pressed = True  # for the cooldown
                    self.user_text = self.user_text + 'z'

                if key_pressed:
                    self.can_write_letter = False
                    self.letter_pressed_time = pygame.time.get_ticks()

    def plus_health(self,heel,player):
        """
        gets how much to heel the player (player.health + heel) and the player
        heel the player.health by the heel parameter we got
        """
        if player.health+heel >= 100:
            player.health = 100
        else: player.health += heel

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
        if not self.can_press_c:
            if current_time - self.c_pressed_time >= self.c_pressed_cooldown:
                self.can_press_c = True

        if not self.can_write_letter: #for the chat writing
            if current_time - self.letter_pressed_time >= self.letter_pressed_cooldown:
                self.can_write_letter = True

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

    def weapon_overlay(self,has_switched,player_shield_on,player ): #printing the weapon image
        bg_rect = self.selection_box(10, 630,has_switched,player_shield_on)  # box backround
        weapon_surf = self.weapon_graphics_dict[player.weapon]
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
      self.weapon_overlay(not player.can_switch_weapon,True, player)
      self.magic_overlay(player.magic_index, not player.can_switch_magic,player.can_shield)

