import socket
from Incoming_packets import Incoming_packets
from Connection_to_server import Connection_to_server
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.connect(("85.65.29.54", 6789))
print("connected")

send_packet = Connection_to_server(None)
send_packet.add_header_register_request("dfgfgd","dfgh")
my_socket.send(send_packet.get_packet().encode('utf-8'))
print(send_packet.get_packet())
print("sand")