# ====================================================PROTOCOL===================================================================================|                                                                                                                |
# * It's a textual protocol                                                                                                                      |
# * The protocol uses encapsulation of type utf-8 (to decode and encode)                                                                         |
#                                                                                                                                                |
# structure - 'Rotshild <ID>/r/n/r/n<headers>End'                                                                                                |
# [ID - an int (from 1 on) that each client gets from the server at the beginning of the connection. Server's ID is 0]                           |
# [each header looks like this: 'header_name: header_info\r\n']                                                                                  |
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
#                                     .  "                                                                                                       |
# ------------------------------------------------------------------                                                                             |
#                                                                                                                                                |
# ------------------------------------------------------------------                                                                             |
# Headers API:                                                                                                                                   |
#             - player_place: ([the X cordinate,[the Y cordinate])                                                     [clients and server send] |
#             - shot_place: ([the X cordinate],[the Y cordinate]) [comes with hit_hp]                                  [clients and server send] |
#             - hit_id: [the ID of the hitted client] [comes with hit_hp]                                              [only server sends]       |
#             - hit_hp: [the amount of heal points to take from a hitted client] [comes with shot_place or hit_id]     [clients ans server send] |
#             - dead: [the ID of the dead client]                                                                      [clients ans server send] |
# ------------------------------------------------------------------                                                                             |
# ===============================================================================================================================================|
from scapy.all import *
from scapy.layers.inet import IP, UDP


def handle_dead(id):
    global CLIENTS_IP # list the saves tuple which contains (ip,port)
    global PLAYER_PLACES_BY_ID # dictionary that saves each player by its id
    global ROTSHILD_OPENING_OF_SERVER_PACKETS  # the beginning of every packet the server sends
    if id in PLAYER_PLACES_BY_ID:  # checking if the id is in the dictionary and if yes deleting him
        PLAYER_PLACES_BY_ID.pop(id)
    for address in CLIENTS_IP:
        send(IP(dst=address[0]) / UDP(dport=address[1]) / Raw((ROTSHILD_OPENING_OF_SERVER_PACKETS + 'dead: ' + id).encode()))


def recognizing_headers(p):
    """
    recognizing the headers and calling to other functions that will deal with a a specific header
    :param p:
    :return:
    """
    headers = p.split('/r/n')
    for line in headers:
        line = line.split()  # line = first place in the list is the name of the header and in the second place there is the info
        # checking which one
        if line[0] == 'player_place:':
            handle_player_place(line[1], headers[0].split()[1])  # headers[0].split()[1]) = id of the sender(client)
        if line[0] == 'shot_place:':
            handle_shot_place(line[1])
        if line[0] == 'dead:':
            handle_dead(line[1])


def main():
    while True:
        packets = sniff(count=1, lfilter=recognizing_headers())


if __name__ == "__main__":
    main()
