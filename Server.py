"""
====================================================PROTOCOL=================================================================================================|                                                                                                                |
* It's a textual protocol                                                                                                                                    |
* The protocol uses encapsulation of type utf-8 (to decode and encode)                                                                                       |
                                                                                                                                                             |
* Rotshild packets's layers will be: IP()/UDP()/Raw()                                                                                                        |
                                                                                                                                                             |
structure - 'Rotshild <ID>\r\n\r\n<headers>'                                                                                                                 |
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
            - login_status: fail [if wrong user name or password] or [the ID given to him] or already_active                       [only server sends]       |
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
                                 + exp [how much?]                                                                                                           |
                                 - exp [how much?]                                                                                                           |
                                 + energy [how much?]                                                                                                        |
                                 - energy [how much?]                                                                                                        |
            - user_name: [user_name]  [comes with chat]                                                                            [only server sends]       |
            - player_place: ([the X coordinate],[the Y coordinate]) [when server sends comes with moved_player_id]                 [clients and server send] |
            - moved_player_id: [the ID of the player who moved] [comes with player_place]                                          [only server sends]       |
            - image: [the name of the file with the image of the player who moved] [comes with player_place]                       [clients and server send] |
            - shot_place: ([the X coordinate],[the Y coordinate]) [when client sends comes with hit_hp]                            [clients and server send] |
            - hit_id: [the ID of the hitted client] [comes with hit_hp and shooter_id]                                             [only server sends]       |
            - hit_hp: [the amount of heal points to take from a hitted client] [comes with shot_place or hit_id and shooter_id]    [clients ans server send] |
            - shooter_id: [the ID of the client who shoot the shot] [comes with hit_id and hit_hp]                                 [only server sends]       |
            - dead: [the ID of the dead client]                                                                                    [clients ans server send] |
            - chat: [the info of the message]  [comes with user_name when server sends]                                            [clients and server send] |
            - server_shutdown: by_user [if closed by the user] or error [if closed because of an error]                            [only server sends]       |
------------------------------------------------------------------                                                                                           |
=============================================================================================================================================================|
"""

import os
import sqlite3
import public_ip
import requests
import subprocess
import re
import platform
import threading
import colorama
import rsa
from rsa.key import PublicKey, PrivateKey
from prettytable import PrettyTable
from socket import socket, AF_INET, SOCK_DGRAM, timeout as socket_timeout
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha512

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
DEFAULT_EXP = 0
DEFAULT_ENERGY = 0
# ------------------------

# ------------------------ Files
SCRIPT_PATH = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
DB_FILE = "Server_DB.db"
DB_PATH = os.path.join(SCRIPT_DIR, DB_FILE)
DB_ACCESS_PERMISSION = 0o600  # The access permission for the  DB file in both UNIX-like and Windows Operating Systems
# (0o600 - means read and write access only for the owner)
# ------------------------

# ------------------------ Multithreading
SHUTDOWN_TRIGGER_EVENT = threading.Event()  # A trigger event to shut down the server
SHUTDOWN_INFORMING_EVENT = threading.Event()  # When set it means finished informing the clients about shutdown
MAX_WORKER_THREADS = 10  # The max amount of running worker threads.
# (larger amount mean faster client handling and able to handle more clients,
# but a big amount that is not match to your CPU will just waste important system resources and wont help)
# ------------------------

# ------------------------ General
CLIENTS_ID_IP_PORT_NAME = []  # IPs, PORTs, IDs and user names of all clients
# as (ID, IP, PORT, NAME)      [ID, IP, PORT and NAME are str]
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


def print_ansi(text: str, color: str = 'white', bold: bool = False, blink: bool = False, italic: bool = False,
               underline: bool = False, new_line: bool = True):
    """
    Prints the text, with all the optional attributes args entered, using ANSI escape sequences.
    :param text: <String> the text to print.
    :param color: <String> the color of the text.
           The options are: - red
                            - green
                            - yellow
                            - blue
                            - magenta
                            - cyan
                            - white
    :param bold: <Boolean> bold attribute.
    :param blink: <Boolean> blink attribute.
    :param italic: <Boolean> italic attribute.
    :param underline: <Boolean> underline attribute.
    :param new_line: <Boolean> to print - '\n'?
    """

    try:
        # Mostly ANSI escape sequences work on UNIX-like but not windows. that is what the colorama module used to solve

        # the next method makes ANSI available for most windows terminals
        # (if running on another OS or the terminal already supports ANSI then it does nothing)
        # (it can run multiple times without a problem)
        colorama.just_fix_windows_console()

        # Check if its a 'dumb' UNIX-like system (then its most likely don't support ANSI)
        if os.name != 'nt' and os.getenv('TERM') == 'dumb':
            # The terminal might not support ANSI, so just printing normally
            if new_line:
                print(text)
            else:
                print(text, end='')
            return

        # Define the color codes dictionary
        colors = {
            'red': '31',
            'green': '32',
            'yellow': '33',
            'blue': '34',
            'magenta': '35',
            'cyan': '36',
            'white': '0'
        }

        # Define the attributes codes dictionary
        attributes = {
            'bold': '1',
            'blink': '5',
            'italic': '3',
            'underline': '4'
        }

        # Start with the ESC character
        escape = '\033['

        # Set the color
        if color in colors:
            escape += colors[color] + ';'
        else:
            escape += '0;'

        # Set the attributes
        if bold:
            escape += attributes['bold'] + ';'
        if blink:
            escape += attributes['blink'] + ';'
        if italic:
            escape += attributes['italic'] + ';'
        if underline:
            escape += attributes['underline'] + ';'

        # Remove the trailing semicolon if present (should be)
        if escape[-1] == ';':
            escape = escape[:-1]

        if new_line:
            # Add the text and reset the formatting
            print(escape + 'm' + text + '\033[0m')
        else:
            # Add the text and reset the formatting
            print(escape + 'm' + text + '\033[0m', end='')

    except:
        if new_line:
            print(text)
        else:
            print(text, end='')


def sha512_hash(data: bytes) -> bytes:
    """
    Hashing the data with SHA-512.
    :param data: <Bytes> the data to be hashed.
    :return: <Bytes> the digest (hashed data) - 512 bit length.
    """

    # hashing the password with SHA-512 (provides a 512 bit hashed value)
    hash_object = sha512()
    hash_object.update(data)
    return hash_object.digest()


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

    global CLIENTS_ID_IP_PORT_NAME

    if ' ' in user_name or ' ' in password:
        # user name and password can not contain spaces
        return 'login_status: fail\r\n'

    for client in CLIENTS_ID_IP_PORT_NAME:
        if user_name == client[3]:
            # user name already active in the game. can't login again.
            return 'login_status: already_active\r\n'

    hashed_password = sha512_hash(password.encode())

    cursor.execute(f"SELECT * FROM clients_info WHERE user_name = '{user_name}'")
    result = cursor.fetchone()
    if not result:
        # user name does not exist in DB
        return 'login_status: fail\r\n'
    elif result[1] == hashed_password:
        # user name exists in DB and matches the password
        given_id = create_new_id((client_ip, client_port, user_name))

        print(">> ", end='')
        print_ansi(text='New client connected to the game', color='green', bold=True, underline=True)
        print_ansi(text=f'   User Name - {user_name}\n'
                        f'   User game ID - {given_id}\n'
                        f'   User IPv4 addr - {client_ip}\n'
                        f'   User port number - {client_port}\n'
                        f'   Number of active players on server - {str(len(CLIENTS_ID_IP_PORT_NAME))}\n', color='green')

        return 'login_status: ' + given_id + '\r\n'
    else:
        # user name exists but password doesn't match
        return 'login_status: fail\r\n'


def create_new_id(client_ip_port_name: tuple) -> str:
    """
    Creating a new ID for a client, saving it with its IP and PORT in the CLIENTS_ID_IP_PORT_NAME list, and returning it
    :param client_ip_port_name: <Tuple> the IP, PORT and user name of the new client as (IP, PORT, NAME).
                                                                                        [IP, PORT and NAME are str]
    :return: <String> the ID given to the client.
    """

    global CLIENTS_ID_IP_PORT_NAME

    # checking if the list is empty
    if not CLIENTS_ID_IP_PORT_NAME:
        # giving ID = 1
        CLIENTS_ID_IP_PORT_NAME.append(('1', client_ip_port_name[0], client_ip_port_name[1], client_ip_port_name[2]))
        return '1'

    last_id = 0  # the last active id we know we have at the moment
    found = False  # flag
    while found is False:  # Running till a free id found
        last_id += 1  # Checking the next id

        for client in CLIENTS_ID_IP_PORT_NAME:  # Running for each client
            if client[0] == str(last_id):
                # if got here then there is a client with the id in last_id
                break

            # checking if we passed all active clients
            elif client[0] == CLIENTS_ID_IP_PORT_NAME[len(CLIENTS_ID_IP_PORT_NAME) - 1][0]:
                # if got here then there is no client with the id in last_id
                found = True

    # the smallest free ID is in last_id
    CLIENTS_ID_IP_PORT_NAME.append((str(last_id), client_ip_port_name[0], client_ip_port_name[1], client_ip_port_name[2]))
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
        DEFAULT_ENERGY_DRINKS, DEFAULT_EXP, DEFAULT_ENERGY

    if ' ' in user_name or ' ' in password:
        # user name and password can not contain spaces
        return 'register_status: invalid\r\n'

    cursor.execute(f"SELECT * FROM clients_info WHERE user_name=?", (user_name,))
    result = cursor.fetchone()

    if result:
        # user name is taken
        return 'register_status: taken\r\n'

    hashed_password = sha512_hash(password.encode())

    # user name is free. saving it to the DB
    new_client = (user_name,
                  hashed_password,
                  DEFAULT_WEAPONS,
                  DEFAULT_AMMO,
                  DEFAULT_BOMBS,
                  DEFAULT_MED_KITS,
                  DEFAULT_BACKPACK,
                  DEFAULT_ENERGY_DRINKS,
                  DEFAULT_EXP,
                  DEFAULT_ENERGY)
    cursor.execute("INSERT INTO clients_info"
                   " (user_name,"
                   " hashed_password,"
                   " weapons,"
                   " ammo,"
                   " bombs,"
                   " med_kits,"
                   " backpack,"
                   " energy_drinks,"
                   " exp,"
                   " energy)"
                   " VALUES (?,?,?,?,?,?,?,?,?,?)", new_client)
    connector.commit()

    print(">> ", end='')
    print_ansi(text='New client registered to server', color='green', bold=True, underline=True)
    print_ansi(text=f'   User Name: {user_name}\n', color='green')

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
    global PLAYER_PLACES_BY_ID

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
    Deleting the dead client from PLAYER_PLACES_BY_ID dict and from the CLIENTS_ID_IP_PORT_NAME list,
    and initializing the inventory (the DB values but for user_name, password and coins) to default.
    :param dead_id: <String> the ID of the dead client
    :param user_name: <String> the uesr name of the dead client.
    :param connector: the connection object to the DB.
    :param cursor: the cursor object to the DB.
    :return: <String> dead header with the ID of the dead client.
    """

    global CLIENTS_ID_IP_PORT_NAME, PLAYER_PLACES_BY_ID

    # Deleting the dead client from the PLAYER_PLACES_BY_ID dict
    if dead_id in PLAYER_PLACES_BY_ID:
        del PLAYER_PLACES_BY_ID[dead_id]

    # Deleting the dead client from the CLIENTS_ID_IP_PORT_NAME list
    for client_addr in CLIENTS_ID_IP_PORT_NAME:
        if client_addr[0] == dead_id:  # client_addr[0] is the ID of the client
            CLIENTS_ID_IP_PORT_NAME.remove(client_addr)
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

    print(">> ", end='')
    print_ansi(text='Client died and disconnected from game server', color='red', bold=True, underline=True)
    print_ansi(text=f'   Dead client ID - {dead_id}\n'
                    f'   Number of active players on server - {str(len(CLIENTS_ID_IP_PORT_NAME))}\n', color='red')

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

    global PLAYER_PLACES_BY_ID

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

    global CLIENTS_ID_IP_PORT_NAME, ROTSHILD_OPENING_OF_SERVER_PACKETS, PUBLIC_KEY

    reply_rotshild_layer = ROTSHILD_OPENING_OF_SERVER_PACKETS
    connector = None  # connection object to DB
    cursor = None  # cursor object to DB
    individual_reply = False  # should the reply for that packet be for an individual client?
    user_name_cache = ''  # saving the user name of the src after found ones (to prevent more scans to find it later)
    id_cache = ''  # saving the id of the src after found ones (to prevent more scans to find it later)

    lines = rotshild_raw_layer.split('\r\n')
    while '' in lines:
        lines.remove('')

    # Recognize and handle each header
    for line in lines:
        line_parts = line.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]

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
                    if id_cache == '':
                        id_cache = lines[0].split()[1]
                    tuple_place = tuple(line_parts[1][1:-1].split(','))  # converting the place from str to tuple
                    reply_rotshild_layer += handle_player_place(tuple_place, id_cache, l_parts[1])
                    break
        # --------------

        # --------------
        # in this header clients should check the shooter_id so they wont print their own shot twice (if don't hit)
        elif line_parts[0] == 'shot_place:':
            # looking for the hit_hp header
            for l in lines:
                l_parts = l.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
                if l_parts[0] == 'hit_hp:':
                    if id_cache == '':
                        id_cache = lines[0].split()[1]
                    tuple_place = tuple(line_parts[1][1:-1].split(','))  # converting the place from str to tuple
                    reply_rotshild_layer += handle_shot_place(tuple_place, l_parts[1], id_cache)
                    break
        # --------------

        # --------------
        elif line_parts[0] == 'dead:':
            # open db connector and cursor if not open already
            if not (connector and cursor):
                connector, cursor = connect_to_db_and_build_cursor()

            if user_name_cache == '':
                if id_cache == '':
                    id_cache = lines[0].split()[1]
                for client in CLIENTS_ID_IP_PORT_NAME:
                    if client[0] == id_cache:
                        user_name_cache = client[3]
                        break
            reply_rotshild_layer += handle_dead(line_parts[1], user_name_cache, connector, cursor)
        # --------------

        # --------------
        elif line_parts[0] == 'inventory_update:':
            # open db connector and cursor if not open already
            if not (connector and cursor):
                connector, cursor = connect_to_db_and_build_cursor()

            if user_name_cache == '':
                if id_cache == '':
                    id_cache = lines[0].split()[1]
                for client in CLIENTS_ID_IP_PORT_NAME:
                    if client[0] == id_cache:
                        user_name_cache = client[3]
                        break
            handle_update_inventory(line[18::], user_name_cache, connector, cursor)
        # --------------

        # --------------
        # clients will get chats of themselves too.
        # so they should print only what comes from the server and don't print their own messages just after sending it.
        elif line_parts[0] == 'chat:':
            if user_name_cache == '':
                if id_cache == '':
                    id_cache = lines[0].split()[1]
                for client in CLIENTS_ID_IP_PORT_NAME:
                    if client[0] == id_cache:
                        user_name_cache = client[3]
                        break
            reply_rotshild_layer += line + '\r\n' + 'user_name: ' + user_name_cache + '\r\n'
        # --------------

    if not individual_reply:
        # sending the reply to all active clients
        for client in CLIENTS_ID_IP_PORT_NAME:
            server_socket.sendto(rsa.encrypt(reply_rotshild_layer.encode('utf-8'), PUBLIC_KEY),
                                 (client[1], int(client[2])))

    else:
        # sending the reply to the specific client
        server_socket.sendto(rsa.encrypt(reply_rotshild_layer.encode('utf-8'), PUBLIC_KEY), (src_ip, int(src_port)))

    if connector or cursor:
        close_connection_to_db_and_cursor(connector, cursor)


def check_if_id_matches_ip_port(src_id: str, src_ip: str, src_port: str) -> bool:
    """
    Checking if an ID matches to the IP and PORT addresses we have in our clients list - CLIENTS_ID_IP_PORT_NAME.
    (in order to make sure only a client's message is coming from its actual machine and not an imposter)
    :param src_id: <String> the ID specified in the packet.
    :param src_ip: <String> the source IP, where the packet came from.
    :param src_port: <String> the source PORT, where the packet came from.
    :return: <Boolean> True - matches, False - doesn't match.
    """

    global CLIENTS_ID_IP_PORT_NAME

    for client in CLIENTS_ID_IP_PORT_NAME:
        if src_id == client[0] and src_ip == client[1] and src_port == client[2]:
            return True
    return False


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

    # I'm doing a general exception handling because this method is a new thread and exceptions raised here will
    # not be cought in the main.
    try:
        if rotshild_filter(payload):  # checking on encoded data if it's a Rotshild protocol packet
            plaintext = rsa.decrypt(payload, PRIVATE_KEY).decode('utf-8')
            # handling packet if ID-IP-PORT matches or if register request
            if plaintext[9] == '\r' or check_if_id_matches_ip_port(plaintext.split('\r\n')[0].split()[1],
                                                                   src_addr[0],
                                                                   str(src_addr[1])):
                packet_handler(plaintext, src_addr[0], str(src_addr[1]), server_socket)  # handling the packet

    except Exception as ex:
        print(">> ", end='')
        print_ansi(text='[ERROR] ', color='red', blink=True, bold=True, new_line=False)
        print_ansi(text=f"Something went wrong (on a packet thread)... This is the error message: {ex}", color='red')
        print(">> ", end='')
        print_ansi(text='Server crashed. closing it...', color='blue')

        # setting the shutdown trigger event.
        SHUTDOWN_TRIGGER_EVENT.set()

        inform_active_clients_about_shutdown(server_socket, 'error')


def inform_active_clients_about_shutdown(server_socket: socket, reason: str):
    """
    Informing all active clients that the server is shutting down.
    :param server_socket: <Socket> The server's socket object.
    :param reason: <String> why doed it closed? (by_user or error)
    """

    global CLIENTS_ID_IP_PORT_NAME, PUBLIC_KEY, ROTSHILD_OPENING_OF_SERVER_PACKETS, SHUTDOWN_INFORMING_EVENT

    print_ansi('   [informing all active clients about the shutdown]', color='cyan', new_line=False)
    try:
        for client in CLIENTS_ID_IP_PORT_NAME:
            server_socket.sendto(
                rsa.encrypt((ROTSHILD_OPENING_OF_SERVER_PACKETS + f'server_shutdown: {reason}\r\n').encode('utf-8'),
                            PUBLIC_KEY), (client[1], int(client[2])))
        print_ansi(' ---> completed', color='green', italic=True)

    except Exception as ex:
        print_ansi(f' ---> failed  [{ex}]', color='red', italic=True)

    finally:
        SHUTDOWN_INFORMING_EVENT.set()


def check_user_input_thread(server_socket: socket):
    """
    Waiting for the user to enter a commend in terminal and execute it.
    - 'shutdown' to shutdown the server. (will set the game loop trigger event)
    - 'get clients' to print all clients registered to this serve with their info.
    - 'delete <user_name>' to delete a client from the server.
    - 'get active players' to print all active clients at the moment (their user name, ID, IP and PORT) and the number
       of active players.
    - 'reset' to reset the server and terminate the existing users and data
    - 'help' to print the optional UI commends.
    :param server_socket: <Socket> the server socket object.
    """

    global SHUTDOWN_TRIGGER_EVENT, SERVER_SOCKET_TIMEOUT, DB_PATH, CLIENTS_ID_IP_PORT_NAME

    # I'm doing a general exception handling because this method is a new thread and exceptions raised here will
    # not be cought in the main.
    try:
        while True:
            commend = input().lower().strip()

            # -------------------
            if commend == 'shutdown':
                print(">> ", end='')
                print_ansi(text=f'Shutting down the server... (it may take up to about {str(SERVER_SOCKET_TIMEOUT)} seconds)',
                           color='blue')

                # setting the shutdown trigger event.
                SHUTDOWN_TRIGGER_EVENT.set()

                inform_active_clients_about_shutdown(server_socket, 'by_user')
                return
            # -------------------

            # -------------------
            elif commend == 'get clients':
                connector, cursor = connect_to_db_and_build_cursor()
                # selecting and fetching the entire table
                cursor.execute("SELECT * FROM clients_info")
                rows = cursor.fetchall()
                # if there are clients
                if rows:
                    # building the Prettytable table
                    table = PrettyTable()
                    # setting field names
                    fields = []
                    for i in range(len(cursor.description)):
                        if i != 1:
                            fields.append(cursor.description[i][0].replace('_', ' ').title())
                        else:
                            fields.append("Password (hashed)")
                    table.field_names = fields
                    # adding rows
                    for row in rows:
                        row = list(row)
                        row[1] = '* * * * * * * *'
                        table.add_row(row)
                    # printing the table
                    print_ansi(text=str(table) + '\n', color='cyan', bold=True)
                # if there are no clients
                else:
                    print(">> ", end='')
                    print_ansi(text='The server got no clients yet.\n', color='blue')

                close_connection_to_db_and_cursor(connector, cursor)
            # -------------------

            # -------------------
            elif len(commend.split()) != 0 and commend.split()[0] == 'delete':
                connector, cursor = connect_to_db_and_build_cursor()
                user_name = commend.split()[1]

                # selecting and fetching the user name line
                cursor.execute("SELECT * FROM clients_info WHERE user_name=?", (user_name,))
                row = cursor.fetchone()

                # if user name exists
                if row:
                    cursor.execute("DELETE FROM clients_info WHERE user_name=?", (user_name,))
                    connector.commit()

                    print(">> ", end='')
                    print_ansi(text=f"Client '{user_name}' had been deleted from the server.\n", color='blue')

                # if user name doesn't exist
                else:
                    print(">> ", end='')
                    print_ansi(text=f"Client '{user_name}' does'nt exist in the server.\n", color='blue')

                close_connection_to_db_and_cursor(connector, cursor)
            # -------------------

            # -------------------
            elif commend == 'get active players':
                # if there are any active players
                if CLIENTS_ID_IP_PORT_NAME:
                    print(">> ", end='')
                    print_ansi(text=f'Number of active players at the moment: {str(len(CLIENTS_ID_IP_PORT_NAME))}',
                               color='blue')

                    # building the Prettytable table
                    table = PrettyTable()
                    table.field_names = ('ID', 'IP', 'PORT', 'USER_NAME')
                    for player in CLIENTS_ID_IP_PORT_NAME:
                        table.add_row(player)
                    # printing the client table
                    print_ansi(text=str(table) + '\n', color='cyan', bold=True)

                # if there are no active players
                else:
                    print(">> ", end='')
                    print_ansi(text='There are no active players on the server at the moment.\n', color='blue')
            # -------------------

            # -------------------
            elif commend == 'reset':
                print(">> ", end='')
                print_ansi(text='Resetting the server (all clients and current data will be permanently terminated)...',
                           color='blue')

                # if there is a DB (should be because we create it in the beginning... but just in case I check again)
                if os.path.isfile(DB_PATH):
                    # delete the DB file
                    print_ansi(text="   [Deleting current DB ('Server_DB.db' file) from your system]", new_line=False,
                               color='cyan')
                    try:
                        os.remove(DB_PATH)
                        print_ansi(text=' -------------------------> completed', color='green', italic=True)
                    except Exception as ex:
                        print_ansi(text=f' -------------------------> failed [{ex}]', color='red', italic=True)

                    # creating a new empty DB
                    print_ansi(text="   [Creating a new empty DB ('Server_DB.db' file) and initializing an empty table]",
                               new_line=False, color='cyan')
                    initialize_sqlite_rdb()
                    print_ansi(text=' ------> completed', color='green', italic=True)

                    print_ansi(text='   Process completed (see above completed/failed in each field).\n', color='blue',
                               italic=True)
            # -------------------

            # -------------------
            elif commend == 'help':
                print(">> ", end='')
                print_ansi(text="OPTIONAL UI COMMENDS:", color='blue', underline=True)
                print_ansi(text="   - 'shutdown': To shutdown the server.\n"
                                "   - 'get clients': To show all clients registered on this server and their info.\n"
                                "   - 'delete <user_name>': To delete a client from the server.\n"
                                "   - 'get active players': To show active clients at the moment (their user name, ID, IP, PORT)\n"
                                "      and the number of active players at the moments.\n"
                                "   - 'reset': To reset the server and terminate any existing users and data.\n"
                                "   - 'help': To show optional UI commends.\n",
                           color='cyan')
            # -------------------

            # -------------------
            elif commend.strip() == '':
                pass
            # -------------------

            # -------------------
            else:
                print(">> ", end='')
                print_ansi(text="Invalid input. Enter 'help' to see the commends you can use.\n", color='red')
            # -------------------

    except Exception as ex:
        print(">> ", end='')
        print_ansi(text='[ERROR] ', color='red', blink=True, bold=True, new_line=False)
        print_ansi(text=f"Something went wrong (on user input thread)... This is the error message: {ex}", color='red')
        print(">> ", end='')
        print_ansi(text='Server crashed. closing it...', color='blue')

        # setting the shutdown trigger event.
        SHUTDOWN_TRIGGER_EVENT.set()

        inform_active_clients_about_shutdown(server_socket, 'error')
        return


def close_connection_to_db_and_cursor(connection, cursor):
    """
    Closing the connection to the DB and the cursor object.
    :param connection: the connection object to the DB.
    :param cursor: the cursor object to the DB.
    """

    try:
        cursor.close()
        connection.close()
    except NameError as ex:
        # can be raised if cursor or connection has not been defined
        print(">> ", end='')
        print_ansi(text='[ERROR] ', color='red', bold=True, blink=True, new_line=False)
        print_ansi(text=f"NameError: {ex}\n   (Possibly connection or cursor object of SQLite3 is trying to get "
                        "closed but had not been defined)", color='red')
    except AttributeError as ex:
        # can be raised if cursor or connection has already been closed
        print(">> ", end='')
        print_ansi(text='[ERROR] ', color='red', bold=True, blink=True, new_line=False)
        print_ansi(text=f"AttributeError: {ex}\n   (Possibly connection or cursor object of SQLite3 is trying to get "
                        "closed but had already been closed)", color='red')


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


def set_db_read_write_permissions_to_only_owner():
    """
    Setting the DataBase file permissions to allow only the owner user account (the creator) to read and write.
    """

    global DB_ACCESS_PERMISSION, DB_PATH

    try:
        if os.name == "posix" or os.name == 'nt':
            # UNIX or Windows Operating System
            os.chmod(DB_PATH, DB_ACCESS_PERMISSION)
        else:
            # Handle other operating systems as needed
            print(">> ", end='')
            print_ansi(text='[WARNING] ', color='yellow', blink=True, new_line=False)
            print_ansi(text="The program doesn't support setting only-owner read-write permissions\n"
                            f"   for DataBase file on {os.name} Operating System like yours.\n"
                            "   (This will not interfere with the normal running of the program).\n", color='yellow')
    except:
        print(">> ", end='')
        print_ansi(text='[WARNING] ', color='yellow', blink=True, new_line=False)
        print_ansi(text='Failed to set only-owner read-write permissions for DataBase file.\n'
                        '   (This will not interfere with the normal running of the program).\n', color='yellow')


def initialize_sqlite_rdb():
    """
    Creating a table of clients_info (if doesn't exist). (also creating the DB file if not exists).
    """

    connection, cursor = connect_to_db_and_build_cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS clients_info"  # creating a table of clients data if not exists yet
                   " (user_name TEXT PRIMARY KEY,"
                   " hashed_password BLOB,"
                   " weapons TEXT,"  # to store separated by ',' like- 'sniper,AR,sword' [can be: stick,sniper,AR,sword]
                   " ammo INTEGER,"
                   " bombs INTEGER,"
                   " med_kits INTEGER,"
                   " backpack INTEGER,"
                   " energy_drinks INTEGER,"
                   " exp INTEGER,"
                   " energy INTEGER)")
    close_connection_to_db_and_cursor(connection, cursor)
    set_db_read_write_permissions_to_only_owner()


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


def get_public_ip() -> str:
    """
    Trying to get the public IP.
    :return: <String> the public IP address.
    """

    # ----------------
    # Try to get public IP address from multiple external APIs
    api_urls = [
        'https://ipinfo.io/ip',  # returns response as plaintext
        'https://api.ipify.org?format=json',  # returns response as JSON object
        'https://api.myip.com/',  # returns response as JSON object
        'https://icanhazip.com/',  # returns response as plaintext
        'https://ifconfig.me/',  # returns response as plaintext
        'https://ip.seeip.org/',  # returns response as plaintext
        'https://www.trackip.net/ip',  # returns response as plaintext
    ]
    methods = ['GET', 'HEAD']
    for url in api_urls:
        for method in methods:
            try:
                response = requests.request(method, url, timeout=3)
                if response.status_code == 200:  # (200 is a success HTTP status code)
                    if url in ['https://api.ipify.org?format=json', 'https://api.myip.com/']:
                        # response is JSON object
                        return response.json()['ip']
                    # response is plaintext
                    return response.text.strip()
            except:
                pass
    # ----------------

    # ----------------
    # if external APIs fails. try to get public IP address from public_ip module (though it works very similar)
    try:
        return public_ip.get()
    except:
        pass
    # ----------------

    # If all methods fail
    return "[Your public IP (our system couldn't find it, ask the NET Admin to find it)]"


def get_private_ip() -> str:
    """
    Getting the private IP of the machine.
    :return: <String> the private IP address.
    """

    # -------------------
    # If its a Windows Operating System
    try:
        if platform.system() == 'Windows':
            # Execute the 'ipconfig' command and get the output
            output = subprocess.check_output(['ipconfig']).decode('cp850')

            # Finding the active interface by detecting the paragraph with the default gateway
            output = output.split('\r\n\r\n')

            # Use a regular expression to parse the output and extract the active default gateway
            gateway_pattern = r'Default Gateway.*: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            for interface in output:
                match = re.search(gateway_pattern, interface)
                if match is not None:
                    active_interface = interface
                    break

            # Use a regular expression to parse the output and extract the IPv4
            ip_pattern = r'IPv4 Address.*: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            match = re.search(ip_pattern, active_interface)
            return match.group(1)
    except:
        pass
    # -------------------

    # -------------------
    try:
        temp_s = socket(AF_INET, SOCK_DGRAM)
        temp_s.connect(('8.8.8.8', 80))  # Google's DNS server address
        # *when connecting a socket to an external host the operating system automatically associate the local ip to it
        private_ip = temp_s.getsockname()[0]
        temp_s.close()
        return private_ip
    except:
        pass
    # -------------------

    return "[Your private IP (our system couldn't find it, check for it yourself)]"


def main():

    global SERVER_IP, SERVER_UDP_PORT, SOCKET_BUFFER_SIZE, PRIVATE_KEY, MAX_WORKER_THREADS,\
        SHUTDOWN_TRIGGER_EVENT, SERVER_SOCKET_TIMEOUT, SHUTDOWN_INFORMING_EVENT

    executor = None
    server_socket = None
    try:
        # -------------------------------------------------- Printing title
        print_ansi(text='\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++',
                   color='blue', bold=True, blink=True, italic=True)
        print_ansi(text='====================== GAME SERVER ======================',
                   color='cyan', bold=True, blink=True, italic=True)
        print_ansi(text='+++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n',
                   color='blue', bold=True, blink=True, italic=True)
        # --------------------------------------------------

        print(">> ", end='')
        print_ansi(text='Loading...\n', color='blue', bold=True, italic=True)

        # -------------------------------------------------- GETTING THINGS READY TO GO
        # setting a socket object of AF_INET (IPv4) and SOCK_DGRAM (UDP) with timeout SERVER_SOCKET_TIMEOUT.
        server_socket = set_socket()
        # building connection and initialization of the SQL (SQLite) DataBase
        initialize_sqlite_rdb()
        # initializing a thread pool executor object
        executor = ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS, thread_name_prefix='worker_thread_')
        # --------------------------------------------------

        # setting a thread to handle user's terminal commends
        executor.submit(check_user_input_thread, server_socket)

        my_public_ip = get_public_ip()
        my_private_ip = get_private_ip()

        # -------------------------------------------------- Printing start info and running status
        print_ansi(text='---------------------------------------------------------',
                   color='magenta', italic=True, bold=True)
        print(">> ", end='')
        print_ansi(text='NOTE:', new_line=False, color='magenta', italic=True, bold=True)
        print_ansi(text='The server requires your network to have port forwarding\n'
                   f'         to route from UDP port {str(SERVER_UDP_PORT)} to your local IP if you want\n'
                   '         it to be available for clients from WAN (outside your network).\n'
                   '         If you only run it for players on your LAN then this is not a mandatory requirement for you.\n'
                   , color='magenta', italic=True)
        print(">> ", end='')
        print_ansi(text='Server is up and running on:', color='magenta', italic=True, bold=True)
        print_ansi(text=f'   - For WAN clients - {my_public_ip}:{str(SERVER_UDP_PORT)}\n'
                   f'   - For LAN clients - {my_private_ip}:{str(SERVER_UDP_PORT)}\n',
                   color='magenta', italic=True)
        print('    ', end='')
        print_ansi(text='NOTE:', new_line=False, color='magenta', italic=True, bold=True)
        print_ansi(text=" It's important that clients on your network will enter the game by the private IP\n"
                   "         (the one for LAN clients), and clients outside your network will enter by the public IP\n"
                   "         (the one for WAN clients).", color='magenta', italic=True)
        print_ansi(text="---------------------------------------------------------\n",
                   color='magenta', italic=True, bold=True)
        # --------------------------------------------------

        print("\n>> ", end='')
        print_ansi(text='All Set! ENJOY!!!\n   (see below the commends you can use as the server manager...)\n',
                   color='green', bold=True)

        # -------------------------------------------------- Printing the UI optional commends
        print(">> ", end='')
        print_ansi(text="OPTIONAL UI COMMENDS:", color='blue', underline=True)
        print_ansi(text="   - 'shutdown': To shutdown the server.\n"
                   "   - 'get clients': To show all clients registered on this server and their info.\n"
                   "   - 'delete <user_name>': To delete a client from the server.\n"
                   "   - 'get active players': To show active clients at the moment (their user name, ID, IP, PORT)\n"
                   "      and the number of active players at the moments.\n"
                   "   - 'reset': To reset the server and terminate any existing users and data.\n"
                   "   - 'help': To show optional UI commends.\n",
                   color='cyan')
        # --------------------------------------------------

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # =================| GAME LOOP |==================
        while not SHUTDOWN_TRIGGER_EVENT.is_set():
            try:
                data, client_address = server_socket.recvfrom(SOCKET_BUFFER_SIZE)  # getting incoming packets
            except socket_timeout:
                continue

            # verify the packet in a different thread and if all good then handling it in another thread
            executor.submit(verify_and_handle_packet_thread, data, client_address, server_socket)
        # ==================================================
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    except OSError as ex:
        if ex.errno == 98:
            print(">> ", end='')
            print_ansi(text='[ERROR] ', color='red', blink=True, bold=True, new_line=False)
            print_ansi(text=f"Port {str(SERVER_UDP_PORT)} is not available on your machine.\n"
                       "    Make sure the port is available and is not already in use by another service and run again.",
                       color='red')
            print(">> ", end='')
            print_ansi(text='Server is shutting down...', color='blue')
        else:
            print(">> ", end='')
            print_ansi(text='[ERROR] ', color='red', blink=True, bold=True, new_line=False)
            print_ansi(text=f"Something went wrong (on main thread)... This is the error message: {ex}", color='red')
            print(">> ", end='')
            print_ansi(text='Server crashed. closing it...', color='blue')
            inform_active_clients_about_shutdown(server_socket, 'error')

    except Exception as ex:
        print(">> ", end='')
        print_ansi(text='[ERROR] ', color='red', blink=True, bold=True, new_line=False)
        print_ansi(text=f"Something went wrong (on main thread)... This is the error message: {ex}", color='red')
        print(">> ", end='')
        print_ansi(text='Server crashed. closing it...', color='blue')
        inform_active_clients_about_shutdown(server_socket, 'error')

    finally:
        SHUTDOWN_INFORMING_EVENT.wait()  # wait for informing to complete

        print_ansi(text='   [waiting for running threads to complete]', new_line=False, color='cyan')
        # the next commend waits for all running tasks to complete (blocking till then), shuts down the
        # tread pool executor and frees up any resources used by it.
        executor.shutdown(wait=True)
        print_ansi(text=' -----------> completed', color='green', italic=True)

        print_ansi(text='   [freeing up last resources]', new_line=False, color='cyan')
        server_socket.close()
        colorama.deinit()  # stop using colorama. restore stduot and stderr to original values (terminal)
        print_ansi(text=' -------------------------> completed', color='green', italic=True)

        print(">> ", end='')
        print_ansi(text='Server is closed.', color='green', italic=True)


# --------------------------- Main Guard
if __name__ == '__main__':
    main()
# ---------------------------
