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
#             - register_request: [user name],[password]                                                               [only clients sends]      |
#             - register_status: taken [if the user name already exists] or success [if registered successfully]       [only server sends]       |
#             - player_place: ([the X coordinate],[the Y coordinate]) [when server sends comes with moved_player_id    [clients and server send] |
#             - moved_player_id: [the ID of the player who moved] [comes with player_place]                            [only server sends]       |
#             - image: [the name of the file with the image of the player who moved] [comes with player_place]         [clients and server send] |
#             - shot_place: ([the X coordinate],[the Y coordinate]) [when client sends comes with hit_hp]              [clients and server send] |
#             - hit_id: [the ID of the hitted client] [comes with hit_hp]                                              [only server sends]       |
#             - hit_hp: [the amount of heal points to take from a hitted client] [comes with shot_place or hit_id]     [clients ans server send] |
#             - dead: [the ID of the dead client]                                                                      [clients ans server send] |
# ------------------------------------------------------------------                                                                             |
# ===============================================================================================================================================|

import sqlite3
import threading
from scapy.all import *
from scapy.layers.inet import IP, UDP


# ------------------------ Default DB values of a new client
DEFAULT_WEAPONS = 'stick'
DEFAULT_AMMO = 0
DEFAULT_BOMBS = 0
DEFAULT_MED_KITS = 0
DEFAULT_BACKPACK = 0
DEFAULT_ENERGY_DRINKS = 0
DEFAULT_EXP = 0
DEFAULT_ENERGY = 0
# ------------------------

# ------------------------ SQLite DateBase objects
DB_CONNECTION = None    # The connection with the SQLite RDB
CURSOR = None   # Cursor object to execute SQL commends on the DB
# ------------------------

# ------------------------ General
THREAD_LIST = []  # list of threads
CLIENTS_ID_IP_PORT = []  # IPs, PORTs and IDs of all clients as (ID, IP, PORT)      [ID, IP and PORT are str]
PLAYER_PLACES_BY_ID = {}  # Places of all clients by IDs as ID:(X,Y)        [ID, X and Y are str]
ROTSHILD_OPENING_OF_SERVER_PACKETS = 'Rotshild 0\r\n\r\n'  # Opening for server's packets (after this are the headers)
# -------------------------


def intialize_sqlite_rdb():
    """
    Connecting to the DataBase ('Server_DB.db') or creating a new one if doesn't exist,
    Creating a cursor object for the DB to execute SQLite commends on it,
    Creating a table of clients_info (if doesn't exist).
    """

    global DB_CONNECTION, CURSOR

    DB_CONNECTION = sqlite3.connect("Server_DB.db")  # connect to the db file or create a new one if doesn't exist
    CURSOR = DB_CONNECTION.cursor()  # creating a cursor object to execute SQL commends
    CURSOR.execute("CREATE TABLE IF NOT EXISTS clients_info"    # creating a table of clients data if not exists yet
                   " (user_name TEXT PRIMARY KEY,"
                   " password TEXT,"
                   " weapons TEXT,"  # to store separated by ',' like- 'sniper,AR,sword' [can be: stick,sniper,AR,sword]
                   " ammo INTEGER,"
                   " bombs INTEGER,"
                   " med_kits INTEGER,"
                   " backpack INTEGER,"
                   " energy_drinks INTEGER,"
                   " exp INTEGER,"
                   " energy INTEGER)")


def handle_login_request(user_name: str, password: str, client_ip: str, client_port: str) -> str:
    """
    Checking if the user_name exists and matches its password in the DB. if yes giving ID.
    :param user_name: <Sting> the user name entered in the login request.
    :param password: <String> the password entered in the login request.
    :param client_ip: <String> the IP of the client.
    :param client_port <String> the port of the client.
    :return: <String> login_status header. (if matches then the given ID, if not then 'fail').
    """

    global CURSOR

    CURSOR.execute(f"SELECT * FROM clients_info WHERE user_name='{user_name}'")
    result = CURSOR.fetchone()
    if not result:
        # user name does not exist in DB
        return 'login_status: fail\r\n'
    elif result[1] == password:
        # user name exists in DB and matches the password
        return 'login_status: ' + create_new_id((client_ip, client_port)) + '\r\n'
    else:
        # user name exists but password doesn't match
        return 'login_status: fail\r\n'


def create_new_id(client_ip_port: tuple) -> str:
    """
    Creating a new ID for a client, saving it with its IP and PORT in the CLIENTS_ID_IP_PORT list, and returning it.
    :param client_ip_port: <Tuple> the IP and PORT of the new client as (IP,PORT).   [IP and PORT are str]
    :return: <String> the ID given to the client.
    """

    global CLIENTS_ID_IP_PORT

    # checking if the list is empty
    if not CLIENTS_ID_IP_PORT:
        # giving ID = 1
        CLIENTS_ID_IP_PORT.append(('1', client_ip_port[0], client_ip_port[1]))
        return '1'

    last_id = 0  # the last active id we know we have at the moment
    found = False   # flag
    while found is False:  # Running till a free id found
        last_id += 1  # Checking the next id

        for client in CLIENTS_ID_IP_PORT:  # Running for each client
            if client[0] == str(last_id):
                # if got here then there is a client with the id in last_id
                break

            # checking if we passed all active clients
            elif client[0] == CLIENTS_ID_IP_PORT[len(CLIENTS_ID_IP_PORT) - 1][0]:
                # if got here then there is no client with the id in last_id
                found = True

    # the smallest free ID is in last_id
    CLIENTS_ID_IP_PORT.append((str(last_id), client_ip_port[0], client_ip_port[1]))
    return str(last_id)


def handle_register_request(user_name: str, password: str) -> str:
    """
    Checking if user_name already taken. if not - adds it to the DB with his password and default values of player data.
    :param user_name: <String> the user name entered in the register request.
    :param password: <String> the password entered in the register request.
    :return: <String> register_status header. (if taken - 'taken', if free - 'success').
    """

    global DB_CONNECTION, CURSOR, DEFAULT_WEAPONS, DEFAULT_AMMO, DEFAULT_BOMBS, DEFAULT_MED_KITS, DEFAULT_BACKPACK, \
        DEFAULT_ENERGY_DRINKS, DEFAULT_EXP, DEFAULT_ENERGY

    CURSOR.execute(f"SELECT * FROM clients_info WHERE user_name='{user_name}'")
    result = CURSOR.fetchone()

    if result:
        # user name is taken
        return 'register_status: taken\r\n'

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
    CURSOR.execute("INSERT INTO clients_info"
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
    DB_CONNECTION.commit()

    return 'register_status: success\r\n'


def handle_shot_place(shot_place: tuple, hp: str) -> str:
    """
    Checking if the shot hit a client.
    if no - building Rotshild headers to inform all clients about where the shot is.
    if yes - building Rotshild headers to inform all clients there was a hit (so they stop showing the shot),
             the ID of the hitted one (so he knows to take down hp), and how much hp to take off.
    :param shot_place: <Tuple> the place of the shot as (X,Y).  [X and Y are str]
    :param hp: <String> the amount of heal point the shot takes down if hit.
    :return: <String> Rotshild headers to describe the shot status.
             if not hit then just shot_place,
             if hit then hit_id and hit_hp.
    """
    global PLAYER_PLACES_BY_ID, CLIENTS_ID_IP_PORT, ROTSHILD_OPENING_OF_SERVER_PACKETS

    # checking if one of the players got hit
    for player_id, player_place in PLAYER_PLACES_BY_ID.items():
        # checking if current client was hitted
        if player_place[0] == shot_place[0] and player_place[1] == shot_place[1]:
            # if got here there was a hit.
            return f'hit_id: {player_id}\r\nhit_hp: {hp}\r\n'

    # if got here then no one got hit so sending to all the clients the shot place
    return f'shot_place: {str(shot_place)}\r\n'


def handle_dead(dead_id: str) -> str:
    """
    Deleting the dead client from PLAYER_PLACES_BY_ID dict and from the CLIENTS_ID_IP_PORT list.
    :param dead_id: <String> the ID of the dead client
    :return: <String> dead header with the ID of the dead client.
    """

    global CLIENTS_ID_IP_PORT, PLAYER_PLACES_BY_ID

    # Deleting the dead client from the PLAYER_PLACES_BY_ID dict
    if dead_id in PLAYER_PLACES_BY_ID:
        del PLAYER_PLACES_BY_ID[dead_id]

    # Deleting the dead client from the CLIENTS_ID_IP_PORT list
    for client_addr in CLIENTS_ID_IP_PORT:
        if client_addr[0] == dead_id:  # client_addr[0] is the ID of the client
            CLIENTS_ID_IP_PORT.remove(client_addr)
            break

    # returning a dead header
    return 'dead: ' + dead_id + '\r\n'


def handle_player_place(place: tuple, id: str, image: str) -> str:
    """
    Updates the place of the player at the dict PLAYER_PLACES_BY_ID.
    :param image: <String> the name of the file with the image of the player(its different between skins and directions)
    :param place: <Tuple> the place of the player as (X,Y).   [X and Y are str]
    :param id: <String> the ID of the player.
    :return: <String> 3 headers - player_place, moved_player_id and image according to the moved player.
    """

    global CLIENTS_ID_IP_PORT, PLAYER_PLACES_BY_ID

    # Updates the dict PLAYER_PLACES_BY_ID with the new place of the player
    PLAYER_PLACES_BY_ID[id] = place

    # returning Rotshild headers with values according to the player's movement
    return 'player_place: {}\r\nmoved_player_id: {}\r\nimage: {}\r\n'.format(str(place), id, image)


def recognizing_headers(rotshild_raw_layer: str, src_ip: str, src_port: str):
    """
    Recognizing the different headers and calling the specific header handler for each one.
    Then taking all the returned values from the handlers (it's header the reply should have) building a reply packet
    and sending it to all clients.
    :param rotshild_raw_layer: <String> the Rotshild layer of the packet (5th layer).
    :param src_ip: <String> the IP of the client who sent the packet.
    :param src_port: <String> the PORT of the client who sent the packet.
    """
    global CLIENTS_ID_IP_PORT, ROTSHILD_OPENING_OF_SERVER_PACKETS

    reply_rotshild_layer = ROTSHILD_OPENING_OF_SERVER_PACKETS
    individual_reply = False    # should the reply for that packet be for an individual client?

    lines = rotshild_raw_layer.split('\r\n')
    for line in lines:
        line_parts = line.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]

        # Recognize and handle each header
        # -------------
        if line_parts[0] == 'login_request:':
            user_name, password = line_parts[1].split(',')
            reply_rotshild_layer += handle_login_request(user_name, password, src_ip, src_port)
            individual_reply = True
            break
        # -------------

        # -------------
        if line_parts[0] == 'register_request:':
            user_name, password = line_parts[1].split(',')
            reply_rotshild_layer += handle_register_request(user_name, password)
            individual_reply = True
            break
        # --------------

        # --------------
        if line_parts[0] == 'player_place:':
            # looking for image header
            for l in lines:
                l_parts = l.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                if l_parts[0] == 'image:':
                    tuple_place = tuple(line_parts[1][1:-1].split(','))  # converting the place from str to tuple
                    reply_rotshild_layer += handle_player_place(tuple_place, lines[0].split()[1], l_parts[1])
                    break
        # --------------

        # --------------
        elif line_parts[0] == 'shot_place:':
            # looking for the hit_hp header
            for l in lines:
                l_parts = l.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                if l_parts[0] == 'hit_hp:':
                    tuple_place = tuple(line_parts[1][1:-1].split(','))  # converting the place from str to tuple
                    reply_rotshild_layer += handle_shot_place(tuple_place, l_parts[1])
                    break
        # --------------

        # --------------
        elif line_parts[0] == 'dead:':
            reply_rotshild_layer += handle_dead(line_parts[1])
        # --------------

    if not individual_reply:
        # sending the reply to all active clients
        for client in CLIENTS_ID_IP_PORT:
            send(IP(dst=client[1]) / UDP(dport=client[2]) / Raw(reply_rotshild_layer.encode('utf-8')))

    else:
        # sending the reply to the specific client
        send(IP(dst=src_ip) / UDP(dport=src_port) / Raw(reply_rotshild_layer.encode('utf-8')))


def rotshild_filter(packet: Packet) -> bool:
    """
    Checking if a packet is of our 5th layer protocol - 'Rotshild'.
    :param packet: <Packet> sniffed packet to check.
    :return: <Boolean> True - passed the filter, False - didn't pass the filter
    """

    if UDP not in packet or Raw not in packet:
        return False
    payload = packet[Raw].load
    expected = 'Rotshild'.encode('utf-8')
    return payload[:len(expected)] == expected


def create_threads(packet):
    parts = packet[Raw].decode('utf-8').split()
    packet = parts[0]
    threading.Thread(target=recognizing_headers, args=(packet,)).start()  # creating thread


def main():
    global CURSOR
    try:
        intialize_sqlite_rdb()  # building connection and initialization of the SQL (SQLite) server

        while True:
            packets = sniff(count=1, lfilter=rotshild_filter, prn=create_threads)

    except Exception as ex:
        print(f'something went wrong... : {ex}\n')

    finally:
        DB_CONNECTION.close()   # NOTE: remember doing this in each place where the script might end!!!


# --------------------------- Main Guard
if __name__ == '__main__':
    main()
# ---------------------------
