"""
====================================================PROTOCOL=================================================================================================|                                                                                                                |
* It's a textual protocol                                                                                                                                    |
* The protocol uses encapsulation of type utf-8 (to decode and encode)                                                                                       |
                                                                                                                                                             |
* Rotshild packets's layers will be: IP()/UDP()/Raw()                                                                                                        |
                                                                                                                                                             |
structure - 'Rotshild <ID>/r/n/r/n<headers>'                                                                                                                 |
[ID - an int (from 1 on) that each client gets from the server at the beginning of the connection. Server's ID is 0. at register request there is no ID]     |
[each header looks like this: 'header_name: header_info\r\n' . except of the last one - its without '\r\n']                                                  |
                                                                                                                                                             |
------------------------------------------------------------------                                                                                           |
The full packet looks like this:                                                                                                                             |
                                   "Rotshild ID\r\n                                                                                                          |
                                    \r\n                                                                                                                     |
                                    header_name: header_info\r\n                                                                                             |
                                    header_name: header_info\r\n                                                                                             |
                                    header_name: header_info\r\n                                                                                             |
                                    .                                                                                                                        |
                                    .                                                                                                                        |
                                    ."                                                                                                                       |
------------------------------------------------------------------                                                                                           |
                                                                                                                                                             |
------------------------------------------------------------------                                                                                           |
Headers API:                                                                                                                                                 |
            - login_request: [user_name],[password]                                                                                [only clients send]       |
            - login_status: fail [if user name doesn't exist in database or wrong password] or [the ID given to him]               [only server sends]       |
            - register_request: [user name],[password]                                                                             [only clients send]       |
            - register_status: taken [if the user name already exists] or success  or invalid                                      [only server sends]       |
            - inventory_update: [can be only one, or a few of the options below, you should separate them by ',']                  [only clients send]       |
                                 + weapons [weapon name]                                                                                                     |
                                 - weapons [weapon name]                                                                                                     |
                                 + ammo [how much?]                                                                                                          |
                                 - ammo [how much?]                                                                                                          |
                                 + bombs [how much?]                                                                                                         |
                                 - bombs [how much?]                                                                                                         |
                                 + med_kits [how much?]                                                                                                      |
                                 - med_kits [how much?]                                                                                                      |
                                 + backpack [how much?]                                                                                                      |
                                 - backpack [how much?]                                                                                                      |
                                 + energy_drinks [how much?]                                                                                                 |
                                 - energy_drinks [how much?]                                                                                                 |
                                 + coins [how much?]                                                                                                         |
                                 - coins [how much?]                                                                                                         |
                                 + exp [how much?]                                                                                                           |
                                 - exp [how much?]                                                                                                           |
                                 + energy [how much?]                                                                                                        |
                                 - energy [how much?]                                                                                                        |
              [comes with user_name]                                                                                                                         |
            - user_name: [user_name]  [comes with inventory_update or chat or dead]                                                [clients and server send] |
            - player_place: ([the X coordinate],[the Y coordinate]) [when server sends comes with moved_player_id                  [clients and server send] |
            - moved_player_id: [the ID of the player who moved] [comes with player_place]                                          [only server sends]       |
            - image: [the name of the file with the image of the player who moved] [comes with player_place]                       [clients and server send] |
            - shot_place: ([the X coordinate],[the Y coordinate]) [when client sends comes with hit_hp]                            [clients and server send] |
            - hit_id: [the ID of the hitted client] [comes with hit_hp and shooter_id]                                             [only server sends]       |
            - hit_hp: [the amount of heal points to take from a hitted client] [comes with shot_place or hit_id and shooter_id]    [clients ans server send] |
            - shooter_id: [the ID of the client who shoot the shot] [comes with hit_id and hit_hp]                                 [only server sends]       |
            - dead: [the ID of the dead client]  [comes with user_name]                                                            [clients ans server send] |
            - chat: [the info of the message]  [comes with user_name]                                                              [clients and server send] |
            - server_shutdown: by_user [if closed by the user] or error [if closed because of an error]                            [only server sends]       |
------------------------------------------------------------------                                                                                           |
=============================================================================================================================================================|
"""


import os
import sqlite3
import public_ip
from concurrent.futures import ThreadPoolExecutor
import threading
from socket import socket, AF_INET, SOCK_DGRAM, timeout as socket_timeout
import rsa
from rsa.key import PublicKey, PrivateKey
from prettytable import PrettyTable

# ------------------------ socket
SERVER_UDP_PORT = 56789
SERVER_IP = '0.0.0.0'
SOCKET_BUFFER_SIZE = 1024
SERVER_SOCKET_TIMEOUT = 10  # to prevent permanent blocking while not getting any input for a while and still enable to
# check the main loop trigger event sometimes.
# The bigger you'll set this timeout - you will check the trigger event less often,
# but your chances of losing packets are smaller.
# ------------------------

# ------------------------ Default DB values of a new client
DEFAULT_WEAPONS = 'stick'
DEFAULT_AMMO = 0
DEFAULT_BOMBS = 0
DEFAULT_MED_KITS = 0
DEFAULT_BACKPACK = 0
DEFAULT_ENERGY_DRINKS = 0
DEFAULT_COINS = 0
DEFAULT_EXP = 0
DEFAULT_ENERGY = 0
# ------------------------


# ------------------------ Files path
SCRIPT_PATH = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
DB_FILE = "Server_DB.db"
DB_PATH = os.path.join(SCRIPT_DIR, DB_FILE)
# ------------------------


# ------------------------ General
SHUTDOWN_TRIGGER_EVENT = threading.Event()  # A trigger event to shut down the server
MAX_WORKER_THREADS = 10  # The max amount of running worker threads.
# (larger amount mean faster client handling and able to handle more clients,
# but a big amount that is not match to your CPU will just waste important system resources and wont help)
CLIENTS_ID_IP_PORT = []  # IPs, PORTs and IDs of all clients as (ID, IP, PORT)      [ID, IP and PORT are str]
PLAYER_PLACES_BY_ID = {}  # Places of all clients by IDs as ID:(X,Y)        [ID, X and Y are str]
ROTSHILD_OPENING_OF_SERVER_PACKETS = 'Rotshild 0\r\n\r\n'  # Opening for server's packets (after this are the headers)
# -------------------------

# ------------------------- RSA deterministic asymmetric encryption
"""
The key generation proccess:
    - generate two large prime numbers, known as the first and second prime factors.
    - These prime factors are used to calculate the modulus, which is used in the modular arithmetic of RSA encryption.
    - The public exponent is selected, which is usually 65537 in modern RSA implementations.
    - The private exponent is calculated based on the public exponent and the totient of the modulus.
      (totient is the number of positive integers less than or equal to a given integer,
       in the RSA case it is calculated as (first prime factor - 1) * (second prime factor - 1)).

* The key generation process is designed to ensure that it is computationally infeasible to determine the private key
  from the public key, even if an attacker has access to both the public and private exponents.

The encryption process works as follows:
(using the public key - contains the modulus and the public exponent)
    - A plaintext message is transformed into a numerical value.
    - The numerical value is raised to the power of the public exponent (modulo the modulus) to produce the ciphertext
      (ciphertext = plaintext ** public_exponent % modulus).

The decryption process works as follows:
(using the private key - contains the modulus, the private exponent and the two prime factors)
    - A ciphertext is raised to the power of the private exponent (modulo the modulus) to produce the plaintext
    (plaintext = ciphertext ** private_exponent % modulus).
    - The recipient then obtains the original message by transforming the plaintext back to its original form.
"""

MODULUS = 7202380422720360875138943832989169827593337421340517606000697629974789073279088263129156773084889735203215777657443638346916570347919877966671239593821849  # (not secret)
PUBLIC_EXPONENT = 65537  # (not secret)
PRIVATE_EXPONENT = 2487759366909086609556743084782273179840859044614268230877791053141573463839494045756198356306801278556401491488506285362190686031132636395114287646477909  # (secret)
FIRST_PRIME_FACTOR = 6722171653111129608666978173114450112621458860424439037672507726695639042339185147  # (secret)
SECOND_PRIME_FACTOR = 1071436552707930761066064576213162123693476737940140711087853990359411067  # (secret)

PUBLIC_KEY = PublicKey(MODULUS, PUBLIC_EXPONENT)  # (not secret)
PRIVATE_KEY = PrivateKey(MODULUS, PUBLIC_EXPONENT, PRIVATE_EXPONENT, FIRST_PRIME_FACTOR, SECOND_PRIME_FACTOR)  # (secret)
# -------------------------


def handle_update_inventory(header_info: str, user_name: str, connector, cursor):
    """
    updating the inventory of a client in the DB
    :param header_info: <String> all the raw info in the update_inventory header.
    :param user_name: <String> the user name of the client (get from the user_name header).
    :param connector: the connection object to the DB.
    :param cursor: the cursor object to the DB.
    """

    updates = header_info.split(',')
    # handle each inventory update
    for update in updates:
        operation, column, info = update.split()
        if column != 'weapons':
            cursor.execute(f"UPDATE clients_info"
                           f" SET {column} = {column} {operation} {info}"
                           f" WHERE user_name = '{user_name}'")
        else:
            if operation == '+':
                cursor.execute(f"UPDATE clients_info SET weapons = weapons + ',{info}' WHERE user_name = '{user_name}'")
            else:
                cursor.execute(f"SELECT weapons FROM clients_info WHERE user_name = '{user_name}'")
                result = cursor.fetchone()
                client_weapons = result[0].split(',')
                updated_weapons = []
                for weapon in client_weapons:
                    if weapon != info:
                        updated_weapons.append(weapon)
                updated_weapons = ','.join(updated_weapons)
                cursor.execute(f"UPDATE clients_info SET weapons = '{updated_weapons}' WHERE user_name = '{user_name}'")
    connector.commit()


def handle_login_request(user_name: str, password: str, client_ip: str, client_port: str, cursor) -> str:
    """
    Checking if the user_name exists and matches its password in the DB. if yes giving ID.
    :param user_name: <Sting> the user name entered in the login request.
    :param password: <String> the password entered in the login request.
    :param client_ip: <String> the IP of the client.
    :param client_port <String> the port of the client.
    :param cursor: the cursor object to the DB.
    :return: <String> login_status header. (if matches then the given ID, if not then 'fail').
    """

    global CLIENTS_ID_IP_PORT

    if ' ' in user_name or ' ' in password:
        # user name and password can not contain spaces
        return 'login_status: fail\r\n'

    cursor.execute(f"SELECT * FROM clients_info WHERE user_name = '{user_name}'")
    result = cursor.fetchone()
    if not result:
        # user name does not exist in DB
        return 'login_status: fail\r\n'
    elif result[1] == password:
        # user name exists in DB and matches the password
        given_id = create_new_id((client_ip, client_port))
        print(f'>> New client connected to the game server.\n'
              f'   User Name - {user_name}\n'
              f'   User game ID - {given_id}\n'
              f'   User IPv4 addr - {client_ip}\n'
              f'   User port number - {client_port}\n'
              f'   Number of active players on server - {str(len(CLIENTS_ID_IP_PORT))}')
        return 'login_status: ' + given_id + '\r\n'
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
    found = False  # flag
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


def handle_register_request(user_name: str, password: str, connector, cursor) -> str:
    """
    Checking if user_name already taken. if not - adds it to the DB with his password and default values of player data.
    :param user_name: <String> the user name entered in the register request.
    :param password: <String> the password entered in the register request.
    :param connector: the connection object to the DB.
    :param cursor: the cursor object to the DB.
    :return: <String> register_status header. (if taken - 'taken', if free - 'success', if invalid - 'invalid').
    """

    global DEFAULT_WEAPONS, DEFAULT_AMMO, DEFAULT_BOMBS, DEFAULT_MED_KITS, DEFAULT_BACKPACK, \
        DEFAULT_ENERGY_DRINKS, DEFAULT_COINS, DEFAULT_EXP, DEFAULT_ENERGY

    if ' ' in user_name or ' ' in password:
        # user name and password can not contain spaces
        return 'register_status: invalid\r\n'

    cursor.execute(f"SELECT * FROM clients_info WHERE user_name=?", (user_name,))
    result = cursor.fetchone()

    if result:
        # user name is taken
        return 'register_status: taken\r\n'

    # user name is free. saving it to the DB
    new_client = (user_name,
                  password,
                  DEFAULT_WEAPONS,
                  DEFAULT_AMMO,
                  DEFAULT_BOMBS,
                  DEFAULT_MED_KITS,
                  DEFAULT_BACKPACK,
                  DEFAULT_ENERGY_DRINKS,
                  DEFAULT_COINS,
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
                   " coins,"
                   " exp,"
                   " energy)"
                   " VALUES (?,?,?,?,?,?,?,?,?,?,?)", new_client)
    connector.commit()

    print(f'>> New client registered to server. User Name: {user_name}.')
    return 'register_status: success\r\n'


def handle_shot_place(shot_place: tuple, hp: str, shooter_id: str) -> str:
    """
    Checking if the shot hit a client.
    if no - building Rotshild headers to inform all clients about where the shot is,
            and who is the shooter (so he knows not to print the shot again).
    if yes - building Rotshild headers to inform all clients there was a hit (so they stop showing the shot),
             the ID of the hitted one (so he knows to take down hp), how much hp to take off,
             and the ID of the shooter (so he knows to increase exp).
    :param shot_place: <Tuple> the place of the shot as (X,Y).  [X and Y are str]
    :param hp: <String> the amount of heal point the shot takes down if hit.
    :param shooter_id: <String> the ID of the shooter client.
    :return: <String> Rotshild headers to describe the shot status.
             if not hit then shot_place and shooter_id.
             if hit then hit_id and hit_hp and shooter_id.
    """
    global PLAYER_PLACES_BY_ID, CLIENTS_ID_IP_PORT, ROTSHILD_OPENING_OF_SERVER_PACKETS

    # checking if one of the players got hit
    for player_id, player_place in PLAYER_PLACES_BY_ID.items():
        # checking if current client was hitted
        if player_place[0] == shot_place[0] and player_place[1] == shot_place[1]:
            # if got here there was a hit.
            return f'hit_id: {player_id}\r\nhit_hp: {hp}\r\nshooter_id: {shooter_id}\r\n'

    # if got here then no one got hit so sending to all the clients the shot place and the shooter ID
    return f'shot_place: {str(shot_place)}\r\nshooter_id: {shooter_id}\r\n'


def handle_dead(dead_id: str, user_name: str, connector, cursor) -> str:
    """
    Deleting the dead client from PLAYER_PLACES_BY_ID dict and from the CLIENTS_ID_IP_PORT list,
    and initializing the inventory (the DB values but for user_name, password and coins) to default.
    :param dead_id: <String> the ID of the dead client
    :param user_name: <String> the uesr name of the dead client.
    :param connector: the connection object to the DB.
    :param cursor: the cursor object to the DB.
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

    # Initializing the inventory (the DB values but for user_name, password and coins) to default
    client_update = (DEFAULT_WEAPONS,
                     DEFAULT_AMMO,
                     DEFAULT_BOMBS,
                     DEFAULT_MED_KITS,
                     DEFAULT_BACKPACK,
                     DEFAULT_ENERGY_DRINKS,
                     DEFAULT_EXP,
                     DEFAULT_ENERGY)
    cursor.execute("UPDATE clients_info"
                   " SET weapons = ?,"
                   " ammo = ?,"
                   " bombs = ?,"
                   " med_kits = ?,"
                   " backpack = ?,"
                   " energy_drinks = ?,"
                   " exp = ?,"
                   " energy = ?"
                   " WHERE user_name = ?", client_update + (user_name,))
    connector.commit()

    # returning a dead header
    print(f'>> Client died and disconnected from game server.\n'
          f'   Dead client ID - {dead_id}\n'
          f'   Number of active players on server - {str(len(CLIENTS_ID_IP_PORT))}')
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


def packet_handler(rotshild_raw_layer: str, src_ip: str, src_port: str, server_socket: socket):
    """
    Recognizing the different headers and calling the specific header handler for each one.
    Then taking all the returned values from the handlers (it's header the reply should have) building a reply,
    encrypting it, and sending it to all clients.
    :param rotshild_raw_layer: <String> the Rotshild layer of the packet (5th layer).
    :param src_ip: <String> the IP of the client who sent the packet.
    :param src_port: <String> the PORT of the client who sent the packet.
    :param server_socket: <Socket> the server's socket object.
    """

    global CLIENTS_ID_IP_PORT, ROTSHILD_OPENING_OF_SERVER_PACKETS, PUBLIC_KEY

    reply_rotshild_layer = ROTSHILD_OPENING_OF_SERVER_PACKETS
    connector = None  # connection object to DB
    cursor = None  # cursor object to DB
    individual_reply = False  # should the reply for that packet be for an individual client?
    user_name_cache = ''  # saving the user_name header info after found ones (to prevent more scans to find it later)

    lines = rotshild_raw_layer.split('\r\n')
    lines.remove('')
    for line in lines:
        line_parts = line.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]

        # Recognize and handle each header
        # -------------
        if line_parts[0] == 'login_request:':
            # open db connector and cursor if not open already
            if not (connector and cursor):
                connector, cursor = connect_to_db_and_build_cursor()
            user_name, password = line_parts[1].split(',')
            reply_rotshild_layer += handle_login_request(user_name, password, src_ip, src_port, cursor)
            individual_reply = True
            break
        # -------------

        # -------------
        if line_parts[0] == 'register_request:':
            # open db connector and cursor if not open already
            if not (connector and cursor):
                connector, cursor = connect_to_db_and_build_cursor()
            user_name, password = line_parts[1].split(',')
            reply_rotshild_layer += handle_register_request(user_name, password, connector, cursor)
            individual_reply = True
            break
        # --------------

        # --------------
        # in this header clients should check the moved_player_id so they wont print their own movement twice.
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
        # in this header clients should check the shooter_id so they wont print their own shot twice (if don't hit)
        elif line_parts[0] == 'shot_place:':
            # looking for the hit_hp header
            for l in lines:
                l_parts = l.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                if l_parts[0] == 'hit_hp:':
                    tuple_place = tuple(line_parts[1][1:-1].split(','))  # converting the place from str to tuple
                    reply_rotshild_layer += handle_shot_place(tuple_place, l_parts[1], lines[0].split()[1])
                    break
        # --------------

        # --------------
        elif line_parts[0] == 'dead:':
            # open db connector and cursor if not open already
            if not (connector and cursor):
                connector, cursor = connect_to_db_and_build_cursor()
            # looking for user_name
            if user_name_cache == '':
                for l in lines:
                    l_parts = l.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                    if l_parts[0] == 'user_name:':
                        user_name_cache = l_parts[1]
                        reply_rotshild_layer += handle_dead(line_parts[1], l_parts[1], connector, cursor)
                        break
            else:
                reply_rotshild_layer += handle_dead(line_parts[1], user_name_cache, connector, cursor)
        # --------------

        # --------------
        elif line_parts[0] == 'inventory_update:':
            # open db connector and cursor if not open already
            if not (connector and cursor):
                connector, cursor = connect_to_db_and_build_cursor()
            # looking for user_name
            if user_name_cache == '':
                for l in lines:
                    l_parts = l.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                    if l_parts[0] == 'user_name:':
                        user_name_cache = l_parts[1]
                        handle_update_inventory(line[18::], l_parts[1], connector, cursor)
                        break
            else:
                handle_update_inventory(line[18::], user_name_cache, connector, cursor)
        # --------------

        # --------------
        # clients will get chats of themselves too.
        # so they should print only what comes from the server and don't print their own messages just after sending it.
        elif line_parts[0] == 'chat:':
            # looking for user_name
            if user_name_cache == '':
                for l in lines:
                    l_parts = l.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                    if l_parts[0] == 'user_name:':
                        user_name_cache = l_parts[1]
                        reply_rotshild_layer += line + '\r\n' + l + '\r\n'
                        break
            else:
                reply_rotshild_layer += line + '\r\n' + 'user_name: ' + user_name_cache + '\r\n'
        # --------------

    if not individual_reply:
        # sending the reply to all active clients
        for client in CLIENTS_ID_IP_PORT:
            server_socket.sendto(rsa.encrypt(reply_rotshild_layer.encode('utf-8'), PUBLIC_KEY),
                                 (client[1], int(client[2])))

    else:
        # sending the reply to the specific client
        server_socket.sendto(rsa.encrypt(reply_rotshild_layer.encode('utf-8'), PUBLIC_KEY), (src_ip, int(src_port)))

    if connector or cursor:
        close_connection_to_db_and_cursor(connector, cursor)


def check_if_id_matches_ip_port(src_id: str, src_ip: str, src_port: str) -> bool:
    """
    Checking if an ID matches to the IP and PORT addresses we have in our clients list - CLIENTS_ID_IP_PORT.
    (in order to make sure only a client's message is coming from its actual machine and not an imposter)
    :param src_id: <String> the ID specified in the packet.
    :param src_ip: <String> the source IP, where the packet came from.
    :param src_port: <String> the source PORT, where the packet came from.
    :return: <Boolean> True - matches, False - doesn't match.
    """

    global CLIENTS_ID_IP_PORT

    return (src_id, src_ip, src_port) in CLIENTS_ID_IP_PORT


def rotshild_filter(payload: bytes) -> bool:
    """
    Checking if a payload received is of our 5th layer protocol - 'Rotshild'.
    :param payload: <Bytes> payload to check.
    :return: <Boolean> True - passed the filter, False - didn't pass the filter
    """

    global PRIVATE_KEY

    expected = 'Rotshild'.encode('utf-8')
    return rsa.decrypt(payload, PRIVATE_KEY)[:len(expected)] == expected


def verify_and_handle_packet_thread(payload: bytes, src_addr: tuple, server_socket: socket):
    """
    Checking on encoded data if it's a Rotshild protocol packet.
    Then (if not register request) verifies match of src IP-PORT-ID.
    If all good then handling the packet.
    :param payload: <Bytes> the payload received.
    :param src_addr: <Tuple> the source address of the packet as (IP, PORT).  [IP is str and PORT is int]
    :param server_socket: <Socket> the socket object of the server.
    """

    global PRIVATE_KEY

    if rotshild_filter(payload):  # checking on encoded data if it's a Rotshild protocol packet
        plaintext = rsa.decrypt(payload, PRIVATE_KEY).decode('utf-8')
        # handling packet if ID-IP-PORT matches or if register request
        if plaintext[9] == '\r' or check_if_id_matches_ip_port(plaintext.split('\r\n')[0].split()[1],
                                                               src_addr[0],
                                                               str(src_addr[1])):
            packet_handler(plaintext, src_addr[0], str(src_addr[1]), server_socket)  # handling the packet


def inform_active_clients_about_shutdown(server_socket: socket, reason: str):
    """
    Informing all active clients that the server is shutting down.
    :param server_socket: <Socket> The server's socket object.
    :param reason: <String> why doed it closed? (by_user or error)
    """

    global CLIENTS_ID_IP_PORT, PUBLIC_KEY, ROTSHILD_OPENING_OF_SERVER_PACKETS

    for client in CLIENTS_ID_IP_PORT:
        server_socket.sendto(
            rsa.encrypt((ROTSHILD_OPENING_OF_SERVER_PACKETS + f'server_shutdown: {reason}\r\n').encode('utf-8'),
                        PUBLIC_KEY), (client[1], int(client[2])))


def check_user_input_thread():
    """
    Waiting for the user to enter a commend in terminal and execute it.
    - 'shutdown' to shutdown the server. (will set the game loop trigger event)
    - 'get clients' to prints all clients registered to this serve with their info.
    - 'delete user_name' to delete a client from the server.
    """

    global SHUTDOWN_TRIGGER_EVENT, SERVER_SOCKET_TIMEOUT

    while True:
        commend = input().lower()

        # -------------------
        if commend == 'shutdown':
            print(f'>> Shutting down the server... (it may take up to about {str(SERVER_SOCKET_TIMEOUT)} seconds)')
            # setting the shutdown trigger event.
            SHUTDOWN_TRIGGER_EVENT.set()
            return
        # -------------------

        # -------------------
        elif commend == 'get clients':
            connector, cursor = connect_to_db_and_build_cursor()
            # selecting and fetching the entire table
            cursor.execute("SELECT * FROM clients_info")
            rows = cursor.fetchall()

            if rows:
                table = PrettyTable()
                table.field_names = [i[0] for i in cursor.description]
                for row in rows:
                    table.add_row(row)
                print(table)

            else:
                print('>> The server got no clients yet.')

            close_connection_to_db_and_cursor(connector, cursor)
        # -------------------

        # -------------------
        elif commend.split()[0] == 'delete':
            connector, cursor = connect_to_db_and_build_cursor()
            user_name = commend.split()[1]

            # selecting and fetching the user name line
            cursor.execute("SELECT * FROM clients_info WHERE user_name=?", (user_name,))
            row = cursor.fetchone()

            # if user name exists
            if row:
                cursor.execute("DELETE FROM clients_info WHERE user_name=?", (user_name,))
                print(f'>> Client {user_name} has been deleted from server.')
                connector.commit()

            else:
                print(f">> Client {user_name} does'nt exist in the server.")

            close_connection_to_db_and_cursor(connector, cursor)
        # -------------------

        # -------------------
        else:
            print(">> Invalid input. (to shutdown the server enter 'shutdown')\n"
                  "                  (to get server's clients info enter 'get clients')\n"
                  "                  (to delete a client from the server enter 'delete user_name')")
        # -------------------


def close_connection_to_db_and_cursor(connection, cursor):
    """
    Closing the connection to the DB and the cursor object.
    :param connection: the connection object to the DB.
    :param cursor: the cursor object to the DB.
    """

    cursor.close()
    connection.close()


def connect_to_db_and_build_cursor() -> tuple:
    """
    Connecting to the DataBase ('Server_DB.db') or creating a new one if doesn't exist,
    Creating a cursor object for the DB to execute SQLite commends on it,
    :return: <Tuple> the Connection object of the DB and the Cursor object of it (by that order).
    """

    global DB_PATH

    connection = sqlite3.connect(DB_PATH)  # connect to the db file or create a new one if doesn't exist
    cursor = connection.cursor()  # creating a cursor object to execute SQL commends

    return connection, cursor


def initialize_sqlite_rdb():
    """
    Creating a table of clients_info (if doesn't exist). (also creating the DB file if not exists).
    """

    connection, cursor = connect_to_db_and_build_cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS clients_info"  # creating a table of clients data if not exists yet
                   " (user_name TEXT PRIMARY KEY,"
                   " password TEXT,"
                   " weapons TEXT,"  # to store separated by ',' like- 'sniper,AR,sword' [can be: stick,sniper,AR,sword]
                   " ammo INTEGER,"
                   " bombs INTEGER,"
                   " med_kits INTEGER,"
                   " backpack INTEGER,"
                   " energy_drinks INTEGER,"
                   " coins INTEGER,"
                   " exp INTEGER,"
                   " energy INTEGER)")
    close_connection_to_db_and_cursor(connection, cursor)


def set_socket() -> socket:
    """
    Setting a socket object of AF_INET (IPv4) and SOCK_DGRAM (UDP) with timeout SERVER_SOCKET_TIMEOUT.
    :return: <Socket> the socket object.
    """

    global SERVER_SOCKET_TIMEOUT

    # setting an IPv4/UDP socket
    server_socket = socket(AF_INET, SOCK_DGRAM)
    # set timeout for the socket (in order to check the loop trigger event and not block forever if not receiving)
    server_socket.settimeout(SERVER_SOCKET_TIMEOUT)
    # binding the server socket
    server_socket.bind((SERVER_IP, SERVER_UDP_PORT))
    return server_socket


def main():

    global SERVER_IP, SERVER_UDP_PORT, SOCKET_BUFFER_SIZE, PRIVATE_KEY, MAX_WORKER_THREADS,\
        SHUTDOWN_TRIGGER_EVENT, SERVER_SOCKET_TIMEOUT

    executor = None
    server_socket = None
    try:
        print(f'>> NOTE: The server requires your network to have port forwarding'
              f' to route from UDP port {str(SERVER_UDP_PORT)} to your local IP.')

        # -------------------------------------------------- GETTING THINGS READY TO GO
        # setting a socket object of AF_INET (IPv4) and SOCK_DGRAM (UDP) with timeout SERVER_SOCKET_TIMEOUT.
        server_socket = set_socket()
        # building connection and initialization of the SQL (SQLite) DataBase
        initialize_sqlite_rdb()
        # initializing a thread pool executor object
        executor = ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS, thread_name_prefix='worker_thread_')
        # --------------------------------------------------

        # setting a thread to handle user's terminal commends
        executor.submit(check_user_input_thread)

        # print(f'>> Server is up and running on {public_ip.get()}:{str(SERVER_UDP_PORT)}')
        print(f">> To shutdown the server - enter 'shutdown' in your terminal.\n"
              f"   To show all clients registered on this server and their info - enter 'get clients' in your terminal."
              f"\n   To delete a client from the server enter 'delete user_name' in your terminal.")

        # ------------------GAME LOOP-----------------------
        while not SHUTDOWN_TRIGGER_EVENT.is_set():
            try:
                data, client_address = server_socket.recvfrom(SOCKET_BUFFER_SIZE)  # getting incoming packets
            except socket_timeout:
                continue

            # verify the packet in a different thread and if all good then handling it in another thread
            executor.submit(verify_and_handle_packet_thread, data, client_address, server_socket)
        # --------------------------------------------------

        # server is shutting down. informing all active clients
        print('   [informing all active clients about the shutdown]', end='')
        inform_active_clients_about_shutdown(server_socket, 'by_user')
        print(' ---> completed')

    except OSError as ex:
        if ex.errno == 98:
            print(f">> [ERROR] Port {str(SERVER_UDP_PORT)} is not available on your machine.\n"
                  f"    Make sure the port is available and is not already in use by another service and run again.")
        else:
            print(f'>> [ERROR] Something went wrong... This is the error message: {ex}')
            print('>> Server crashed.')
            print('   [informing all active clients about the shutdown]', end='')
            inform_active_clients_about_shutdown(server_socket, 'error')
            print(' ---> completed')

    except Exception as ex:
        print(f'>> [ERROR] Something went wrong... This is the error message: {ex}')
        print('>> Server crashed.')
        print('   [informing all active clients about the shutdown]', end='')
        inform_active_clients_about_shutdown(server_socket, 'error')
        print(' ---> completed')

    finally:
        print('   [waiting for running threads to complete]', end='')
        # the next commend waits for all running tasks to complete (blocking till then), shuts down the
        # tread pool executor and frees up any resources used by it.
        executor.shutdown(wait=True)
        print(' -----------> completed')

        print('   [freeing up last resources]', end='')
        server_socket.close()
        print(' -------------------------> completed')

        print('>> Server is closed.')


# --------------------------- Main Guard
if __name__ == '__main__':
    main()
# ---------------------------
