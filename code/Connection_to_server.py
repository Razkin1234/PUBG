class Connection_to_server:

    ####################################################################################################################
    # FOR SENDING PACKETS
    ####################################################################################################################
    def __init__(self, id, packet):
        self.__packet = packet
        self.__rotshild_opening_clients_packets = f'Rotshild {id}\r\n\r\n'

    def add_header_login_request(self, user_name, password):
        self.__packet += f'login_request: {user_name},{password}\r\n'
        return self.__packet

    def add_header_register_request(self, user_name, password):
        self.__packet += f'register_request: {user_name},{password}\r\n'
        return self.__packet

    def add_header_inventory_update(self, header_name, name_of_item):
        """
        in the client they will check what item is it and the will send us
        :param name_of_item:
        :param header_name: +/- and if it weapons or something else
        :param packet:
        :return:
        """
        self.__packet += f'inventory_update: {header_name} {name_of_item}\r\n'
        return self.__packet

    def add_header_player_place_and_image(self, player_place, image):
        self.__packet += f'player_place: {player_place}\r\nimage: {image}\r\n'
        return self.__packet

    def add_header_shot_place_and_hit_hp(self, shot_place, hit_hp):
        self.__packet += f'shot_place: {shot_place}\r\nhit_hp: {hit_hp}\r\n'
        return self.__packet

    def add_header_dead(self, dead):
        self.__packet += f'dead: {dead}\r\n'
        return self.__packet

    def add_header_chat(self, message):
        self.__packet += f'chat: {message}\r\n'
        return self.__packet
