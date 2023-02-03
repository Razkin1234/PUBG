# place, x and y
#  all kinds of weapons classes


class Main_player:
    def __init__(self):
        self.__speed_of_player = 4
        self.__lives = 5

    def decrease_life(self):
        self.__lives = self.__lives - 1

    def get_life(self):
        return self.__lives

    def get_speed(self):
        return self.__speed_of_player

    def set_speed(self, new_speed):
        self.__speed_of_player = new_speed


class Weapons:
    def __init__(self):  # creating the class
        self.__distance = 0
        self.__speed_of_shot = 0

    def sniper(self):
        self.__distance = 10  # 10 cm
        self.__speed_of_shot = 2  # 2 cm/second

    def ar(self):
        self.__distance = 5  # 5 cm
        self.__speed_of_shot = 4  # 4cm/second

    def smg(self):
        self.__distance = 3  # 10 cm
        self.__speed_of_shot = 6  # 6 cm/second


class Objects(Main_player):
    def __init__(self):
        self.__time = 0  # how much time the object will be activate
        self.__speed_of_player = 0

    def shield(self):
        self.__time = 4  # 4 seconds

    def increase_speed(self):
        pass
