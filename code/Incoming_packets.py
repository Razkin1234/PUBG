from settings import COL_TILES, ROW_TILES,weapon_data
# from level import Level
from other_players import Players
from player import Player
from YsortCameraGroup import YsortCameraGroup
from item import Item
from enemy import  Enemy
class Incoming_packets:

    ####################################################################################################################
    # FOR FILTERING INCOMING PACKETS
    ####################################################################################################################
    def __init__(self, packet, server_ip, client_id):
        self.__packet = packet
        self.__server_ip = server_ip
        self.__client_id = client_id # it can be null


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

    def handle_first_inventory(self, first_inventory, player):
        # to add it to the inventory
        items = first_inventory.split(", ")
        weapons = first_inventory.split("/")[0]
        for weapon in weapons:
            if weapon in weapon_data:
                player.objects_on[weapon] = weapon_data[weapon]
            for item in items:
                player.items_on[item]
    def handle_register_status(self, register_status):
        if register_status == 'taken':
            # here to add that the message is taken
            return False, 'is taken'
        elif register_status == 'invalid':
            return False, 'invalid'
        elif register_status == 'success':
            # to go now back to the login page
            return True, None
            pass

    def handle_player_place(self, player_place, player_id, image, my_player_pos, visiable_sprites,obstecal_sprits):  # maybe done
        # to add a check this is real
        # if not so return false
        # and if its okay to do here the checking if its in your map to print it
        pass
        try:

            player_place = tuple((player_place[1:-1].split(',')) ) # converting the place from str to tuple
            player_place = (int(player_place[0]),int(player_place[1]))

            if player_place[0] < COL_TILES * 64 and player_place[0] > 0 and player_place[1] < ROW_TILES * 64 and player_place[1] > 0:
                if not visiable_sprites.check_existines(player_id, image, player_place):
                    Enemy(1, player_id, player_place, visiable_sprites, obstecal_sprits, image)


        except Exception as e:
            print(str(e) + f"line_{e.__traceback__.tb_lineno}")


    def handle_shot_place(self, shot_place):
        # to check if its real and if not return false and
        # if yes print it on the map
        pass


    def handle_dead(self, dead_id, visble_sprites):  # dont need

        # remove the dead id from your list
        visble_sprites.erase_dead_sprites(int(dead_id))

    def handle_chat(self, user_name, message):
        # print here the message and the user name
        return f'{user_name}: {message}'

    def handle_server_shutdown(self):
        pass

    def handle_disconnect(self):
        # remove a player from your list don't print him anymore
        pass

    def handle_object_update(self, header_info):
        changes = header_info.split('/')
        for each_change in changes:
            each_change = each_change.split('-')
            if each_change[0] == 'pick':
                # so delete the object that is on the screen, you have the type in each_change[1] and the place in each_change[2]
                pass
            else:
                # print the object on the screen, you have the type in each_change[1] and the place in each_change[2]
                pass

    def handle_first_objects_position(self, header_info,item_sprites):
        changes = header_info.split('/')
        for each_change in changes:
            each_change1 = each_change.split('-')
            if each_change1[0] == 'weapons':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(place_number[1]):
                        item_place = (int(place_number[1]), int(place_number[4]))
                        Item(item_place,item_sprites,each_change1[0])
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'Weapons':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(place_number[1]):
                        item_place = (int(place_number[1]), int(place_number[4]))
                        Item(item_place, item_sprites, each_change1[0])
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'Weapons':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(place_number[1]):
                        item_place = (int(place_number[1]), int(place_number[4]))
                        Item(item_place, item_sprites, each_change1[0])
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'Weapons':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(place_number[1]):
                        item_place = (int(place_number[1]), int(place_number[4]))
                        Item(item_place, item_sprites, each_change1[0])
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'ammo':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(place_number[1]):
                        item_place = (int(place_number[1]), int(place_number[4]))
                        Item(item_place, item_sprites, each_change1[0])
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'med_kits':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(place_number[1]):
                        item_place = (int(place_number[1]), int(place_number[4]))
                        Item(item_place, item_sprites, each_change1[0])
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'backpacks':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(place_number[1]):
                        item_place = (int(place_number[1]), int(place_number[4]))
                        Item(item_place, item_sprites, each_change1[0])
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'plasters':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(place_number[1]):
                        item_place = (int(place_number[1]), int(place_number[4]))
                        Item(item_place, item_sprites, each_change1[0])
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]
            elif each_change1[0] == 'shoes':
                how_many = each_change1[1].split(';')
                for screen in how_many:
                    place_number = screen.split('|')
                    for i in range(place_number[1]):
                        item_place = (int(place_number[1]), int(place_number[4]))
                        Item(item_place, item_sprites, each_change1[0])
                # save it in your thing that you saves things and print it in where the value is place_number[0] and you have the type in each_change1[0]

    def handle_dead_enemy(self, id,visble_sprites):
        # delete enemy from your list
        visble_sprites.erase_dead_sprites(int(id))

    # [id_enemy]/([the X coordinate],[the Y coordinate])/[type_of_enemy]/[Yes or No(if hitting)]-

    def handle_enemy_player_place_type_hit(self, header_info, player, bullet_group):
        info = header_info.split('-')
        for each_info in info:
            each_info = header_info.split('/')
            if each_info[3]=='yes':
                hit = True
            else:
                hit = False

            if not bullet_group.check_existines(each_info[0], hit, (int(each_info[1][1],int(each_info[1][4])))):
                Players(each_info[2],each_info[0],(int(each_info[1][1],int(each_info[1][4]))),)

            # in each_info[0] you have the enemy_id and in each_info[1] you have the place_of_enemy and in each_info[2] you have the type of the enemy and in each_info[3] you have Yes if him hitting ot No if not