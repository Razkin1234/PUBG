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
        self.__packet += f'player_place: {str(player_place).replace(" ", "")}\r\nimage: {image}\r\n'

    def add_header_shot_place_and_hit_hp(self, shot_place, hit_hp):
        shot_place = str(shot_place).replace(' ','')
        self.__packet += f'shot_place: {shot_place}\r\nhit_hp: {hit_hp}\r\n'

    def add_header_dead(self, dead):
        self.__packet += f'dead: {dead}\r\n'

    def add_header_chat(self, message):
        self.__packet += f'chat: {message}\r\n'

    def add_header_disconnect(self, id_of_player):
        self.__packet += f'disconnect: {id_of_player}\r\n'

    def for_dead_object_update(self, player):
        # how_many = {'sword' : 0,'lance': 0, 'axe' : 0, 'rapier' : 0, 'sai' : 0, 'gun' : 0, 'backpack' : 0, 'ammo' : 0, 'boots' : 0, 'medkit' : 0, 'bendage' : 0}
        how_many = {}
        for_this = ''
        for item in player.items_on():
            if 'backpack' == item:
                if item in how_many:
                    how_many[item] += 1
                else:
                    how_many[item] = 1
            elif 'ammo' == item:
                if item in how_many:
                    how_many[item] += 1
                else:
                    how_many[item] = 1
            elif 'boots' == item:
                if item in how_many:
                    how_many[item] += 1
                else:
                    how_many[item] = 1
            elif 'medkit' == item:
                if item in how_many:
                    how_many[item] += 1
                else:
                    how_many[item] = 1
            elif 'bendage' == item:
                if item in how_many:
                    how_many[item] += 1
                else:
                    how_many[item] = 1
        for weapon in player.objects_on():
            if 'sword' == weapon:
                if weapon in how_many:
                    how_many[weapon] += 1
                else:
                    how_many[weapon] = 1
            elif 'lance' == weapon:
                if weapon in how_many:
                    how_many[weapon] += 1
                else:
                    how_many[weapon] = 1
            elif 'axe' == weapon:
                if weapon in how_many:
                    how_many[weapon] += 1
                else:
                    how_many[weapon] = 1
            elif 'rapier' == weapon:
                if weapon in how_many:
                    how_many[weapon] += 1
                else:
                    how_many[weapon] = 1
            elif 'sai' == weapon:
                if weapon in how_many:
                    how_many[weapon] += 1
                else:
                    how_many[weapon] = 1
            elif 'gun' == weapon:
                if weapon in how_many:
                    how_many[weapon] += 1
                else:
                    how_many[weapon] = 1
        for key in how_many:
            for_this += f'object_update: drop-{key}-{player.rect.center}-{how_many[key]}/'
        for_this = for_this[:-1]
        for_this += '\r\n'
        self.__packet += for_this

    def add_object_update(self, pick_drop, type_object, place, amount):
        if type(place) != str:
            place = str(place)
        place = place.replace(' ', '')
        self.__packet += f'object_update: {pick_drop}-{type_object}-{place}-{amount}\r\n'

    def get_packet(self):
        return self.__packet

    def add_hit_an_enemy(self, id_of_enemy, hp_to_sub):
        self.__packet += f'hit_an_enemy: {id_of_enemy},{hp_to_sub}'
