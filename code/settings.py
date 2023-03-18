from collections import deque


# game setup
WIDTH = 1280
HEIGTH = 720
FPS = 60
TILESIZE = 64
MIDDLE_SCREEN = (WIDTH/2, HEIGTH/2)


#server
SERVER_IP = '192.168.172.244'
SERVER_PORT = 56789
packets_to_handle_queue = deque()
#map setup
ROW_LOAD_TILE_DISTANCE = 8  #8 is the good one
COL_LOAD_TILE_DISTANCE = 12  #12 is the good one
ROW_TILES = 450
COL_TILES = 800

#ui
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
UI_FONT = '../graphics/font/joystix.ttf'
UI_FONT_SIZE = 18

# general colors
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'

# ui colors
HEALTH_COLOR = 'red'
ENERGY_COLOR = 'blue'
UI_BORDER_COLOR_ACTIVE = 'gold'

#weapons
weapon_data = {
	'sword': {'cooldown': 100, 'damage': 15,'graphic':'../graphics/weapons/sword/full.png'},
	'lance': {'cooldown': 400, 'damage': 30,'graphic':'../graphics/weapons/lance/full.png'},
	'axe': {'cooldown': 300, 'damage': 20, 'graphic':'../graphics/weapons/axe/full.png'},
	'rapier': {'cooldown': 50, 'damage': 8, 'graphic':'../graphics/weapons/rapier/full.png'},
	'sai': {'cooldown': 200, 'damage': 10, 'graphic':'../graphics/weapons/sai/full.png'},
	'gun': {'cooldown': 80, 'damage': 10, 'graphic':'../graphics/weapons/gun/full.png'}
	}

item_data = {
	'backpack': {'graphic': '../graphics/items/backpack.png'},

	'ammo': {'amount': 20, 'graphic': '../graphics/items/ammo.png'},
	'boots': {'speed': 1, 'graphic': '../graphics/items/boots.png'},
	'medkit': {'health': 50, 'graphic': '../graphics/items/medkit.png'},
	'bendage': {'health': 7, 'graphic': '../graphics/items/bendage.png'}
}
items_add_data = {
            'backpack': {'name': 'backpack','ui':0},
            'ammo': {'name': 'ammo','amount': 1,'ui':0},
            'boots': {'name': 'boots','speed': 1,'ui':0},
            'medkit': {'name': 'medkit','health': 50,'ui':0},
            'bendage': {'name': 'bendage','health': 7,'ui':0}
        } #for all of the items we will have


#magic
magic_data = {
	'flame': {'strength': 5,'cost': 20,'graphic':'../graphics/particles/flame/ferari.png'},
	'heal': {'strength': 20,'cost': 10,'graphic':'../graphics/particles/heal/teleport.png'},
	'shield': {'strength': 20,'cost': 10,'graphic':'../graphics/particles/shield/shield.png'}}

#enemy
monster_data = {
	'squid': {'health': 100,'exp':100,'damage':20,'attack_type': 'slash', 'attack_sound':'../audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 80, 'notice_radius': 360},
	'raccoon': {'health': 300,'exp':250,'damage':40,'attack_type': 'claw',  'attack_sound':'../audio/attack/claw.wav','speed': 2, 'resistance': 3, 'attack_radius': 120, 'notice_radius': 400},
	'spirit': {'health': 100,'exp':110,'damage':8,'attack_type': 'thunder', 'attack_sound':'../audio/attack/fireball.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 60, 'notice_radius': 350},
	'bamboo': {'health': 70,'exp':120,'damage':6,'attack_type': 'leaf_attack', 'attack_sound':'../audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 50, 'notice_radius': 300}}