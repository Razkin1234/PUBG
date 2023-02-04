# ====================================================PROTOCOL===================================================================================|                                                                                                                |
# * It's a textual protocol                                                                                                                      |
# * The protocol uses encapsulation of type utf-8 (to decode and encode)                                                                         |
#                                                                                                                                                |
# * Rotshild packets's layers will be: IP()/UDP()/Raw()                                                                                          |
#                                                                                                                                                |
# structure - 'Rotshild <ID>/r/n/r/n<headers>End'                                                                                                |
# [ID - an int (from 1 on) that each client gets from the server at the beginning of the connection. Server's ID is 0]                           |
# [each header looks like this: 'header_name: header_info\r\n' . except of the last one - its without '\r\n']                                    |
#                                                                                                                                                |
# ------------------------------------------------------------------                                                                             |
# The full packet looks like this:                                                                                                               |
#                                    "Rotshild ID\r\n                                                                                            |
#                                     \r\n                                                                                                       |
#                                     header_name: header_info\r\n                                                                               |
#                                     header_name: header_info\r\n                                                                               |
#                                     header_name: header_info\r\n                                                                               |
#                                     .                                                                                                          |
#                                     .                                                                                                          |
#                                     ."                                                                                                         |
# ------------------------------------------------------------------                                                                             |
#                                                                                                                                                |
# ------------------------------------------------------------------                                                                             |
# Headers API:                                                                                                                                   |
#             - login_request: [user_name],[password]                                                                  [only clients sends]      |
#             - login_status: fail [if user name doesn't exist in database or wrong password] or [the ID given to him] [only server sends]       |
#             - register_request: [user name]                                                                          [only clients sends]      |
#             - register_status: taken [if the user name already exists] or success [if registered successfully]       [only server sends]       |
#             - player_place: ([the X coordinate],[the Y coordinate]) [when server sends comes with moved_player_id    [clients and server send] |
#             - moved_player_id: [the ID of the player who moved] [comes with player_place]                            [only server sends]       |
#             - image_of_the_player: [the image of the player who moved] [comes with player_place]                     [clients and server send] |
#             - shot_place: ([the X coordinate],[the Y coordinate]) [comes with hit_hp]                                [clients and server send] |
#             - hit_id: [the ID of the hitted client] [comes with hit_hp]                                              [only server sends]       |
#             - hit_hp: [the amount of heal points to take from a hitted client] [comes with shot_place or hit_id]     [clients ans server send] |
#             - dead: [the ID of the dead client]                                                                      [clients ans server send] |
# ------------------------------------------------------------------                                                                             |
# ===============================================================================================================================================|

import sqlite3
import threading
from scapy.all import *
from scapy.layers.inet import IP, UDP


DEFAULT_WEAPONS = 'stick'
DEFAULT_AMMO = 0
DEFAULT_BOMBS = 0
DEFAULT_MED_KITS = 0
DEFAULT_BACKPACK = 0
DEFAULT_ENERGY_DRINKS = 0
DEFAULT_EXP = 0
DEFAULT_ENERGY = 0

db_connection = None    # The connection with the SQLite RDB
cursor = None   # Cursor object to execute SQL commends on the server DB

thread_list = []  # list of threads
CLIENTS_IP_PORT_ID_USERNAME = []  # IPs, PORTs, IDs AND USER_NAMES of all clients as (ID, IP, PORT, USER_NAME)
PLAYER_PLACES_BY_ID = {}  # Places of all clients by IDs as ID:(X,Y)
ROTSHILD_OPENING_OF_SERVER_PACKETS = 'Rotshild 0\r\n\r\n'  # Opening for the server's packets (after this are the headers)


def intialize_sqlite_rdb():
    global db_connection, cursor

    db_connection = sqlite3.connect("Server_DB.db")  # connect to the db file or create a new one if doesn't exist
    cursor = db_connection.cursor()  # creating a cursor object to execute SQL commends
    cursor.execute("CREATE TABLE IF NOT EXISTS clients_info"    # creating a table of clients data if not exists yet
                   " (user_name TEXT PRIMARY KEY,"
                   " password TEXT,"
                   " weapons TEXT,"  # NOTE: to store separated by ',' like - 'sniper,AR,sword' [options are - stick,sniper,AR,sword]
                   " ammo INTEGER,"
                   " bombs INTEGER,"
                   " med_kits INTEGER,"
                   " backpack INTEGER,"
                   " energy_drinks INTEGER,"
                   " exp INTEGER,"
                   " energy INTEGER")


def handle_login_request(user_name, password, client_ip, client_port):
    """
    Checking if the user_name exist and matches its password in the DB. if yes giving ID.
    :param user_name: <Sting> the user name entered in the login request
    :param password: <String> the password entered in the login request
    :param client_ip: <String> the IP of the client
    :param client_port <String> the port of the client
    :return: <String> login_status header. (if matches then the given ID, if not then 'fail').
    """

    global cursor

    cursor.execute(f"SELECT * FROM clients_info WHERE user_name='{user_name}'")
    result = cursor.fetchone()
    if result is None:
        # user name does not exist in DB
        return 'login_status: fail'
    elif result[1] == password:
        # user name exists in DB and matches the password
        return 'login_status: ' + create_new_id((client_ip, client_port))
    else:
        # user name exists but password doesn't match
        return 'login_status: fail'



def create_new_id(client_ip_port):
    """
    Creating a new ID for a client, saving it with its IP and PORT in the CLIENTS_IP_PORT_ID list, and returning it.
    :param client_ip_port: <Tuple> the ip and port of the new client as (IP,PORT)
    :return: <String> the ID given to the client
    """

    global CLIENTS_IP_PORT_ID_USERNAME

    # checking if the list is empty
    if not CLIENTS_IP_PORT_ID_USERNAME:
        # giving ID = 1
        CLIENTS_IP_PORT_ID_USERNAME.append(('1', client_ip_port[0], client_ip_port[1]))
        return '1'

    last_id = 0  # the last id we know we have
    found = False
    while found is False:  # Running till a free id found
        last_id += 1  # Checking the next id

        # finding the smallest free id we have
        for client in CLIENTS_IP_PORT_ID_USERNAME:  # Running for each client
            if client[0] == str(last_id):
                # if got here then there is a client with the id in last_id
                break

            # if its the last client in the list
            elif client == CLIENTS_IP_PORT_ID_USERNAME[len(CLIENTS_IP_PORT_ID_USERNAME) - 1]:
                # if got here then there is no client with the id in last_id
                found = True

    # the smallest free ID is in last_id
    CLIENTS_IP_PORT_ID_USERNAME.append((str(last_id), client_ip_port[0], client_ip_port[1]))
    return str(last_id)


def handle_register_request(user_name, password):
    """
    Checking if user_name already taken. if not adds it to the DB with his password and gives default weapons, objects and skills.
    :param user_name: <String> the user name entered in the register request
    :param password: <String> the password entered in the register request
    :return: <String> register_status header. (if taken - 'taken', if free - 'success').
    """

    global db_connection, cursor, DEFAULT_WEAPONS, DEFAULT_AMMO, DEFAULT_BOMBS, DEFAULT_MED_KITS, DEFAULT_BACKPACK, DEFAULT_ENERGY_DRINKS, DEFAULT_EXP, DEFAULT_ENERGY

    cursor.execute(f"SELECT * FROM clients_info WHERE user_name='{user_name}'")
    result = cursor.fetchone()
    if result is not None:
        # user name is taken
        return 'register_status: taken'

    # user name is free. saving it to the DB
    new_client = (f'{user_name}',
                  f'{password}',
                  f'{DEFAULT_WEAPONS}',
                  DEFAULT_AMMO,
                  DEFAULT_BOMBS,
                  DEFAULT_MED_KITS,
                  DEFAULT_BACKPACK,
                  DEFAULT_ENERGY_DRINKS,
                  DEFAULT_EXP,
                  DEFAULT_ENERGY)
    cursor.execute("INSERT INTO clients_info"
                   " (user_name,"
                   " password,"
                   " weapons,"
                   " ammo,"
                   " bombs,"
                   " med_kits,"
                   " backpack,"
                   " energy_drinks,"
                   " exp,"
                   " energy)"
                   " VALUES (?,?,?,?,?,?,?,?,?,?)", new_client)
    db_connection.commit()

    return 'register_status: success'


def handle_shot_place(shot_place, hp):
    """
    Checking if the shot hit a client.
    if no - informing all clients about where the shot is,
    if yes - informing all clients there was a hit (so they stop showing the shot) and the ID of the hitted one (so he knows to take down hp), and how much hp to take off
    :param shot_place: <String> the place of the shot as tuple (X,Y)
    :param hp: <String> the amount of heal point the shot takes down if hit
    """
    global PLAYER_PLACES_BY_ID, CLIENTS_IP_PORT_ID_USERNAME, ROTSHILD_OPENING_OF_SERVER_PACKETS
    # checking if one of the players got hit
    for (player_id, player_place) in PLAYER_PLACES_BY_ID.items():
        # checking the x place
        if player_place[0] == shot_place[0]:
            # checking the t place
            if player_place[1] == shot_place[1]:
                # looking for the ip and port of the player who got hit
                for client in CLIENTS_IP_PORT_ID_USERNAME:
                    if client[0] == player_id:
                        # he got hit and telling him how many to decrease
                        send(IP(dst=client[1]) / UDP(dport=client[2]) / Raw(
                            (ROTSHILD_OPENING_OF_SERVER_PACKETS + 'hit_hp: ' + hp).encode('utf-8')))
                        return
    # no one got hit so sending to all the clients the shot place
    # when the client gets shots place he prints it and after that he doesnt care
    return 'shot_place: ' + shot_place


def handle_dead(dead_id):
    """
    Deleting the dead client from PLAYER_PLACES_BY_ID dict and from the CLIENTS_IP_PORT_ID list,
    and informing all clients that a player died with sending them his ID.
    :param dead_id: <String> the ID of the dead client
    """

    global CLIENTS_IP_PORT_ID_USERNAME, PLAYER_PLACES_BY_ID

    # Deleting the dead client from the PLAYER_PLACES_BY_ID dict
    if dead_id in PLAYER_PLACES_BY_ID:
        del PLAYER_PLACES_BY_ID[dead_id]

    # Deleting the dead client from the CLIENTS_IP_PORT_ID list
    for client_addr in CLIENTS_IP_PORT_ID_USERNAME:
        if client_addr[0] == dead_id:  # client_addr[0] == the ID of the client
            CLIENTS_IP_PORT_ID_USERNAME.remove(client_addr)
            break

    # Sending to all clients that someone died and his ID
    return 'dead: ' + dead_id


def handle_player_place(place, id, image):
    """
    Updates the place of the player at the dict PLAYER_PLACES_BY_ID,
    and sending to all clients the new place, the ID of the player who moved and his image.
    :param image:
    :param place: <String> the place of the player as tuple (IP,PORT)
    :param id: <String> the ID of the player
    """

    global CLIENTS_IP_PORT_ID_USERNAME, PLAYER_PLACES_BY_ID

    # Updates the dict at the server with the new place by the ID
    PLAYER_PLACES_BY_ID[id] = place

    # Builds Raw layer of Rotshild protocol for the packet to send
    return 'player_place: {}\r\nmoved_player_id: {}\r\nimage_of_the_player: {}'.format(place, id, image)
    # Sends the packet to all clients


def recognizing_headers(Rotshild):
    """
    Recognizing the different headers and calling to the specific header handler for each one.
    :param Rotshild: <String> the Rotshild layer of the packet
    """
    global CLIENTS_IP_PORT_ID_USERNAME, ROTSHILD_OPENING_OF_SERVER_PACKETS
    lines = Rotshild.split('\r\n')
    for line in lines:
        line_parts = line.split()  # in the opening line it will be - ['Rotshild',ID], and in the headers - [header_name, info]
        # Recognize and handle each header
        if line_parts[0] == 'login_request:':
            user_name, password = line_parts[1].split(',')
            answer_for_login_request = handle_login_request(user_name, password, Rotshild[IP].src, Rotshild[UDP].sport)
        elif line_parts[0] == 'register_request:':
            answer_for_register_request = handle_register_request(line_parts[1], Rotshild[IP].src, Rotshild[UDP].sport)
            send(IP(dst=Rotshild[IP].src) / UDP(dport=Rotshild[UDP].sport) / Raw(
                (ROTSHILD_OPENING_OF_SERVER_PACKETS + answer_for_register_request).encode('utf-8')))
            break
        elif line_parts[0] == 'player_place:':
            # looking for image_of_the_player header
            for l in lines:
                l_parts = l.split()
                if l_parts[0] == 'image_of_the_player:':
                    answer_for_player_place = handle_player_place(tuple(line_parts[1]),
                                                                  lines[0].split()[1],
                                                                  l_parts[1])  # line_parts[0].split()[1]) == src client's ID and l_parts[1] == image_of_the_player
                    break

        elif line_parts[0] == 'shot_place:':
            # looking for the hit_hp header
            for l in lines:
                l_parts = l.split()  # in the opening line it will be - ['Rotshild',ID], and in the headers - [header_name, info]
                if l_parts[0] == 'hit_hp:':
                    answer_for_shot_place = handle_shot_place(line_parts[1], l_parts[1])
                    break

        if line_parts[0] == 'dead:':
            answer_for_dead = handle_dead(line_parts[1])

    for addr in CLIENTS_IP_PORT_ID_USERNAME:
        send(IP(dst=addr[1]) / UDP(dport=addr[2]) / Raw((ROTSHILD_OPENING_OF_SERVER_PACKETS +
                                                         answer_for_player_place + '\r\n'
                                                         + answer_for_shot_place + '\r\n'
                                                         + answer_for_dead).encode('utf-8')))


def Rotshild_filter(packet):
    """
    Checking if a packet is of our protocol 'Rotshild'.
    :param packet: <Packet> sniffed packet to check
    :return: <Boolean> True - passed the filter, False - didn't pass the filter
    """

    if not UDP in packet or not Raw in packet:
        return False
    if packet[UDP].sport != 555 or packet[UDP].dport != 555:
        return False
    print(packet)
    try:
        packet[Raw].decode()
    except AttributeError:
        return False

    parts = packet[Raw].decode('utf-8').split()
    print(packet)
    return parts[0] == 'Rotshild'


def decode_raw(packet):
    decoded_packet = packet[Raw].decode('utf-8')
    return decoded_packet


def create_threads(packet):
    parts = packet[Raw].decode('utf-8').split()
    packet = parts[0]
    threading.Thread(target=recognizing_headers, args=(packet,)).start()  # creating thread


def main():
    global cursor
    try:
        intialize_sqlite_rdb()

        while True:
            packets = sniff(count=1, lfilter=Rotshild_filter, prn=create_threads)

    except Exception as ex:
        print(f'something went wrong... : {ex}\n')

    finally:
        db_connection.close()   # NOTE: remember doing this in each place where the script might end!


if __name__ == '__main__':
    main()
