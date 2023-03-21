from settings import *
# from level import Level
from other_players import Players
from weapon_item import Weapon_item
from player import Player
from YsortCameraGroup import YsortCameraGroup
from item import Item
from enemy import Enemy
import pygame
import sys
import time

from bullet import Bullets


class Incoming_packets:

    ####################################################################################################################
    # FOR FILTERING INCOMING PACKETS
    ####################################################################################################################
    def __init__(self, packet, server_ip, client_id):
        self.__packet = packet
        self.__server_ip = server_ip
        self.__client_id = client_id  # it can be null

    def set_packet_after_filter(self, packet):
        self.__packet = packet

    def set_player_id(self, client_id):
        self.__client_id = client_id

    def get_id(self):
        return self.__client_id

    def rotshild_filter(self):
        expected = 'Rotshild'.encode('utf-8')
        if self.__packet[:len(expected)] != expected:
            return False
        self.set_packet_after_filter(self.__packet.decode('utf-8'))
        return True

    def get_packet(self):
        return self.__packet

    def handle_login_status(self, login_status):
        if login_status == 'fail':
            # here to add that it is wrong
            return False, 'password or username is incorrect'
        elif login_status == 'already_active':
            # here to add a message that the user is active in the game already
            return False, 'someone already logged in'
        return True, login_status  # returning the id of the client is given

    def handle_first_place(self, first_inventory):
        items = first_inventory.split(",")
        place_to_start = items[-1]

        place_to_start = tuple((place_to_start[1:-1].split('-')))  # converting the place from str to tuple
        place_to_start = (int(place_to_start[0]), int(place_to_start[1]))
        return place_to_start

    def handle_first_inventory(self, first_inventory, player):
        # to add it to the inventory
        items = first_inventory.split(",")
        new_item = []
        weapons = items[0].split("/")
        del items[0]
        del items[-1]
        for i, item in enumerate(items):
            try:
                items[i] = int(items[i])
                for j in range(items[i]):
                    if i == 0:
                        new_item.append('ammo')

                    elif i == 1:
                        new_item.append('medkit')

                    elif i == 2:
                        new_item.append('backpack')

                    elif i == 3:
                        new_item.append('bendage')

                    elif i == 4:
                        new_item.append('boots')
            except:
                pass
        print(new_item)
        for weapon in weapons:
            if weapon in weapon_data:
                if weapon not in player.objects_on:
                    count = 6
                    for i in range(1, count):
                        flag = True
                        for item, item_value in player.objects_on.items():
                            if item_value['ui'] == i:
                                flag = False
                                break
                        if flag:  # we will put the item in this slott
                            temp_dict = weapon_data[weapon].copy()
                            temp_dict['ui'] = i
                            player.objects_on[weapon] = temp_dict.copy()
                            temp_dict.clear()
                            break
        for item in new_item:
            if item in item_data:
                if 'ammo' in player.items_on:
                    if item == 'ammo':
                        if player.items_on['ammo']['amount'] < 200:
                            player.items_on['ammo']['amount'] += 1
                if 'backpack' in new_item:
                    count = 13
                else:
                    count = 10
                for i in range(1, count):
                    flag = True
                    for item1, item_value in player.items_on.items():
                        if item_value['ui'] == i:
                            flag = False
                            break
                    if flag:  # we will put the item in this slott
                        if item != "backpack" and item != 'boots' and item != 'ammo':
                            if item in items_add_data:
                                temp_dict = items_add_data[item].copy()
                                temp_dict['ui'] = i
                                counter = 0  # for the loop that gives the dict name in player.itmes (can't have the same names)
                                while True:
                                    if not str(counter) in player.items_on:
                                        player.items_on[str(counter)] = temp_dict.copy()
                                        temp_dict.clear()
                                        break
                                    counter += 1
                                break
                        elif item == 'backpack':
                            if 'backpack' in player.items_on:
                                break
                            else:
                                temp_dict = items_add_data[item].copy()
                                temp_dict['ui'] = i
                                player.items_on['backpack'] = temp_dict.copy()
                                temp_dict.clear()
                        elif item == 'boots':
                            if 'boots' in player.items_on:
                                break
                            else:
                                temp_dict = items_add_data[item].copy()
                                temp_dict['ui'] = i
                                player.items_on['boots'] = temp_dict.copy()
                                temp_dict.clear()
                        elif item == 'ammo':
                            if 'ammo' not in player.items_on:
                                temp_dict = items_add_data['ammo'].copy()
                                temp_dict['ui'] = i
                                player.items_on['ammo'] = temp_dict.copy()
                                player.items_on['ammo']['amount'] = 1
                                temp_dict.clear()

    def handle_register_status(self, register_status):
        if register_status == 'taken':
            # here to add that the message is taken
            return False, 'is taken'
        elif register_status == 'invalid':
            return False, 'invalid'
        elif register_status == 'success':
            # to go now back to the login page
            return True, None

    def handle_player_place(self, player_place, player_id, image, my_player_pos, visiable_sprites, obstecal_sprits,
                            damage_player, create_attack, destroy_attack, create_magic, bullet_group):  # maybe done
        # to add a check this is real
        # if not so return false
        # and if its okay to do here the checking if its in your map to print it
        # pass
        player_place = tuple((player_place[1:-1].split(',')))  # converting the place from str to tuple
        player_place = (int(player_place[0]), int(player_place[1]))

        if my_player_pos[0] + MIDDLE_SCREEN[0] > player_place[0] > my_player_pos[0] - MIDDLE_SCREEN[0] and \
                my_player_pos[1] + MIDDLE_SCREEN[1] > player_place[1] > my_player_pos[1] - MIDDLE_SCREEN[1]:
            image = image.split(',')

            if not visiable_sprites.check_existines(player_id, image, player_place):
                Players(player_place, visiable_sprites,
                        obstecal_sprits, create_attack, destroy_attack, create_magic,
                        bullet_group, player_id, image[0], image[1])
                pass

    def handle_shot_place(self, shot_place, bullet, obsicales_sprites, player_place):

        # add check if hit you
        # to check if its real and if not return false and
        # if yes print it on the map
        shot_place = tuple((shot_place[1:-1].split(',')))  # converting the place from str to tuple
        shot_place = (int(shot_place[0]), int(shot_place[1]))
        if player_place[0] + MIDDLE_SCREEN[0] > shot_place[0] > player_place[0] - MIDDLE_SCREEN[0] and \
                player_place[1] + MIDDLE_SCREEN[1] > shot_place[1] > player_place[1] - MIDDLE_SCREEN[1]:
            Bullets(shot_place, bullet, obsicales_sprites, None)

    def handle_dead(self, dead_id, visble_sprites):  # dont need

        # remove the dead id from your list
        visble_sprites.erase_dead_sprites(dead_id)

    def handle_chat(self, user_name, message):
        # print here the message and the user name
        return f'{user_name}: {message}'

    def handle_server_shutdown(self):
        pygame.quit()
        sys.exit()

    def handle_disconnect(self, dead_id, visble_sprites):
        visble_sprites.erase_dead_sprites(dead_id)

    def handle_object_update(self, header_info, item_sprites, weapon_sprites):
        changes = header_info.split('/')
        type_for_clients = ''
        for each_change in changes:
            each_change = each_change.split('-')
            if 'backpack' == each_change[1]:
                type_for_clients = 'backpack'
            elif 'boots' == each_change[1]:
                type_for_clients = 'boots'
            elif 'ammo' == each_change[1]:
                type_for_clients = 'ammo'
            elif 'med_kit' == each_change[1]:
                type_for_clients = 'medkit'
            elif 'bandage' == each_change[1]:
                type_for_clients = 'bendage'
            if each_change[0] == 'pick':
                # so delete the object that is on the screen, you have the type in each_change[1] and the place in each_change[2]
                each_change1 = tuple((each_change[2][1:-1].split(',')))  # converting the place from str to tuple
                each_change1 = (int(each_change1[0]), int(each_change1[1]))
                for item in item_sprites:
                    if item.rect.center == each_change1 and item.sprite_type == type_for_clients:
                        item.kill()
                        break
                for weapon in weapon_sprites:
                    if weapon.rect.center == each_change1 and weapon.sprite_type == each_change[1]:
                        weapon.kill()
                        break
            else:
                # print the object on the screen, you have the type in each_change[1] and the place in each_change[2]
                each_change1 = tuple((each_change[2][1:-1].split(',')))  # converting the place from str to tuple
                each_change1 = (int(each_change1[0]), int(each_change1[1]))
                if each_change[1] == 'ammo' or each_change[1] == 'med_kit' or each_change[1] == 'backpack' or \
                        each_change[1] == 'bandage' or each_change[1] == 'boots':
                    Item(each_change1, item_sprites, type_for_clients)
                else:
                    Weapon_item(each_change1, weapon_sprites, each_change[1])

    def handle_first_objects_position(self, header_info, item_sprites, weapon_sprites):
        changes = header_info.split('/')
        for each_change in changes:
            each_change1 = each_change.split('-')
            if each_change1[0] == 'sword':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(int(place_number[1])):
                        item_place = tuple((place_number[0][1:-1].split(',')))  # converting the place from str to tuple
                        item_place = (int(item_place[0]), int(item_place[1]))
                        # Weapon(item_place, item_sprites, 'sword')
                        Weapon_item(item_place, weapon_sprites, 'sword')
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'lance':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(int(place_number[1])):
                        item_place = tuple((place_number[0][1:-1].split(',')))  # converting the place from str to tuple
                        item_place = (int(item_place[0]), int(item_place[1]))
                        # Weapon(item_place, item_sprites, 'lance')
                        Weapon_item(item_place, weapon_sprites, 'lance')
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'axe':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(int(place_number[1])):
                        item_place = tuple((place_number[0][1:-1].split(',')))  # converting the place from str to tuple
                        item_place = (int(item_place[0]), int(item_place[1]))
                        # Weapon(item_place, item_sprites, 'axe')
                        Weapon_item(item_place, weapon_sprites, 'axe')
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'rapier':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(int(place_number[1])):
                        item_place = tuple((place_number[0][1:-1].split(',')))  # converting the place from str to tuple
                        item_place = (int(item_place[0]), int(item_place[1]))
                        # Item(item_place, item_sprites, 'rapier')
                        Weapon_item(item_place, weapon_sprites, 'rapier')
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'sai':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(int(place_number[1])):
                        item_place = tuple((place_number[0][1:-1].split(',')))  # converting the place from str to tuple
                        item_place = (int(item_place[0]), int(item_place[1]))
                        # Item(item_place, item_sprites, 'sai')
                        Weapon_item(item_place, weapon_sprites, 'sai')
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'gun':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(int(place_number[1])):
                        item_place = tuple((place_number[0][1:-1].split(',')))  # converting the place from str to tuple
                        item_place = (int(item_place[0]), int(item_place[1]))
                        # Item(item_place, item_sprites, 'gun')
                        Weapon_item(item_place, weapon_sprites, 'gun')
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'ammo':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(int(place_number[1])):
                        item_place = tuple((place_number[0][1:-1].split(',')))  # converting the place from str to tuple
                        item_place = (int(item_place[0]), int(item_place[1]))
                        Item(item_place, item_sprites, 'ammo')
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'med_kit':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(int(place_number[1])):
                        item_place = tuple((place_number[0][1:-1].split(',')))  # converting the place from str to tuple
                        item_place = (int(item_place[0]), int(item_place[1]))
                        Item(item_place, item_sprites, 'medkit')
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'backpack':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(int(place_number[1])):
                        item_place = tuple((place_number[0][1:-1].split(',')))  # converting the place from str to tuple
                        item_place = (int(item_place[0]), int(item_place[1]))
                        Item(item_place, item_sprites, 'backpack')
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'bandage':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(int(place_number[1])):
                        item_place = tuple((place_number[0][1:-1].split(',')))  # converting the place from str to tuple
                        item_place = (int(item_place[0]), int(item_place[1]))
                        Item(item_place, item_sprites, 'bendage')
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'boots':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(int(place_number[1])):
                        item_place = tuple((place_number[0][1:-1].split(',')))  # converting the place from str to tuple
                        item_place = (int(item_place[0]), int(item_place[1]))
                        Item(item_place, item_sprites, 'boots')
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]

    def handle_dead_enemy(self, id, visble_sprites):
        # delete enemy from your list
        visble_sprites.erase_dead_sprites(int(id))

    # [id_enemy]/([the X coordinate],[the Y coordinate])/[type_of_enemy]/[Yes or No(if hitting)]-

    def handle_enemy_player_place_type_hit(self, header_info, player, visiable_sprites, obstecal_sprits):
        info = header_info.split('-')
        for each_info in info:
            each_info = header_info.split('/')
            if each_info[3] == 'yes':
                hit = True
            else:
                hit = False

                if not visiable_sprites.check_existines(each_info[0], hit,
                                                        (int(each_info[1][1], int(each_info[1][4])))):
                    enemy_place = tuple((each_info[2][1:-1].split(',')))  # converting the place from str to tuple
                    enemy_place = (int(enemy_place[0]), int(enemy_place[1]))
                    if player.rect.center + MIDDLE_SCREEN[0] > enemy_place[0] > player.rect.center - MIDDLE_SCREEN[
                        0] and \
                            player.rect.center + MIDDLE_SCREEN[1] > enemy_place[1] > player.rect.center - MIDDLE_SCREEN[
                        1]:
                        Enemy(each_info[3], each_info[2], each_info[1], enemy_place, visiable_sprites, obstecal_sprits,
                              hit)

            # in each_info[0] you have the enemy_id and in each_info[1] you have the place_of_enemy and in each_info[2] you have the type of the enemy and in each_info[3] you have Yes if him hitting ot No if not
