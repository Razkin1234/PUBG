from csv import reader
from os import  walk
import  pygame
import csv

def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map , delimiter = ',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map

def import_folder(path):
    surface_list = []
    for _,__,img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list

def get_csv_area(path, loc):
    map = []
    row_start= loc[1]#the row that i will start commiting
    col_start=loc[0]#the col that i will start commiting
    if row_start<=10: #cechks were to start the commit
        row_start =0
    else:
        row_start-=10
    if col_start<=15:
        col_start=0
    else:
        col_start-=15

    with open(path) as file:
        layout = csv.reader(file, delimiter=',')
        for count, row in enumerate(layout):
            try:
                if count >= row_start and count <= row_start+20:
                    map.append(row[col_start:col_start+40])


            except ValueError:
                pass
    return map
def get_player_loc(player_rect): #returnning the player location devide by 64 (the tile number location)
   loc = (player_rect[0]//64,(player_rect[1]//64)+1)
   return loc