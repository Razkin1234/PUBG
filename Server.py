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
            - first_inventory: [[weapon_name1]/[weapon_name2]...],                                                                 [only server sends]       |
                               [how much ammo?],                                                                                                             |
                               [how much med kits?],                                                                                                         |
                               [how much backpack?],                                                                                                         |
                               [how much plasters?],                                                                                                         |
                               [how much shoes?],                                                                                                            |
                               [how much exp?],                                                                                                              |
                               ([the X respawn coordinate]-[the Y respawn coordinate])               (*NOTE: all in 1 line)                                  |
            - register_request: [user name],[password]                                                                             [only clients send]       |
            - register_status: taken [if the user name already exists] or success  or invalid                                      [only server sends]       |
            - inventory_update: [can be only one, or a few of the options below, you should separate them by ',']                  [only clients send]       |
                                 + weapons [weapon name]                                                                                                     |
                                 - weapons [weapon name]                                                                                                     |
                                 + ammo [how much?]                                                                                                          |
                                 - ammo [how much?]                                                                                                          |
                                 + med_kits [how much?]                                                                                                      |
                                 - med_kits [how much?]                                                                                                      |
                                 + backpack [how much?]                                                                                                      |
                                 - backpack [how much?]                                                                                                      |
                                 + plasters [how much?]                                                                                                      |
                                 - plasters [how much?]                                                                                                      |
                                 + shoes [how much?]                                                                                                         |
                                 - shoes [how much?]                                                                                                         |
                                 + exp [how much?]                                                                                                           |
                                 - exp [how much?]                                                                                                           |
            - user_name: [user_name]  [comes with chat]                                                                            [only server sends]       |
            - player_place: ([the X coordinate],[the Y coordinate]) [comes with image and when server sends moved_player_id]       [clients and server send] |
            - moved_player_id: [the ID of the player who moved] [comes with player_place and image]                                [only server sends]       |
            - image: [the name of the file with the image of the player who moved] [comes with player_place and image]             [clients and server send] |
            - shot_place: ([the X coordinate],[the Y coordinate]) [comes with hit_hp and when server sends then shooter_id too]    [clients and server send] |
            - hit_hp: [the amount of heal points to take from a hitted client] [comes with shot_place and shooter_id if server]    [clients ans server send] |
            - shooter_id: [the ID of the client who shoot the shot] [comes with shot_place and hit_hp]                             [only server sends]       |
            - dead: [the ID of the dead client]                                                                                    [clients ans server send] |
            - chat: [the info of the message]  [comes with user_name when server sends]                                            [clients and server send] |
            - server_shutdown: by_user [if closed by the user] or error [if closed because of an error]                            [only server sends]       |
            - disconnect: [the ID of the clients]                                                                                  [clients ans server send] |
            - enemy_player_place_image_type_hit: [id_enemy],([the X coordinate],[the Y coordinate]),[image],[type_of_enemy],[Yes or No(if hitting)] [only server sends]  |
            - hit_an_enemy: [id_of_enemy]                                                                                          [only clients sends]      |
------------------------------------------------------------------                                                                                           |
=============================================================================================================================================================|
"""

import os
import sys
import sqlite3
import requests
import subprocess
import re
import threading
import colorama
import MyKeyring  # my module (not the external library)
from prettytable import PrettyTable
from socket import socket, AF_INET, SOCK_DGRAM, timeout as socket_timeout
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha512
from cryptography.fernet import Fernet
from random import randint

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
DEFAULT_MED_KITS = 0
DEFAULT_BACKPACK = 0
DEFAULT_PLASTERS = 0
DEFAULT_SHOES = 0
DEFAULT_EXP = 0
# ------------------------

# ------------------------ Running machine info
SYS_PLATFORM = None  # The operating system of the machine (will be 'nt' for windows and 'posix' for Unix-like)
SCRIPT_PATH = None
SCRIPT_DIR = None
DB_FILE = None
DB_PATH = None
DB_ACCESS_PERMISSION = None  # The access permission for the  DB file in both UNIX-like and Windows Operating Systems
# ------------------------

# ------------------------ Events
SHUTDOWN_TRIGGER_EVENT = threading.Event()  # A trigger event to shut down the server (to exit the game loop)
SHUTDOWN_INFORMING_EVENT = threading.Event()  # When set it means finished informing the clients about shutdown
CLOSING_THREADS_EVENT = threading.Event()  # when set it means the server is closing its worker threads
# (the purpose of this is to inform the user input thread to terminate at a crash situation)
# ------------------------

# ------------------------ Fernet encryption
# Fernet is a high-level implementation of the Advanced Encryption Standard (AES) algorithm.
# It uses AES in CBC (Cipher Block Chaining) mode with 128-bit key and PKCS7 padding to encrypt and decrypt data.
FERNET_ENCRYPTION = None  # Will store the Fernet object (contains the key) to encrypt and decrypt data.
# ------------------------

# ------------------------ Keyring identifiers (I use my own keyring on a JSON file. not using the library)
# The service name (a label that helps to identify the purpose of the password being stored in the keyring. which app?)
SERVICE_NAME = 'Local_Private_Game_Server'

# The username (helps to identify the specific password being stored in the keyring. which key?)
FERNET_KEY_USERNAME = 'fernet_key'  # the real Fernet key
FAKE_FERNET_KEY_1 = 'fake_fernet_1'  # a fake Fernet key
FAKE_FERNET_KEY_2 = 'fake_fernet_2'  # a fake Fernet key
FAKE_FERNET_KEY_3 = 'fake_fernet_3'  # a fake Fernet key
FAKE_FERNET_KEY_4 = 'fake_fernet_4'  # a fake Fernet key
FAKE_FERNET_KEY_5 = 'fake_fernet_5'  # a fake Fernet key
# ------------------------

# ------------------------ General
# The optional respawn places on the map as (X,Y)   [X and Y are str]
RESPAWN_SPOTS = [('1', '1'), ('2', '2'), ('3', '3')]  # REPLACE THIS WITH THE REAL OPTIONS!!!!!!!!!!!!!!!!!!!
# IPs, PORTs, IDs and user names of all clients as (ID, IP, PORT, NAME)      [ID, IP, PORT and NAME are str]
CLIENTS_ID_IP_PORT_NAME = []
# Places of all clients by IDs as ID:(X,Y)        [ID, X and Y are str]
PLAYER_PLACES_BY_ID = {}
# List of all of the IDs of enemy [ID1,ID2,ID3,....]
SAVE_ID_FOR_ENEMY = []
# Dictionary that the key is the id of enemy like ID:[[place_of_enemy],[[id_of_player_locked]],[number_of_lives_enemy],[type_enemy]]
ENEMY_BY_ID = {}
# Opening for server's packets (after this are the headers)
ROTSHILD_OPENING_OF_SERVER_PACKETS = 'Rotshild 0\r\n\r\n'
# -------------------------


def handle_locking_on_enemy(enemy_id, player_id):
    """
    changing the enemy who got shot to locked on the one who shot him
    :param player_id:
    :param enemy_id:
    :return: none
    """
    global ENEMY_BY_ID
    ENEMY_BY_ID[enemy_id][1] = player_id


def first_player_locked_on():
    """
    i am checking if there is only one player on the map. if there
    so i am setting all of the enemies to be locked on him
    :return: nothing
    """
    global ENEMY_BY_ID, PLAYER_PLACES_BY_ID, CLIENTS_ID_IP_PORT_NAME, SAVE_ID_FOR_ENEMY
    if len(PLAYER_PLACES_BY_ID) == 1:
        client_id = CLIENTS_ID_IP_PORT_NAME[0][0]
        for id_enemy in SAVE_ID_FOR_ENEMY:
            ENEMY_BY_ID[id_enemy][1] = client_id


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

    global SYS_PLATFORM

    try:
        # Mostly ANSI escape sequences work on UNIX-like but not windows. that is what the colorama module used to solve

        # the next method makes ANSI available for most windows terminals
        # (if running on another OS or the terminal already supports ANSI then it does nothing)
        # (it can run multiple times without a problem)
        colorama.just_fix_windows_console()

        # Check if its a 'dumb' UNIX-like system (then its most likely don't support ANSI)
        if SYS_PLATFORM != 'nt' and os.getenv('TERM') == 'dumb':
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


def handle_disconnect(client_id: str, user_name: str, connector, cursor) -> str:
    """
    Deleting the client from PLAYER_PLACES_BY_ID dict and from the CLIENTS_ID_IP_PORT_NAME list and saving its place to
    the DB for respawn.
    :param client_id: <String> the ID of the clients who is disconnecting.
    :param user_name: <String> the user name of the client.
    :param connector: the connection object to the DB.
    :param cursor: the cursor object to the DB.
    :return: <String> disconnect header with the ID of the disconnected clients.
    """

    global PLAYER_PLACES_BY_ID, CLIENTS_ID_IP_PORT_NAME, FERNET_ENCRYPTION

    # Store current place to DB and delete the client from the PLAYER_PLACES_BY_ID dict
    if client_id in PLAYER_PLACES_BY_ID:
        # saving the location for respawn
        cursor.execute("UPDATE clients_info SET respawn_place = ? WHERE user_name = ?",
                       (FERNET_ENCRYPTION.encrypt(str(PLAYER_PLACES_BY_ID[client_id]).replace("'", '').replace(' ', '')
                                                  .encode('utf-8')), user_name.encode('utf-8')))
        connector.commit()
        # deleting client from game dict
        del PLAYER_PLACES_BY_ID[client_id]

    # Deleting the client from the CLIENTS_ID_IP_PORT_NAME list
    for client_addr in CLIENTS_ID_IP_PORT_NAME:
        if client_addr[0] == client_id:  # client_addr[0] is the ID of the client
            CLIENTS_ID_IP_PORT_NAME.remove(client_addr)
            break

    print(">> ", end='')
    print_ansi(text='Client manually disconnected from game server', color='red', bold=True, underline=True)
    print_ansi(text=f'   client ID - {client_id}\n'
                    f'   Number of active players on server - {str(len(CLIENTS_ID_IP_PORT_NAME))}\n', color='red')

    # returning a dead header
    return 'disconnect: ' + client_id + '\r\n'


def handle_update_inventory(header_info: str, user_name: str, connector, cursor):
    """
    updating the inventory of a client in the DB
    :param header_info: <String> all the raw info in the update_inventory header.
    :param user_name: <String> the user name of the client.
    :param connector: the connection object to the DB.
    :param cursor: the cursor object to the DB.
    """

    global FERNET_ENCRYPTION

    updates = header_info.split(',')
    # handle each inventory update
    for update in updates:
        operation, column, info = update.split()
        if column != 'weapons':
            # getting the old value (will be an encrypted bytes object)
            cursor.execute(f"SELECT {column} FROM clients_info WHERE user_name = ?", (user_name.encode('utf-8'),))
            value = cursor.fetchone()
            # changing it to the real int value of it
            value = int(FERNET_ENCRYPTION.decrypt(value[0]).decode('utf-8'))
            # making the operation
            if operation == '+':
                value += int(info)
            elif operation == '-':
                value -= int(info)
            # updating the value
            cursor.execute(f"UPDATE clients_info"
                           f" SET {column} = ?"
                           f" WHERE user_name=?",
                           (FERNET_ENCRYPTION.encrypt(str(value).encode('utf-8')), user_name.encode('utf-8')))
        else:
            # getting the old value (will be an encrypted bytes object)
            cursor.execute(f"SELECT weapons FROM clients_info WHERE user_name = ?", (user_name.encode('utf-8'),))
            value = cursor.fetchone()
            # changing it to the real int value of it
            value = FERNET_ENCRYPTION.decrypt(value[0]).decode('utf-8')
            # making the operation
            if operation == '+':
                if value == '':
                    value = info
                else:
                    value += ',' + info
            else:
                client_weapons = value.split(',')
                updated_weapons = []
                for weapon in client_weapons:
                    if weapon != info:
                        updated_weapons.append(weapon)
                value = ','.join(updated_weapons)
            cursor.execute("UPDATE clients_info"
                           " SET weapons = ?"
                           " WHERE user_name = ?",
                           (FERNET_ENCRYPTION.encrypt(value.encode('utf-8')), user_name.encode('utf-8')))
    connector.commit()


def handle_login_request(user_name: str, password: str, client_ip: str, client_port: str, cursor) -> str:
    """
    Checking if the user_name exists and matches its password in the DB. if yes giving ID and inventory.
    :param user_name: <Sting> the user name entered in the login request.
    :param password: <String> the password entered in the login request.
    :param client_ip: <String> the IP of the client.
    :param client_port <String> the port of the client.
    :param cursor: the cursor object to the DB.
    :return: <String> login_status header (if matches then the given ID, if not then 'fail') and first_inventory header.
    """

    global CLIENTS_ID_IP_PORT_NAME, FERNET_ENCRYPTION, PLAYER_PLACES_BY_ID

    if ' ' in user_name or ' ' in password:
        # user name and password can not contain spaces
        return 'login_status: fail\r\n'

    for client in CLIENTS_ID_IP_PORT_NAME:
        if user_name == client[3]:
            # user name already active in the game. can't login again.
            return 'login_status: already_active\r\n'

    hashed_password = sha512_hash(password.encode('utf-8'))

    cursor.execute(f"SELECT * FROM clients_info WHERE user_name = ?", (user_name.encode('utf-8'),))
    result = cursor.fetchone()
    if not result:
        # user name does not exist in DB
        return 'login_status: fail\r\n'
    elif result[1] == hashed_password:
        # user name exists in DB and matches the password
        given_id = create_new_id((client_ip, client_port, user_name))

        # decrypting the data from the DB
        plsintext_inventory = []
        for i in range(2, len(result), 1):
            plsintext_inventory.append(FERNET_ENCRYPTION.decrypt(result[i]).decode('utf-8'))

        # save in PLAYER_PLACES_BY_ID dict
        PLAYER_PLACES_BY_ID[given_id] = tuple(plsintext_inventory[7][1:-1].split(','))

        print(">> ", end='')
        print_ansi(text='New client connected to the game', color='green', bold=True, underline=True)
        print_ansi(text=f'   User Name - {user_name}\n'
                        f'   User game ID - {given_id}\n'
                        f'   User IPv4 addr - {client_ip}\n'
                        f'   User port number - {client_port}\n'
                        f'   Number of active players on server - {str(len(CLIENTS_ID_IP_PORT_NAME))}\n', color='green')

        return 'login_status: ' + given_id + '\r\n' + f'first_inventory: ' \
                                                      f"{plsintext_inventory[0].replace(',', '/')}," \
                                                      f'{plsintext_inventory[1]},' \
                                                      f'{plsintext_inventory[2]},' \
                                                      f'{plsintext_inventory[3]},' \
                                                      f'{plsintext_inventory[4]},' \
                                                      f'{plsintext_inventory[5]},' \
                                                      f'{plsintext_inventory[6]},' \
                                                      f"{plsintext_inventory[7].replace(',', '-')}\r\n"
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
    CLIENTS_ID_IP_PORT_NAME.append(
        (str(last_id), client_ip_port_name[0], client_ip_port_name[1], client_ip_port_name[2]))
    return str(last_id)


def random_respawn_place() -> tuple:
    """
    Random a respawn spot from the RESPAWN_SPOTS global list.
    :return: <Tuple> the random respawn place as (X,Y).  [X and Y are str]
    """

    global RESPAWN_SPOTS

    return RESPAWN_SPOTS[randint(0, len(RESPAWN_SPOTS) - 1)]


def handle_register_request(user_name: str, password: str, connector, cursor) -> str:
    """
    Checking if user_name already taken. if not - adds it to the DB with his password and default values of player data.
    :param user_name: <String> the user name entered in the register request.
    :param password: <String> the password entered in the register request.
    :param connector: the connection object to the DB.
    :param cursor: the cursor object to the DB.
    :return: <String> register_status header. (if taken - 'taken', if free - 'success', if invalid - 'invalid').
    """

    global DEFAULT_WEAPONS, DEFAULT_AMMO, DEFAULT_MED_KITS, DEFAULT_BACKPACK, DEFAULT_PLASTERS, DEFAULT_SHOES, \
        DEFAULT_EXP, FERNET_ENCRYPTION

    if ' ' in user_name or ' ' in password:
        # user name and password can not contain spaces
        return 'register_status: invalid\r\n'

    cursor.execute(f"SELECT * FROM clients_info WHERE user_name = ?", (user_name.encode('utf-8'),))
    result = cursor.fetchone()

    if result:
        # user name is taken
        return 'register_status: taken\r\n'

    # random a spawn location
    spawn_place = random_respawn_place()

    # encrypting the data to be saved (and hashing the password)
    hashed_password = sha512_hash(password.encode('utf-8'))
    encrypted_default_weapons = FERNET_ENCRYPTION.encrypt(DEFAULT_WEAPONS.encode('utf-8'))
    encrypted_default_ammo = FERNET_ENCRYPTION.encrypt(str(DEFAULT_AMMO).encode('utf-8'))
    encrypted_default_med_kits = FERNET_ENCRYPTION.encrypt(str(DEFAULT_MED_KITS).encode('utf-8'))
    encrypted_default_backpack = FERNET_ENCRYPTION.encrypt(str(DEFAULT_BACKPACK).encode('utf-8'))
    encrypted_default_plasters = FERNET_ENCRYPTION.encrypt(str(DEFAULT_PLASTERS).encode('utf-8'))
    encrypted_default_shoes = FERNET_ENCRYPTION.encrypt(str(DEFAULT_SHOES).encode('utf-8'))
    encrypted_default_exp = FERNET_ENCRYPTION.encrypt(str(DEFAULT_EXP).encode('utf-8'))
    encrypted_spawn_place = FERNET_ENCRYPTION.encrypt(str(spawn_place).replace("'", '').replace(' ', '')
                                                      .encode('utf-8'))

    # user name is free. saving it to the DB
    new_client = (user_name.encode('utf-8'),
                  hashed_password,
                  encrypted_default_weapons,
                  encrypted_default_ammo,
                  encrypted_default_med_kits,
                  encrypted_default_backpack,
                  encrypted_default_plasters,
                  encrypted_default_shoes,
                  encrypted_default_exp,
                  encrypted_spawn_place)
    cursor.execute("INSERT INTO clients_info"
                   " (user_name,"
                   " hashed_password,"
                   " weapons,"
                   " ammo,"
                   " med_kits,"
                   " backpack,"
                   " plasters,"
                   " shoes,"
                   " exp,"
                   " respawn_place)"
                   " VALUES (?,?,?,?,?,?,?,?,?,?)", new_client)
    connector.commit()

    print(">> ", end='')
    print_ansi(text='New client registered to server', color='green', bold=True, underline=True)
    print_ansi(text=f'   User Name: {user_name}\n', color='green')

    return 'register_status: success\r\n'


def handle_shot_place(shot_place: tuple, hp: str, shooter_id: str) -> str:
    """
    Return the following Rotshild headers:
    *shot_place - to inform the clients about the shot location.
    *hit_hp - because if a client got hit he should know how much HP to take down.
    *shooter_id - for the clients to ignore self-fire.
    :param shot_place: <Tuple> the place of the shot as (X,Y).  [X and Y are str]
    :param hp: <String> the amount of heal point the shot takes down if hit.
    :param shooter_id: <String> the ID of the shooter client.
    :return: <String> Rotshild headers to describe the shot status - shot_place, hit_hp, shooter_id.
    """

    # now the shot_place it a tuple of strings, and when casting it to str it will be like - "('1', '1')".
    # So changing it to be '(1,1)'
    place = f'({shot_place[0]},{shot_place[1]})'

    return f'shot_place: {shot_place}\r\nhit_hp: {hp}\r\n\r\nshooter_id: {shooter_id}\r\n'


def handle_dead(dead_id: str, user_name: str, connector, cursor) -> str:
    """
    Deleting the dead client from PLAYER_PLACES_BY_ID dict and from the CLIENTS_ID_IP_PORT_NAME list,
    and initializing the inventory (the DB values but for user_name and password) to default.
    :param dead_id: <String> the ID of the dead client
    :param user_name: <String> the uesr name of the dead client.
    :param connector: the connection object to the DB.
    :param cursor: the cursor object to the DB.
    :return: <String> dead header with the ID of the dead client.
    """

    global CLIENTS_ID_IP_PORT_NAME, PLAYER_PLACES_BY_ID, DEFAULT_WEAPONS, DEFAULT_AMMO, DEFAULT_MED_KITS, \
        DEFAULT_BACKPACK, DEFAULT_PLASTERS, DEFAULT_SHOES, DEFAULT_EXP, FERNET_ENCRYPTION

    # Deleting the dead client from the PLAYER_PLACES_BY_ID dict
    if dead_id in PLAYER_PLACES_BY_ID:
        del PLAYER_PLACES_BY_ID[dead_id]

    # Deleting the dead client from the CLIENTS_ID_IP_PORT_NAME list
    for client_addr in CLIENTS_ID_IP_PORT_NAME:
        if client_addr[0] == dead_id:  # client_addr[0] is the ID of the client
            CLIENTS_ID_IP_PORT_NAME.remove(client_addr)
            break

    # random a new respawn location
    respawn_place = random_respawn_place()

    # encrypting the data to be saved (and hashing the password)
    encrypted_default_weapons = FERNET_ENCRYPTION.encrypt(DEFAULT_WEAPONS.encode('utf-8'))
    encrypted_default_ammo = FERNET_ENCRYPTION.encrypt(str(DEFAULT_AMMO).encode('utf-8'))
    encrypted_default_med_kits = FERNET_ENCRYPTION.encrypt(str(DEFAULT_MED_KITS).encode('utf-8'))
    encrypted_default_backpack = FERNET_ENCRYPTION.encrypt(str(DEFAULT_BACKPACK).encode('utf-8'))
    encrypted_default_plasters = FERNET_ENCRYPTION.encrypt(str(DEFAULT_PLASTERS).encode('utf-8'))
    encrypted_default_shoes = FERNET_ENCRYPTION.encrypt(str(DEFAULT_SHOES).encode('utf-8'))
    encrypted_default_exp = FERNET_ENCRYPTION.encrypt(str(DEFAULT_EXP).encode('utf-8'))
    encrypted_respawn_place = FERNET_ENCRYPTION.encrypt(str(respawn_place).replace("'", '').replace(' ', '')
                                                        .encode('utf-8'))

    # Initializing the inventory (the DB values but for user_name, password and coins) to default
    client_update = (encrypted_default_weapons,
                     encrypted_default_ammo,
                     encrypted_default_med_kits,
                     encrypted_default_backpack,
                     encrypted_default_plasters,
                     encrypted_default_shoes,
                     encrypted_default_exp,
                     encrypted_respawn_place)
    cursor.execute("UPDATE clients_info"
                   " SET weapons = ?,"
                   " ammo = ?,"
                   " med_kits = ?,"
                   " backpack = ?,"
                   " plasters = ?,"
                   " shoes = ?,"
                   " exp = ?,"
                   " respawn_place = ?"
                   " WHERE user_name = ?", client_update + (user_name.encode('utf-8'),))
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

    # now the place it a tuple of strings, and when casting it to str it will be like - "('1', '1')".
    # So changing it to be '(1,1)'
    place = f'({place[0]},{place[1]})'

    # returning Rotshild headers with values according to the player's movement
    return 'player_place: {}\r\nmoved_player_id: {}\r\nimage: {}\r\n'.format(place, id, image)


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
        # in this header clients should check the shooter_id so they wont take self-fire.
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

        # --------------
        elif line_parts[0] == 'disconnect:':
            # open db connector and cursor if not open already
            if not (connector and cursor):
                connector, cursor = connect_to_db_and_build_cursor()

            if user_name_cache == '':
                if id_cache == '':
                    id_cache = line_parts[1]
                for client in CLIENTS_ID_IP_PORT_NAME:
                    if client[0] == id_cache:
                        user_name_cache = client[3]
                        break
            reply_rotshild_layer += handle_disconnect(id_cache, user_name_cache, connector, cursor)
        # --------------

        # --------------
        elif line_parts[0] == 'dead:':
            # open db connector and cursor if not open already
            if not (connector and cursor):
                connector, cursor = connect_to_db_and_build_cursor()

            if user_name_cache == '':
                if id_cache == '':
                    id_cache = line_parts[1]
                for client in CLIENTS_ID_IP_PORT_NAME:
                    if client[0] == id_cache:
                        user_name_cache = client[3]
                        break
            reply_rotshild_layer += handle_dead(id_cache, user_name_cache, connector, cursor)
        # --------------

        # --------------
        elif line_parts[0] == 'hit_an_enemy:':
            if id_cache == '':
                id_cache = lines[0].split()[1]
            handle_locking_on_enemy(line_parts[1], id_cache)
        # --------------

    if not individual_reply:
        # sending the reply to all active clients
        for client in CLIENTS_ID_IP_PORT_NAME:
            server_socket.sendto(reply_rotshild_layer.encode('utf-8'), (client[1], int(client[2])))

    else:
        # sending the reply to the specific client
        server_socket.sendto(reply_rotshild_layer.encode('utf-8'), (src_ip, int(src_port)))

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
    return payload[:len(expected)] == expected


def verify_and_handle_packet_thread(payload: bytes, src_addr: tuple, server_socket: socket):
    """
    Checking on encoded data if it's a Rotshild protocol packet.
    Then (if not register request) verifies match of src IP-PORT-ID.
    If all good then handling the packet.
    :param payload: <Bytes> the payload received.
    :param src_addr: <Tuple> the source address of the packet as (IP, PORT).  [IP is str and PORT is int]
    :param server_socket: <Socket> the socket object of the server.
    """

    global PRIVATE_KEY, SERVER_SOCKET_TIMEOUT

    # I'm doing a general exception handling because this method is a new thread and exceptions raised here will
    # not be cought in the main.
    try:
        if rotshild_filter(payload):  # checking on encoded data if it's a Rotshild protocol packet
            plaintext = payload.decode('utf-8')
            # handling packet if ID-IP-PORT matches or if register request
            if plaintext[9] == '\r' or check_if_id_matches_ip_port(plaintext.split('\r\n')[0].split()[1],
                                                                   src_addr[0],
                                                                   str(src_addr[1])):
                packet_handler(plaintext, src_addr[0], str(src_addr[1]), server_socket)  # handling the packet

    except Exception as ex:
        CLOSING_THREADS_EVENT.set()  # setting the event of closing worker threads (for user input thread to terminate)
        print(">> ", end='')
        print_ansi(text='[ERROR] ', color='red', blink=True, bold=True, new_line=False)
        print_ansi(text=f"Something went wrong (on a packet thread)... This is the error message: {ex}", color='red')
        print(">> ", end='')
        print_ansi(text=f'Server crashed. closing it... (it may take up to about {str(SERVER_SOCKET_TIMEOUT)} seconds)',
                   color='blue')

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
    sys.stdout.flush()  # force flushing the buffer to the terminal
    try:
        for client in CLIENTS_ID_IP_PORT_NAME:
            server_socket.sendto((ROTSHILD_OPENING_OF_SERVER_PACKETS + f'server_shutdown: {reason}\r\n').encode('utf-8')
                                 , (client[1], int(client[2])))
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

    global SHUTDOWN_TRIGGER_EVENT, SERVER_SOCKET_TIMEOUT, DB_PATH, CLIENTS_ID_IP_PORT_NAME, FERNET_ENCRYPTION, \
        CLOSING_THREADS_EVENT, SYS_PLATFORM, ROTSHILD_OPENING_OF_SERVER_PACKETS, PLAYER_PLACES_BY_ID

    # I'm doing a general exception handling because this method is a new thread and exceptions raised here will
    # not be cought in the main.
    try:
        def get_input_win(timeout: float = None) -> tuple:
            """
            Getting a timed out input for Windows platforms.
            :param timeout: <Float> the timeout to wait for input. (by default blocking forever)
            :return: <Tuple> the input and a boolean to represent if its a full finished line or not.
            """
            input_string = ''  # Create an empty string to hold the input characters
            start_time = time.time()  # Record the start time of the input loop
            while True:  # Loop until input is received or the timeout expires
                if msvcrt.kbhit():  # Check if there is keyboard input waiting to be read
                    char = msvcrt.getche()  # Read a single character from the keyboard buffer (and removing it)
                    if char == b'\r':  # If Enter key is pressed
                        print()
                        return input_string, True  # Return the input string and flag indicating that input is complete
                    elif char == b'\x03':  # If Ctrl+C is pressed (its a keyboard interrupt)
                        raise KeyboardInterrupt  # Raise a KeyboardInterrupt exception
                    elif char == b'\x08':  # If backspace key is pressed
                        print(' \b', end='', flush=True)  # clear last character from screen and move cursor back.
                        # the last line assumes that the terminal will move the cursor back by its own after
                        # pressing backspace but wont delete the char (because that is what my terminal does),
                        # but it might be different in different terminals. In some terminals it might do nothing
                        # visible on the screen, but the program will see it like the last char was deleted,
                        # so it wont effect the functionality of the code. It may only confuse the user because he
                        # will see like it didn't delete anything while it does.
                        if input_string != '' and input_string[len(input_string) - 1] != '\x08':  # if it is not empty
                            input_string = input_string[:-1]  # remove last character
                        else:
                            input_string += '\x08'
                    else:
                        try:
                            input_string += char.decode('utf-8')  # Add the character to the input string
                        except UnicodeDecodeError:
                            input_string = ''  # clearing input string
                            print('\b \b', end='', flush=True)  # clear last character from screen and move cursor back.
                            # (in my terminal a trash char is being printed to the screen. that's why the previous line)
                            print("\n>> ", end='')
                            print_ansi(text="You pressed a character that is not available on this program.\n",
                                       color='red')
                            # flushing the input buffer although it should be clean (because the msvcrt.getche() is
                            # popping the char from the buffer). But I still do it because in some cases there will be
                            # more then one char and we wont read the second one (like for example, in my terminal, when
                            # pressing an arrow key it saves to the buffer 2 chars, the first one is handled in the
                            # UnicodeDecodeError exception block, but then we need to check the second one too...)
                            while msvcrt.kbhit():
                                msvcrt.getch()  # Read and discard any remaining characters in the input buffer

                # If timeout is set and the timeout period has elapsed
                elif timeout is not None and (time.time() - start_time) > timeout:
                    return input_string, False  # Return the input string and a flag indicating that input is incomplete
                time.sleep(0.1)  # to prevent waisting CPU cycles

        def get_input_unix(timeout: float = None) -> tuple:
            """
            Getting a timed out input for UNIX-like platforms.
            :param timeout: <Float> the timeout to wait for input. (by default blocking forever)
            :return: <Tuple> the input and a boolean to represent if its a full finished line or not.
            """
            # Getting lists of file descriptors to monitor for read, write and execute events. (SYS CALL)
            # in our case we will get just the stdin file descriptor, when it is ready to read a full line from.
            # all in all in this line we wait 'timeout' seconds for input. it will exit before then if entered '\n'
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if rlist[0]:
                # there is input available in the stdin buffer
                # reading the input (not removing from the buffer)
                input_string = sys.stdin.read()
                # checking if there was a full finished line
                if '\n' in input_string:
                    print()
                    termios.tcflush(sys.stdin, termios.TCIFLUSH)  # flushing the input buffer
                    # [:-1] will remove the newline character.
                    return input_string[:-1], True
                termios.tcflush(sys.stdin, termios.TCIFLUSH)  # flushing the input buffer
                return input_string, False
            return '', True

        unfinished_buffer = ''  # will save the unfinished messages

        # wrapper to get the right method
        if SYS_PLATFORM == 'posix':
            # if UNIX-like (Linux, MAC...)
            import termios
            import select
            get_input = get_input_unix
        elif SYS_PLATFORM == 'nt':
            # if Windows
            import msvcrt
            import time
            get_input = get_input_win
        else:
            # if unsupported platform. trying with the unix method and printing a warning
            print(">> ", end='')
            print_ansi(text='[WARNING] ', color='yellow', blink=True, new_line=False)
            print_ansi(text="The user UI commends may not works on your platform. You can try, but it may act "
                            "unexpectedly.\n", color='yellow')
            import termios
            import select
            get_input = get_input_unix

        while not CLOSING_THREADS_EVENT.is_set():
            # ------------------ Take input
            # its the same timeout like the socket without a reason, just for order with the error messages
            commend, finished_flag = get_input(SERVER_SOCKET_TIMEOUT)
            # handle backspace
            while '\x08' in commend:
                commend = commend[1:]  # remove backspace character
                if unfinished_buffer != '':
                    unfinished_buffer = unfinished_buffer[:-1]  # remove last character
            # chack is finished line
            if finished_flag is False:
                unfinished_buffer += commend
                continue
            commend = (unfinished_buffer + commend).strip().lower()
            unfinished_buffer = ''
            # -------------------

            # -------------------
            if commend == 'shutdown':
                print(">> ", end='')
                print_ansi(
                    text=f'Shutting down the server... (it may take up to about {str(SERVER_SOCKET_TIMEOUT)} seconds)',
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
                    for i in range(len(cursor.description) - 1):
                        if i != 1:
                            fields.append(cursor.description[i][0].replace('_', ' ').title())
                        else:
                            fields.append("Password (hashed)")
                    table.field_names = fields
                    # adding rows
                    for row in rows:
                        row = list(row)
                        del row[len(row) - 1]  # the respawn place
                        for i in range(len(row)):
                            if i != 0 and i != 1:
                                row[i] = FERNET_ENCRYPTION.decrypt(row[i]).decode('utf-8')
                        row[0] = row[0].decode('utf-8')  # the user_name
                        row[1] = '* * * * * * * *'  # the password
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
                cursor.execute("SELECT * FROM clients_info WHERE user_name=?", (user_name.encode('utf-8'),))
                row = cursor.fetchone()

                # if user name exists
                if row:
                    # check if user name is active
                    for client in CLIENTS_ID_IP_PORT_NAME:
                        if client[3] == user_name:
                            print(">> ", end='')
                            print_ansi(text=f"Client '{user_name}' is currently active on the server. disconnecting him"
                                            f" first...", color='blue')
                            print_ansi(text="   [Disconnecting the client from the game]", new_line=False, color='cyan')
                            sys.stdout.flush()  # force flushing the buffer to the terminal

                            client_id = client[0]
                            # disconnecting the clients from the game
                            # ---------------------
                            # Deleting the dead client from the PLAYER_PLACES_BY_ID dict
                            if client_id in PLAYER_PLACES_BY_ID:
                                del PLAYER_PLACES_BY_ID[client_id]

                            # Deleting the dead client from the CLIENTS_ID_IP_PORT_NAME list
                            for client_addr in CLIENTS_ID_IP_PORT_NAME:
                                if client_addr[0] == client_id:  # client_addr[0] is the ID of the client
                                    CLIENTS_ID_IP_PORT_NAME.remove(client_addr)
                                    break

                            # informing all other clients
                            layer = ROTSHILD_OPENING_OF_SERVER_PACKETS + 'disconnect: ' + client_id + '\r\n'
                            for player in CLIENTS_ID_IP_PORT_NAME:
                                server_socket.sendto(layer.encode('utf-8'), (player[1], int(player[2])))
                            # ---------------------

                            print_ansi(text=' ------------------------> completed', color='green', italic=True)

                    # deleting the clients from the server DB
                    cursor.execute("DELETE FROM clients_info WHERE user_name=?", (user_name.encode('utf-8'),))
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
                    sys.stdout.flush()  # force flushing the buffer to the terminal
                    try:
                        os.remove(DB_PATH)
                        print_ansi(text=' -------------------------> completed', color='green', italic=True)
                    except Exception as ex:
                        print_ansi(text=f' -------------------------> failed [{ex}]', color='red', italic=True)

                    # creating a new empty DB
                    print_ansi(
                        text="   [Creating a new empty DB ('Server_DB.db' file) and initializing an empty table]",
                        new_line=False, color='cyan')
                    sys.stdout.flush()  # force flushing the buffer to the terminal
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
        print_ansi(text=f'Server crashed. closing it... (it may take up to about {str(SERVER_SOCKET_TIMEOUT)} seconds)',
                   color='blue')

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

    global DB_ACCESS_PERMISSION, DB_PATH, SYS_PLATFORM

    try:
        if SYS_PLATFORM == "posix" or SYS_PLATFORM == 'nt':
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


def retrieve_fernet_key_from_keyring():
    """
    Searches in the for a password (or key) that has the matching service_name and username values as the args,
    and setting a Fernet object with the corresponding encryption key.
    If there is no match it create a new random key with these identifiers and saving it with 5 more fake ones.
    """

    global FERNET_ENCRYPTION, FERNET_KEY_USERNAME, FAKE_FERNET_KEY_1, FAKE_FERNET_KEY_2, FAKE_FERNET_KEY_3, \
        FAKE_FERNET_KEY_4, FAKE_FERNET_KEY_5, SERVICE_NAME

    keyring = MyKeyring.MyKeyring()  # initializing a MyKeyring object in th same directory as the script

    key = keyring.get_password(SERVICE_NAME, FERNET_KEY_USERNAME)
    if key is None:
        # Generating a new encryption key and 5 fake ones and store them in the keyring in random order
        user_names = [FERNET_KEY_USERNAME, FAKE_FERNET_KEY_1, FAKE_FERNET_KEY_2, FAKE_FERNET_KEY_3,
                      FAKE_FERNET_KEY_4, FAKE_FERNET_KEY_5]
        for _ in range(len(user_names)):
            index = randint(0, len(user_names) - 1)
            key = Fernet.generate_key().decode('utf-8')
            keyring.set_password(SERVICE_NAME, user_names[index], key)
            if index == 0:
                # setting a Fernet object with the real key
                FERNET_ENCRYPTION = Fernet(key.encode('utf-8'))
            del user_names[index]
    else:
        # setting a Fernet object with the real key
        FERNET_ENCRYPTION = Fernet(key.encode('utf-8'))


def initialize_sqlite_rdb():
    """
    Creating a table of clients_info (if doesn't exist). (also creating the DB file if not exists).
    """

    connection, cursor = connect_to_db_and_build_cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS clients_info"  # creating a table of clients data if not exists yet
                   " (user_name BLOB PRIMARY KEY,"
                   " hashed_password BLOB,"
                   " weapons BLOB,"  # to store separated by ',' like- 'sniper,AR,sword' [can be: stick,sniper,AR,sword]
                   " ammo BLOB,"
                   " med_kits BLOB,"
                   " backpack BLOB,"
                   " plasters BLOB,"
                   " shoes BLOB,"
                   " exp BLOB,"
                   " respawn_place BLOB)")
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
                        if response.json()['ip'] != '':  # some APIs may reply with empty strings
                            return response.json()['ip']
                    # response is plaintext
                    if response.text.strip() != '':  # some APIs may reply with empty strings
                        return response.text.strip()
            except:
                pass
    # ----------------

    # If all failed
    return "[Your public IP (our system couldn't find it)]"


def get_private_ip() -> str:
    """
    Getting the private IP of the machine.
    :return: <String> the private IP address.
    """

    global SYS_PLATFORM

    # -------------------
    # If its a Windows Operating System
    try:
        # if windows
        if SYS_PLATFORM == 'nt':
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

    return "[Your private IP (our system couldn't find it)]"


def print_start_info_and_running_status():
    """
    Printing start info and running status
    """

    # -------------------------------------------------- trying to get the runner machine's IP addresses
    my_public_ip = get_public_ip()
    my_private_ip = get_private_ip()
    # --------------------------------------------------

    # -------------------------------------------------- Printing start info and running status
    print_ansi(text='---------------------------------------------------------',
               color='magenta', italic=True, bold=True)
    print(">> ", end='')
    print_ansi(text='NOTE: ', new_line=False, color='magenta', italic=True, bold=True)
    print_ansi(text='The server requires your network to have port forwarding\n'
                    f'         to route from UDP port {str(SERVER_UDP_PORT)} to your local IP if you want\n'
                    '         it to be available for clients from WAN (outside your network).\n'
                    '         If you only run it for players on your LAN then this is not a mandatory requirement for'
                    ' you.\n'
               , color='magenta', italic=True)
    print(">> ", end='')
    print_ansi(text='NOTE: ', new_line=False, color='magenta', italic=True, bold=True)
    print_ansi(text='The server was designed to run on Windows or UNIX-like (Linux, MAC...) platforms, and checked only'
                    ' on Windows.\n         We can only be sure it works the best on Windows, any other platform wasnt '
                    'checked.\n', color='magenta', italic=True)
    print(">> ", end='')
    print_ansi(text='Server is up and running on:', color='magenta', italic=True, bold=True)
    if my_public_ip == "[Your public IP (our system couldn't find it)]":
        # explanation for this if is in the next if (a few lines down)
        print_ansi(text=f'   - For WAN clients - ', new_line=False, color='magenta', italic=True)
        print_ansi(text=f'{my_public_ip}', new_line=False, color='red', italic=True, bold=True)
        print_ansi(text=f':{str(SERVER_UDP_PORT)}\n   - For LAN clients - ',
                   new_line=False, color='magenta', italic=True)
        print_ansi(text=f'{my_private_ip}', new_line=False, color='yellow', italic=True)
        print_ansi(text=f':{str(SERVER_UDP_PORT)}\n', color='magenta', italic=True)
    else:
        print_ansi(text=f'   - For WAN clients - ', new_line=False, color='magenta', italic=True)
        print_ansi(text=f'{my_public_ip}', new_line=False, color='green', italic=True)
        print_ansi(text=f':{str(SERVER_UDP_PORT)}\n   - For LAN clients - ',
                   new_line=False, color='magenta', italic=True)
        print_ansi(text=f'{my_private_ip}', new_line=False, color='green', italic=True)
        print_ansi(text=f':{str(SERVER_UDP_PORT)}\n', color='magenta', italic=True)
    print('    ', end='')
    print_ansi(text='NOTE:', new_line=False, color='magenta', italic=True, bold=True)
    print_ansi(text=" It's important that clients on your network will enter the game by the private IP\n"
                    "         (the one for LAN clients), and clients outside your network will enter by the public IP\n"
                    "         (the one for WAN clients).", color='magenta', italic=True)

    if not my_private_ip == "[Your private IP (our system couldn't find it)]" \
            and my_public_ip == "[Your public IP (our system couldn't find it)]":
        # If got here, there is no connection to WAN but there is a private IP.
        # probably in that case there is also no Networks connection (LAN) at all (in most cases...).
        # Sometimes even if you are not connected to the internet or a local network, your system may still have a
        # network interface configured with a private IP address. This could happen if your system was previously
        # connected to a network and the IP address was not released when the network connection was terminated.
        # In this case, you may be able to bind a private IP address to a socket, but you will not be able to
        # communicate with other devices over the network.
        # So I'm printing a warning that the private IP might not be True and clients might not be able to connect.

        print("\n>> ", end='')
        print_ansi(text='[WARNING] ', color='yellow', blink=True, new_line=False)
        print_ansi(text='There might be a problem with your internet network connection.\n'
                        '   Seems like you got a private IP but not a public one.\n'
                        "   Usually cases like this are a result of a previous connection that the operating system"
                        " didn't realesed its IP when the connection terminated.\n   ",
                   color='yellow', new_line=False)
        print_ansi(text='In that case clients will not be able to connect to you.',
                   color='yellow', underline=True, new_line=False)
        print_ansi(text=' You might want to check your network connection...', color='yellow')

    print_ansi(text="---------------------------------------------------------\n",
               color='magenta', italic=True, bold=True)
    # --------------------------------------------------


def initialize_global_system_consts():
    """
    Initializing the global vars related to the OS and file paths for example with the correct data about this machine.
    """

    global SYS_PLATFORM, SCRIPT_PATH, SCRIPT_DIR, DB_FILE, DB_PATH, DB_ACCESS_PERMISSION

    SYS_PLATFORM = os.name  # The operating system of the machine (will be 'nt' for windows or 'posix' for Unix-like)
    if SYS_PLATFORM != 'nt' and SYS_PLATFORM != 'posix':
        print("\n>> ", end='')
        print_ansi(text='[WARNING] ', color='yellow', blink=True, new_line=False)
        print_ansi(text="Seems like your platform is not Windows or UNIX-like (Linux, MAC...) system.\n"
                        '   The program designed to run on these systems (better on Windows) and it may act in an '
                        'unexpected manner on your system.', color='yellow')
    SCRIPT_PATH = os.path.abspath(__file__)
    SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
    DB_FILE = "Server_DB.db"
    DB_PATH = os.path.join(SCRIPT_DIR, DB_FILE)
    DB_ACCESS_PERMISSION = 0o600  # The access permission for the  DB file in both UNIX-like and Windows Operating Systems
    # (0o600 - means read and write access only for the owner)


def store_all_respawn_places():
    """
    Storing in the DB the current places of all the active clients on the map (for respawn later)
    """

    global CLIENTS_ID_IP_PORT_NAME, PLAYER_PLACES_BY_ID, FERNET_ENCRYPTION

    connector, cursor = connect_to_db_and_build_cursor()
    for client in CLIENTS_ID_IP_PORT_NAME:
        client_id = client[0]
        client_user_name = client[3]
        cursor.execute("UPDATE clients_info SET respawn_place = ? WHERE user_name = ?",
                       (FERNET_ENCRYPTION.encrypt(str(PLAYER_PLACES_BY_ID[client_id]).replace("'", '').replace(' ', '')
                                                  .encode('utf-8')), client_user_name.encode('utf-8')))
    connector.commit()
    close_connection_to_db_and_cursor(connector, cursor)


def main():
    global SERVER_IP, SERVER_UDP_PORT, SOCKET_BUFFER_SIZE, SHUTDOWN_TRIGGER_EVENT, SERVER_SOCKET_TIMEOUT, \
        SHUTDOWN_INFORMING_EVENT, CLOSING_THREADS_EVENT

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
        # initializing global vars related to the OS and file paths for example with the correct data about this machine
        initialize_global_system_consts()
        # setting a socket object of AF_INET (IPv4) and SOCK_DGRAM (UDP) with timeout SERVER_SOCKET_TIMEOUT
        server_socket = set_socket()
        # initializing the SQL (SQLite) DataBase
        initialize_sqlite_rdb()
        # retrieving the Fernet encryption key (for the DB) from the keyring and setting a Fernet object with it
        retrieve_fernet_key_from_keyring()
        # initializing a thread pool executor object
        # I don't set max_workers so it will use the numer of CPU cores on my machine.
        executor = ThreadPoolExecutor(thread_name_prefix='worker_thread_')
        # --------------------------------------------------

        print_start_info_and_running_status()

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

        # setting a thread to handle user's terminal commends
        executor.submit(check_user_input_thread, server_socket)

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # ==============================================| GAME LOOP |=============================================# !!
        while not SHUTDOWN_TRIGGER_EVENT.is_set():  # !!
            first_player_locked_on()
            try:  # !!
                data, client_address = server_socket.recvfrom(SOCKET_BUFFER_SIZE)  # getting incoming packets     # !!
            except socket_timeout:  # !!
                continue  # !!
                # !!
            # verify the packet in a different thread and if all good then handling it in another thread          # !!
            executor.submit(verify_and_handle_packet_thread, data, client_address, server_socket)  # !!
        # ========================================================================================================# !!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    except OSError as ex:
        CLOSING_THREADS_EVENT.set()  # setting the event of closing worker threads (for user input thread to terminate)
        if ex.errno == 98 or ex.errno == 10048:
            # In UNIX-like operating systems error number 98 is what in windows specifies by error number 10048.
            # (in windows its Error-'WSAEADDRINUSE' and in UNIX-like - 'EADDRINUSE')
            # (it means address is in use by another process and not free to bind)
            print(">> ", end='')
            print_ansi(text='[ERROR] ', color='red', blink=True, bold=True, new_line=False)
            print_ansi(text=f"Port {str(SERVER_UDP_PORT)} is not available on your machine.\n"
                            "    Make sure the port is available and is not already in use by another service and run again.",
                       color='red')
            print(">> ", end='')
            print_ansi(
                text=f'Server is shutting down... (it may take up to about {str(SERVER_SOCKET_TIMEOUT)} seconds)',
                color='blue')
            # don't have clients to inform so setting the event
            SHUTDOWN_INFORMING_EVENT.set()
        else:
            print(">> ", end='')
            print_ansi(text='[ERROR] ', color='red', blink=True, bold=True, new_line=False)
            print_ansi(text=f"Something went wrong (on main thread)... This is the error message: {ex}", color='red')
            print(">> ", end='')
            print_ansi(
                text=f'Server crashed. closing it... (it may take up to about {str(SERVER_SOCKET_TIMEOUT)} seconds)',
                color='blue')
            inform_active_clients_about_shutdown(server_socket, 'error')

    except Exception as ex:
        CLOSING_THREADS_EVENT.set()  # setting the event of closing worker threads (for user input thread to terminate)
        print(">> ", end='')
        print_ansi(text='[ERROR] ', color='red', blink=True, bold=True, new_line=False)
        print_ansi(text=f"Something went wrong (on main thread)... This is the error message: {ex}", color='red')
        print(">> ", end='')
        print_ansi(text=f'Server crashed. closing it... (it may take up to about {str(SERVER_SOCKET_TIMEOUT)} seconds)',
                   color='blue')
        inform_active_clients_about_shutdown(server_socket, 'error')

    finally:
        SHUTDOWN_INFORMING_EVENT.wait()  # wait for informing to complete

        print_ansi(text='   [waiting for running threads to complete]', new_line=False, color='cyan')
        sys.stdout.flush()  # force flushing the buffer to the terminal
        if executor:  # if there is an executor up
            # the next commend waits for all running tasks to complete (blocking till then), shuts down the
            # tread pool executor and frees up any resources used by it.
            executor.shutdown(wait=True)
        print_ansi(text=' -----------> completed', color='green', italic=True)

        print_ansi(text='   [storing respawn locations of active players]', new_line=False, color='cyan')
        sys.stdout.flush()  # force flushing the buffer to the terminal
        # if this exists, it means all initializations till retrieve_fernet_key_from_keyring were successfully executed
        if FERNET_ENCRYPTION:
            store_all_respawn_places()
        print_ansi(text=' -------> completed', color='green', italic=True)

        print_ansi(text='   [freeing up last resources]', new_line=False, color='cyan')
        sys.stdout.flush()  # force flushing the buffer to the terminal
        # if there is a socket up, closing it
        if server_socket:
            server_socket.close()
        # stop using colorama. restore stduot and stderr to original values (terminal)
        colorama.deinit()
        # unset all events
        SHUTDOWN_TRIGGER_EVENT.clear()
        SHUTDOWN_INFORMING_EVENT.clear()
        CLOSING_THREADS_EVENT.clear()
        print_ansi(text=' -------------------------> completed', color='green', italic=True)

        print(">> ", end='')
        print_ansi(text='Server is closed.', color='green', italic=True)


# --------------------------- Main Guard
if __name__ == '__main__':
    main()
# ---------------------------
