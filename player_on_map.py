import pygame
import math
from all_classes import Main_player

# camera = pygame.math.Vector2((0, 0))
left = 1  # the signal if pressed left on mousebutton
window_width = 1250
window_height = 640
pygame.init()  # so i can use all the functions from pygame
size = (window_width, window_height)  # creating the size
screen = pygame.display.set_mode(size)
pygame.display.set_caption("PUBG")


def moving_the_player(place_of_player, saves_last_mouse_place, player):
    where_x, where_y = pygame.mouse.get_pos()
    # here calculating the line.
    incline = (where_y - place_of_player[1]) / (where_x - place_of_player[0])
    print(incline)
    temp = "{}x".format(incline)

    line = temp + '+' + str(-where_x * incline + where_y)
    print(line)

    ################################
    print_screen(screen)
    mouse_point = pygame.mouse.get_pos()  # the head of the mouse
    print_player(screen, mouse_point)
    saves_last_mouse_place = pygame.mouse.get_pos()


# printing the background of the game
def print_screen(screen):
    image = 'screen.png'
    img = pygame.image.load(image)
    screen.blit(img, (0, 0))
    pygame.display.flip()


def print_player(screen, place_of_player):
    player = pygame.image.load('player.png').convert()  # creating the player
    player.set_colorkey((255, 255, 255))  # printing all the colors except white
    screen.blit(player, place_of_player)  # where i print it
    pygame.display.flip()  # updating the screen


def main():
    place_of_player = [0, 0]
    player = Main_player  # the object of the player
    print_screen(screen)
    print_player(screen, place_of_player)
    saves_last_mouse_place = pygame.mouse.get_pos()
    finish = False
    while not finish:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN \
                    and event.button == left:
                if saves_last_mouse_place != pygame.mouse.get_pos():
                    moving_the_player(place_of_player, saves_last_mouse_place, player)
                    place_of_player = pygame.mouse.get_pos()
                    saves_last_mouse_place = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                finish = True


if __name__ == "__main__":
    main()
