from settings import COL_TILES, ROW_TILES,weapon_data
# from level import Level
from other_players import Players
from player import Player
from YsortCameraGroup import YsortCameraGroup
class Incoming_packets:

    ####################################################################################################################
    # FOR FILTERING INCOMING PACKETS
    ####################################################################################################################
    def _init_(self, packet, address, server_ip, client_id):
        self.__packet = packet
        self.__src_ip = address[0]
        self.__src_port = address[1]
        self.__server_ip = server_ip
        self.__client_id = client_id # it can be null


    def set_packet_after_filter(self, packet):
        self.__packet = packet

    def set_playe_id(self, client_id):
        self.__client_id = client_id

    def get_id(self):
        return self.__client_id

    def rotshild_filter(self):
        expected = 'Rotshild'.encode('utf-8')
        if self.__packet[:len(expected)] != expected or not self.check_if_id_matches_ip_port():
            return False
        self.set_packet_after_filter(self.__packet.decode('utf-8'))
        return True

    def get_packet(self):
        return self.__packet

    def check_if_id_matches_ip_port(self):
        return (self.__src_ip, self.__src_port) in (self._server_ip, 56789)

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
                pass

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

    def handle_player_place(self, player_place, player_id, image, my_player_pos, visiable_sprites):  # maybe done
        # to add a check this is real
        # if not so return false
        # and if its okay to do here the checking if its in your map to print it
        pass
        try:
            player_place = (int(player_place[0]), int(player_place[1]))

            if player_place[0] < COL_TILES * 64 and player_place[0] > 0 and player_place[1] < ROW_TILES * 64 and \
                    player_place[1] > 0:
                Players(image, player_id, player_place, visiable_sprites)


        except Exception as e:
            print(e)


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

