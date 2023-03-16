class Connection_to_server:

    ####################################################################################################################
    # FOR SENDING PACKETS
    ####################################################################################################################


    def __init__(self, id):
        if id == None:
            id = ""
        self.__packet = f'Rotshild {id}\r\n\r\n'

    def add_header_login_request(self, user_name, password):
        self.__packet += f'login_request: {user_name},{password}\r\n'

    def add_header_register_request(self, user_name, password):
        self.__packet += f'register_request: {user_name},{password}\r\n'

    def add_header_inventory_update(self, header_name, name_of_item):
        """
        in the client they will check what item is it and the will send us
        :param name_of_item:
        :param header_name: +/- and if it weapons or something else
        :param packet:
        :return:
        """
        self.__packet += f'inventory_update: {header_name} {name_of_item}\r\n'

    def add_header_player_place_and_image(self, player_place, image):
<<<<<<< HEAD:code/Connection_to_server.py
        self.__packet += f'player_place: {str(player_place).replace(" ", "")}\r\nimage: {image}\r\n'
=======
        self.__packet += f'player_place: {player_place}\r\nimage: {image}\r\n'
>>>>>>> c889099ae00df15ec43116487240717081b3153b:Connection_to_server.py

    def add_header_shot_place_and_hit_hp(self, shot_place, hit_hp):
        self.__packet += f'shot_place: {shot_place}\r\nhit_hp: {hit_hp}\r\n'

    def add_header_dead(self, dead):
        self.__packet += f'dead: {dead}\r\n'

    def add_header_chat(self, message):
        self.__packet += f'chat: {message}\r\n'

    def add_header_disconnect(self, id_of_player):
        self.__packet += f'disconnect: {id_of_player}\r\n'

    def add_object_update(self, pick_drop, type_object, place, amount, how_many_dropped_picked):
        self.packet += f'object_update: {pick_drop}-{type_object}-{place}-{amount}'
        for i in range(how_many_dropped_picked - 1):
            self.packet += f'/{pick_drop}-{type_object}-{place}-{amount}'
        self.__packet += '\r\n'

    def add_hit_an_enemy(self, id_of_enemy, hp_to_sub):
        self.__packet += f'hit_an_enemy: {id_of_enemy},{hp_to_sub}'

    def get_packet(self):
        return self.__packet
