class Incoming_packets:

    ####################################################################################################################
    # FOR FILTERING INCOMING PACKETS
    ####################################################################################################################
    def __init__(self, packet, address, server_ip, client_id):
        self.__packet = packet
        self.__src_ip = address[0]
        self.__src_port = address[1]
        self.__server_ip = server_ip
        self.__client_id = client_id

    def set_packet_after_filter(self, packet):
        self.__packet = packet

    def rotshild_filter(self):
        expected = 'Rotshild'.encode('utf-8')
        if self.__packet[:len(expected)] != expected or not self.check_if_id_matches_ip_port():
            return False
        self.set_packet_after_filter(self.__packet.decode('utf-8'))

    def check_if_id_matches_ip_port(self):
        return (self.__src_ip, self.__src_port) in (self.__server_ip, 56789)

    def handle_login_status(self, login_status):
        if login_status == 'fail':
            # here to add that it is wrong
            return False, 'password or username is incorrect'
        elif login_status == 'already_active':
            # here to add a message that the user is active in the game already
            return False, 'someone already logged in'
        self.handle_first_inventory()
        return login_status  # returning the id of the client is given

    def handle_first_inventory(self):
        # to add it to the inventory
        pass

    def handle_register_status(self, register_status):
        if register_status == 'taken':
            # here to add that the message is taken
            pass
        elif register_status == 'invalid':
            # here to add it isn't like we asked
            pass
        elif register_status == 'success':
            # to go now back to the login page
            pass

    def handle_player_place(self, player_place, player_id, image):
        # to add a check this is real
        # if not so return false
        # and if its okay to do here the checking if its in your map to print it
        pass

    def handle_shot_place(self, shot_place):
        # to check if its real and if not return false and
        # if yes print it on the map
        pass

    def handle_hit_id(self, hit_id, hit_hp):
        if hit_id == self.__client_id:
            # decrease your life by the hit_hp
            pass

    def handle_shooter_id(self, shooter_id):
        if self.__client_id == shooter_id:
            # add exp to your client
            pass

    def handle_dead(self, dead_id):
        # remove the dead id from your list
        pass

    def handle_chat(self, user_name, message):
        # print here the message and the user name
        pass

    def handle_server_shutdown(self):
        pass
