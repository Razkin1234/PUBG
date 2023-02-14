import socket
import rsa
from rsa import PublicKey, PrivateKey

# ------------------ RSA encryption
MODULUS = 7202380422720360875138943832989169827593337421340517606000697629974789073279088263129156773084889735203215777657443638346916570347919877966671239593821849  # (not secret)
PUBLIC_EXPONENT = 65537  # (not secret)
PRIVATE_EXPONENT = 2487759366909086609556743084782273179840859044614268230877791053141573463839494045756198356306801278556401491488506285362190686031132636395114287646477909  # (secret)
FIRST_PRIME_FACTOR = 6722171653111129608666978173114450112621458860424439037672507726695639042339185147  # (secret)
SECOND_PRIME_FACTOR = 1071436552707930761066064576213162123693476737940140711087853990359411067  # (secret)

PUBLIC_KEY = PublicKey(MODULUS, PUBLIC_EXPONENT)  # (not secret)
PRIVATE_KEY = PrivateKey(MODULUS, PUBLIC_EXPONENT, PRIVATE_EXPONENT, FIRST_PRIME_FACTOR, SECOND_PRIME_FACTOR)  # (secret)
# -------------------

# ------------------- Server address
SERVER_IP = '127.0.0.1'
SERVER_PORT = 56789
# -------------------

# ------------------- Socket
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# -------------------


my_socket.connect((SERVER_IP, SERVER_PORT))


def wait_for_reply():
    print('waiting for reply...')
    ciphertext_reply = my_socket.recv(1024)
    encoded_reply = rsa.decrypt(ciphertext_reply, PRIVATE_KEY)
    plaintext_reply = encoded_reply.decode('utf-8')
    print('Got reply: \n----------------\n' + plaintext_reply + '\n----------------\n\n\n')


def test_register_request(user_name: str, password: str):
    plaintext = 'Rotshild \r\n' \
                '\r\n' \
                f'register_request: {user_name},{password}\r\n'

    encoded = plaintext.encode('utf-8')

    ciphertext = rsa.encrypt(encoded, PUBLIC_KEY)

    try:
        payload_bytes = my_socket.send(ciphertext)
    except Exception as ex:
        print(f'ERROR: {ex}')

    print(f'{str(payload_bytes)} bytes of register_request sent successfully')

    wait_for_reply()


def test_login_request(user_name: str, password: str):
    plaintext = 'Rotshild \r\n' \
                '\r\n' \
                f'login_request: {user_name},{password}\r\n'

    encoded = plaintext.encode('utf-8')

    ciphertext = rsa.encrypt(encoded, PUBLIC_KEY)

    try:
        payload_bytes = my_socket.send(ciphertext)
    except Exception as ex:
        print(f'ERROR: {ex}')

    print(f'{str(payload_bytes)} bytes of login_request sent successfully')

    wait_for_reply()


def test_dead(id: str, user_name: str):
    plaintext = 'Rotshild \r\n' \
                '\r\n' \
                f'dead: {id}\r\n' \
                f'user_name: {user_name}\r\n'

    encoded = plaintext.encode('utf-8')

    ciphertext = rsa.encrypt(encoded, PUBLIC_KEY)

    try:
        payload_bytes = my_socket.send(ciphertext)
    except Exception as ex:
        print(f'ERROR: {ex}')

    print(f'{str(payload_bytes)} bytes od dead sent successfully')

    wait_for_reply()


def test_update_inventory(header_info: str, user_name: str):
    plaintext = 'Rotshild \r\n' \
                '\r\n' \
                f'inventory_update: {header_info}\r\n' \
                f'user_name: {user_name}\r\n'

    encoded = plaintext.encode('utf-8')

    ciphertext = rsa.encrypt(encoded, PUBLIC_KEY)

    try:
        payload_bytes = my_socket.send(ciphertext)
    except Exception as ex:
        print(f'ERROR: {ex}')

    print(f'{str(payload_bytes)} bytes of inventory_update sent successfully')

    wait_for_reply()


#test_register_request('test1', 'test1')
test_login_request('test1', 'test1')  # BUG: to check if user name already logging before logging in
#test_update_inventory('+ bomb 4', 'test')
#test_dead('2', 'test2')  # BUG: to check if user name exists and active
#wait_for_reply()