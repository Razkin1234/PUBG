import pygame
from settings import *

class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player

    def shield(self,player,cost,groups):
        if player.exp >= cost and player.can_shield:
            player.can_shield = False
            player.exp -= cost
            self.animation_player.create_particles('aura',player.rect.center,groups)
            player.shield_timer = pygame.time.get_ticks()


    def highspeed(self,player,cost, packet_to_send):
        if player.exp >= cost and player.can_run:
            player.can_run = False
            player.exp -= cost
            player.speed = 16
            packet_to_send.add_header_player_place_and_image((int(player.rect.center[0]), int(player.rect.center[1])),
                                                             (int(player.place_to_go[0]), int(player.place_to_go[1])),
                                                             16, f'{player.status},no')
            player.run_timer = pygame.time.get_ticks()

    def ammo_add(self, player, cost, packet_to_send):  # gives us emmo not teleport
        if player.exp >= cost and player.can_ammo:
            magic_happend = False  # if we had used the magic (if we able to)
            if 'ammo' in player.items_on:
                if player.items_on['ammo']['amount'] + 20 < 200:
                    player.items_on['ammo']['amount'] += 20
                    packet_to_send.add_header_inventory_update("+ ammo", 20)
                    magic_happend = True

                    player.can_ammo = False
                    player.ammo_time = pygame.time.get_ticks()
                elif player.items_on['ammo']['amount'] + 20 > 200:
                    packet_to_send.add_header_inventory_update("+ ammo", 200-player.items_on['ammo']['amount'])
                    player.items_on['ammo']['amount'] = 200
                    magic_happend = True

            else:  # need to add ammo to the player
                if 'backpack' in player.items_on:
                    count = 13
                else:
                    count = 10
                for i in range(1, count):
                    flag = True
                    for item, item_value in player.items_on.items():
                        if item_value['ui'] == i:
                            flag = False
                            break
                    if flag:  # we will put the item in this slott
                        temp_dict = items_add_data['ammo'].copy()
                        temp_dict['ui'] = i
                        player.items_on['ammo'] = temp_dict.copy()
                        player.items_on['ammo']['amount'] = 20
                        packet_to_send.add_header_inventory_update("+ ammo", 20)
                        temp_dict.clear()
                        magic_happend = True  # to take exp if the magic worked

            if magic_happend:
                player.exp -= cost  # the xp remove
                player.can_ammo = False
                player.ammo_time = pygame.time.get_ticks()



