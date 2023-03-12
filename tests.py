import socket

# ------------------- Server address
SERVER_IP = '127.0.0.1'
SERVER_PORT = 56789
# -------------------

# ------------------- Socket
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# -------------------

my_socket.bind(('0.0.0.0', 62227))
my_socket.connect((SERVER_IP, SERVER_PORT))


def wait_for_reply():
    print('waiting for reply...')
    ciphertext_reply = my_socket.recv(8192)
    encoded_reply = ciphertext_reply
    plaintext_reply = encoded_reply.decode('utf-8')
    print('Got reply: \n----------------\n' + plaintext_reply + '\n----------------\n\n\n')


def test_register_request(user_name: str, password: str):
    plaintext = 'Rotshild \r\n' \
                '\r\n' \
                f'register_request: {user_name},{password}\r\n'

    encoded = plaintext.encode('utf-8')

    try:
        payload_bytes = my_socket.send(encoded)
    except Exception as ex:
        print(f'ERROR: {ex}')

    print(f'{str(payload_bytes)} bytes of register_request sent successfully')

    wait_for_reply()


def test_login_request(user_name: str, password: str):
    plaintext = 'Rotshild \r\n' \
                '\r\n' \
                f'login_request: {user_name},{password}\r\n'

    encoded = plaintext.encode('utf-8')

    try:
        payload_bytes = my_socket.send(encoded)
    except Exception as ex:
        print(f'ERROR: {ex}')

    print(f'{str(payload_bytes)} bytes of login_request sent successfully')

    wait_for_reply()


def test_dead(id: str):
    plaintext = f'Rotshild {id}\r\n' \
                '\r\n' \
                f'dead: {id}\r\n'

    encoded = plaintext.encode('utf-8')

    try:
        payload_bytes = my_socket.send(encoded)
    except Exception as ex:
        print(f'ERROR: {ex}')

    print(f'{str(payload_bytes)} bytes od dead sent successfully')


def test_disconnect(id: str):
    plaintext = f'Rotshild {id}\r\n' \
                '\r\n' \
                f'disconnect: {id}\r\n'

    encoded = plaintext.encode('utf-8')

    try:
        payload_bytes = my_socket.send(encoded)
    except Exception as ex:
        print(f'ERROR: {ex}')

    print(f'{str(payload_bytes)} bytes od dead sent successfully')


def test_update_inventory(header_info: str, id: str):
    plaintext = f'Rotshild {id}\r\n' \
                '\r\n' \
                f'inventory_update: {header_info}\r\n'

    encoded = plaintext.encode('utf-8')

    try:
        payload_bytes = my_socket.send(encoded)
    except Exception as ex:
        print(f'ERROR: {ex}')

    print(f'{str(payload_bytes)} bytes of inventory_update sent successfully')


def test_shot_place(place: str, hp: str, id: str):
    plaintext = f'Rotshild {id}\r\n' \
                '\r\n' \
                f'shot_place: {place}\r\n' \
                f'hit_hp: {hp}\r\n'

    encoded = plaintext.encode('utf-8')

    try:
        payload_bytes = my_socket.send(encoded)
    except Exception as ex:
        print(f'ERROR: {ex}')

    print(f'{str(payload_bytes)} bytes of inventory_update sent successfully')

    wait_for_reply()


def test_player_place(place: str, image: str, id: str):
    plaintext = f'Rotshild {id}\r\n' \
                '\r\n' \
                f'player_place: {place}\r\n' \
                f'image: {image}\r\n'

    encoded = plaintext.encode('utf-8')

    try:
        payload_bytes = my_socket.send(encoded)
    except Exception as ex:
        print(f'ERROR: {ex}')

    print(f'{str(payload_bytes)} bytes of inventory_update sent successfully')

    wait_for_reply()


def test_object_update(header_info: str, id: str):
    plaintext = f'Rotshild {id}\r\n' \
                '\r\n' \
                f'object_update: {header_info}\r\n'

    encoded = plaintext.encode('utf-8')

    try:
        payload_bytes = my_socket.send(encoded)
    except Exception as ex:
        print(f'ERROR: {ex}')

    print(f'{str(payload_bytes)} bytes of inventory_update sent successfully')

    wait_for_reply()


# -------------------------------------------------
#test_register_request('user1', 'password1')
test_login_request('user1', 'password1')
#test_update_inventory('+ weapons weapon_name1', '1')
#test_dead('1')
#test_disconnect('1')
#test_shot_place('(1,1)', '8', '1')
#test_player_place('(1,2)', 'image_name', '1')
#test_object_update('drop-ammo-(32845,25492)-7', '1')
#wait_for_reply()
while True:
    wait_for_reply()
# -------------------------------------------------
