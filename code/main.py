import pygame, sys
from settings import *
from level import Level
from  button import  Button
class Game:
	def __init__(self):
		  
		# general setup
		pygame.init()
		self.screen = pygame.display.set_mode((WIDTH,HEIGTH))
		pygame.display.set_caption('PUBG')
		self.clock = pygame.time.Clock()

		self.level = Level()
		self.font = pygame.font.Font(UI_FONT,18)  # our font
		self.display_surface = pygame.display.get_surface()
		self.user_text = ''
		self.passward = ''
		self.server_id = ''

	def main_menu(self):
		"""
		the main menu sceen creator
		:return:
		"""
		pygame.display.set_caption('menu')
		text_color =TEXT_COLOR
		ID_input_rect = pygame.Rect((550, 240), (160, 32))
		passward_input_rect = pygame.Rect((550, 290), (160, 32))
		server_input_rect = pygame.Rect((550, 340), (160, 32))
		active_ID = False
		active_pasward = False
		active_server = False
		while True:
			self.screen.fill('black')

			mouse_menu = pygame.mouse.get_pos()
			text_surf = pygame.font.Font(UI_FONT,150).render('PUBG', True, TEXT_COLOR)
			text_rect = text_surf.get_rect(center=(MIDDLE_SCREEN[0], MIDDLE_SCREEN[1] - 250))  # the bar
			self.display_surface.blit(text_surf, text_rect)


			play_button = Button(None, #create the play button
								 (640,450), "play",pygame.font.Font(UI_FONT,50), TEXT_COLOR, "yellow")


			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					if ID_input_rect.collidepoint(event.pos):
						active_ID = True
						active_pasward = False
						active_server = False
					if 	passward_input_rect.collidepoint(event.pos):
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
								self.user_text = self.user_text[:-1]
								text_color = TEXT_COLOR
							elif len(self.user_text) <= 8:
								self.user_text += event.unicode
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
								self.passward += event.unicode
								text_color = TEXT_COLOR
							else:
								text_color = 'red'
				if active_server:
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_SPACE:
							pass
						elif event.key == pygame.K_BACKSPACE:
							self.server_id = self.server_id[:-1]
							text_color = TEXT_COLOR
						elif len(self.server_id) <= 8:
							self.server_id += event.unicode
							text_color = TEXT_COLOR
						else:
							text_color = 'red'
				if event.type == pygame.MOUSEBUTTONDOWN:
					if play_button.checkForInput(event.pos):
						if len(self.user_text) > 0 and len(self.passward) > 0 and len(self.server_id) > 0:
							self.play()

			pygame.draw.rect(self.screen,'white',server_input_rect,2)
			pygame.draw.rect(self.screen,'white',passward_input_rect,2)
			pygame.draw.rect(self.screen,'white',ID_input_rect,2)
			ID_text_surface = self.font.render(self.user_text,True,text_color)#show text that the player write on the screen
			passward_text_surface = self.font.render(self.passward,True,text_color)
			server_text_surface = self.font.render(self.server_id,True,text_color)
			self.screen.blit(passward_text_surface,(555,295))
			self.screen.blit(ID_text_surface,(555,245))
			self.screen.blit(server_text_surface,(555,345))
			for button in [play_button]:
				button.changeColor(mouse_menu)
				button.update(self.screen)

			pygame.display.update()


	def play(self):
		pygame.display.set_caption('PUBG')
		self.screen.fill('black')
		while True:

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

			self.level.run(self.server_id,self.user_text,self.passward)
			pygame.display.update()
			self.clock.tick(FPS)
	def run(self):
		self.screen.fill('black')
		self.main_menu()

if __name__ == '__main__':
	game = Game()
	game.run()