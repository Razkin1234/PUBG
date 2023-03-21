import pygame, sys
from settings import *
from level import Level
from button import Button
import socket
from Incoming_packets import Incoming_packets
from Connection_to_server import Connection_to_server
from concurrent.futures import ThreadPoolExecutor

def give_me_first_place(packet):
    lines = packet.get_packet().split('\r\n')
    while '' in lines:
        lines.remove('')
    for line in lines:
        line_parts = line.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]
        if line_parts[0] == 'first_inventory:':
            place_to_start = packet.handle_first_place(line_parts[1])
            return place_to_start

def handeler_of_incoming_packets(packet, screen):
    lines = packet.get_packet().split('\r\n')
    while '' in lines:
        lines.remove('')
    for line in lines:
        line_parts = line.split()  # opening line will be - ['Rotshild',ID], and headers - [header_name, info]

        # Recognize and handle each header
        # -------------
        if packet.get_packet() != "":
            if line_parts[0] == 'login_status:':
                answer = packet.handle_login_status(line_parts[1])  # returning a tuple (True/False, answer)
                if not answer[0]:
                    # here print to the screen like what is in the value answer[1]
                    screen.fill('black')
                    text_surf = pygame.font.Font(UI_FONT, 150).render(answer[1], True, TEXT_COLOR)
                    text_rect = text_surf.get_rect(center=(MIDDLE_SCREEN[0], MIDDLE_SCREEN[1] - 250))  # the bar
                    screen.blit(text_surf, text_rect)
                    return -1, False
                else:
                    # here convert what is in answer[1] to integer because it's your new id and put it in your player object
                    return answer[1], True

            elif line_parts[0] == 'register_status:':
                answer = packet.handle_register_status(line_parts[1])
                if not answer[0]:
                    screen.fill('black')
                    text_surf = pygame.font.Font(UI_FONT, 150).render(answer[1], True, TEXT_COLOR)
                    text_rect = text_surf.get_rect(center=(MIDDLE_SCREEN[0], MIDDLE_SCREEN[1] - 250))  # the bar
                    screen.blit(text_surf, text_rect)
                    return False
                else:
                    return True
        # go back to opening page
        # --------------
        # --------------


class Game:
    def __init__(self):

        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption('PUBG')
        self.clock = pygame.time.Clock()

        self.level = None
        self.font = pygame.font.Font(UI_FONT, 18)  # our font
        self.display_surface = pygame.display.get_surface()
        self.user_name = ''
        self.passward = ''
        self.server_ip = ''
        self.player_id = ''
        # ------------------- Socket
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.my_socket.settimeout(5)


    def run(self):
        pygame.init()
        self.screen.fill('black')
        self.main_menu()

    def main_menu(self):
        """
		the main menu screen creator
		:return:
		"""
        pygame.display.set_caption('menu')
        text_color = TEXT_COLOR
        ID_input_rect = pygame.Rect((550, 240), (160, 32))
        passward_input_rect = pygame.Rect((550, 290), (160, 32))
        server_input_rect = pygame.Rect((550, 340), (260, 32))
        active_ID = False
        active_pasward = False
        active_server = False
        play_button = Button(None,  # create the play button
                             (640, 450), "play", pygame.font.Font(UI_FONT, 50), TEXT_COLOR, "yellow")

        sign_up_button = Button(None, (550, 240), "sign up", pygame.font.Font(UI_FONT, 50), TEXT_COLOR, "yellow")
        log_in_button = Button(None, (550, 410), "log in", pygame.font.Font(UI_FONT, 50), TEXT_COLOR, "yellow")
        sign_in = False
        log_in = False
        check = True
        pushed = True
        while True:
            self.display_surface.fill('black')

            mouse_menu = pygame.mouse.get_pos()
            text_surf = pygame.font.Font(UI_FONT, 150).render('PUBG', True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=(MIDDLE_SCREEN[0], MIDDLE_SCREEN[1] - 250))  # the bar
            self.display_surface.blit(text_surf, text_rect)

            for event in pygame.event.get():  # check the events

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:  # check if he clicked the mouse

                    if ID_input_rect.collidepoint(event.pos):
                        active_ID = True
                        active_pasward = False
                        active_server = False

                    if passward_input_rect.collidepoint(event.pos):
                        active_pasward = True
                        active_ID = False
                        active_server = False

                    if server_input_rect.collidepoint(event.pos):
                        active_server = True
                        active_ID = False
                        active_pasward = False

                if active_ID:

                    if event.type == pygame.KEYDOWN:

                        if event.key == pygame.K_SPACE:
                            pass

                        elif event.key == pygame.K_BACKSPACE:
                            self.user_name = self.user_name[:-1]
                            text_color = TEXT_COLOR

                        elif len(self.user_name) <= 8:
                            if 'z' >= event.unicode >= 'a' or 'A' >= event.unicode >= 'A' or '9' >= event.unicode >= '0':
                                self.user_name += event.unicode
                                text_color = TEXT_COLOR

                        else:
                            text_color = 'red'

                if active_pasward:

                    if event.type == pygame.KEYDOWN:

                        if event.key == pygame.K_SPACE:
                            pass

                        elif event.key == pygame.K_BACKSPACE:
                            self.passward = self.passward[:-1]
                            text_color = TEXT_COLOR

                        elif len(self.passward) <= 8:
                            if 'z' >= event.unicode >= 'a' or 'A' >= event.unicode >= 'A' or '9' >= event.unicode >= '0':
                                self.passward += event.unicode
                                text_color = TEXT_COLOR

                        else:
                            text_color = 'red'

                if active_server:

                    if event.type == pygame.KEYDOWN:

                        if event.key == pygame.K_SPACE:
                            pass

                        elif event.key == pygame.K_BACKSPACE:
                            self.server_ip = self.server_ip[:-1]
                            text_color = TEXT_COLOR

                        elif len(self.server_ip) <= 20:
                            self.server_ip += event.unicode
                            text_color = TEXT_COLOR

                        else: #makes guy to do a flip
                            text_color = 'red'

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pushed:
                        if sign_up_button.checkForInput(event.pos):
                            sign_in = True
                            pushed = False

                        elif log_in_button.checkForInput(event.pos):
                            sign_in = False
                            log_in = True
                            pushed = False

                    if play_button.checkForInput(event.pos):

                        if len(self.user_name) > 0 and len(self.passward) > 0 and len(self.server_ip) > 0:
                            ####################################################################################################################
                            # FOR REGISTER RECUEST
                            ####################################################################################################################
                            if not log_in and sign_in:
                                # try:
                                print(self.server_ip)
                                print(type(self.server_ip))
                                self.my_socket.connect((self.server_ip, SERVER_PORT))
                                print("connected")
                                send_packet = Connection_to_server(None)
                                send_packet.add_header_register_request(self.user_name, self.passward)
                                self.my_socket.send(send_packet.get_packet().encode('utf-8'))
                                print(send_packet.get_packet())
                                print("sand")
                                # here the tttttl
                                server_reply = self.my_socket.recv(8192)
                                print("recive")
                                print(server_reply)
                                packet = Incoming_packets(server_reply, self.server_ip, None)

                                if packet.rotshild_filter():
                                    check = handeler_of_incoming_packets(packet, self.display_surface)
                                if not check:
                                    sign_in = False
                                    log_in = False
                            # except Exception as e:
                            #    print(e)
                            #    sign_in = False
                            #    log_in = False
                            ####################################################################################################################
                            # FOR LOGIN RECUEST
                            ####################################################################################################################
                            if (sign_in or log_in) and check:
                                # try:
                                if log_in:
                                    self.my_socket.connect((self.server_ip, SERVER_PORT))
                                send_packet = Connection_to_server(None)
                                send_packet.add_header_login_request(self.user_name, self.passward)
                                self.my_socket.send(send_packet.get_packet().encode('utf-8'))
                                # here the tttttl
                                server_reply = self.my_socket.recv(28000)
                                print(server_reply)
                                print("a")
                                packet = Incoming_packets(server_reply, self.server_ip, None)
                                packet_to_save = Incoming_packets(server_reply, self.server_ip, None)
                                packets_to_handle_queue.append(packet_to_save)
                                if packet.rotshild_filter():
                                    self.player_id, check = handeler_of_incoming_packets(packet, self.display_surface)
                                if check:
                                    self.play(packet)  # packet
                            # except Exception as e:
                            # print(e)

            if log_in or sign_in:
                server_text_surface = self.font.render(self.server_ip, True, text_color)
                self.display_surface.blit(server_text_surface, (555, 345))
                pygame.draw.rect(self.display_surface, 'white', server_input_rect, 2)

                pygame.draw.rect(self.display_surface, 'white', passward_input_rect, 2)
                pygame.draw.rect(self.display_surface, 'white', ID_input_rect, 2)
                ID_text_surface = self.font.render(self.user_name, True,
                                                   text_color)  # show text that the player write on the screen
                passward_text_surface = self.font.render(self.passward, True, text_color)

                self.display_surface.blit(passward_text_surface, (555, 295))
                self.display_surface.blit(ID_text_surface, (555, 245))

                play_button.changeColor(mouse_menu)
                play_button.update(self.display_surface)
                pushed = False
            else:

                for button in [sign_up_button, log_in_button]:
                    button.changeColor(mouse_menu)
                    button.update(self.display_surface)
                pushed = True
            pygame.display.update()

    def handle_of_incoming_packets(self):
        while not shut_down_event.is_set():
            server_reply = self.my_socket.recv(8192)
            packet = Incoming_packets(server_reply, self.server_ip, self.player_id)
            packets_to_handle_queue.append(packet)
            print(packet.get_packet())

    # self.my_socket.bind(('0.0.0.0', 62227))
    # -------------------


    def play(self, packet):
        try:
            with ThreadPoolExecutor(thread_name_prefix='worker_thread_') as executor:
                place_to_start = give_me_first_place(packet)
                self.level = Level(place_to_start)
                pygame.display.set_caption('PUBG')
                self.screen.fill('black')
                executor.submit(self.level.handeler_of_incoming_packets, self.level.visble_sprites, self.level.player,
                                self.level.obstacle_sprites, self.level.item_sprites, self.player_id)
                executor.submit(self.level.handeler_of_incoming_packets, self.level.visble_sprites, self.level.player,
                                self.level.obstacle_sprites, self.level.item_sprites, self.player_id)

                packet_to_send = Connection_to_server(self.player_id)

                pygame.display.update()
                self.clock.tick(FPS)
                executor.submit(self.handle_of_incoming_packets)
                print('receiving packets thread started')
                while not shut_down_event.is_set():
                    packet_to_send = Connection_to_server(self.player_id)

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            packet_to_send.add_header_disconnect(self.player_id)
                            self.my_socket.send(packet_to_send.get_packet().encode('utf-8'))
                            packets_to_handle_queue.clear()
                            shut_down_event.set()#for the thread closing
                            pygame.quit()
                            self.my_socket.close()
                            sys.exit()

                    packet_to_send = self.level.run(packet_to_send,self.player_id)
                    self.my_socket.send(packet_to_send.get_packet().encode('utf-8'))
                    pygame.display.update()
                    self.clock.tick(FPS)
        except:
            packet_to_send.add_header_disconnect(self.player_id)
            self.my_socket.send(packet_to_send.get_packet().encode('utf-8'))
            packets_to_handle_queue.clear()
            shut_down_event.set()  # for the thread closing
            pygame.quit()
            self.my_socket.close()
            sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()
