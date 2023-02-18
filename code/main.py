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

	def main_menu(self):
		"""
		the main menu sceen creator
		:return:
		"""
		pygame.display.set_caption('menu')
		text_color =TEXT_COLOR
		input_rect = pygame.Rect(550, 240, 160, 32)

		while True:
			self.screen.fill('black')

			mouse_menu = pygame.mouse.get_pos()
			text_surf = pygame.font.Font(UI_FONT,150).render('PUBG', True, TEXT_COLOR)
			text_rect = text_surf.get_rect(center=(MIDDLE_SCREEN[0], MIDDLE_SCREEN[1] - 250))  # the bar
			self.display_surface.blit(text_surf, text_rect)

			play_button = Button(None, #create the play button
								 (640,350), "play",pygame.font.Font(UI_FONT,100), TEXT_COLOR, "yellow")

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_BACKSPACE:
							self.user_text = self.user_text[:-1]
							text_color = TEXT_COLOR
						elif len(self.user_text) < 8 :
							self.user_text += event.unicode
							text_color=TEXT_COLOR
						else:
							text_color = 'red'
				if event.type == pygame.MOUSEBUTTONDOWN:
					print("check")
					if play_button.checkForInput(mouse_menu):
						print("f")
						if len(self.user_text) > 0:
							print("play")
							self.play()



			pygame.draw.rect(self.screen,'white',input_rect,3)
			text_surface = self.font.render(self.user_text,True,text_color)#show text that the player write on the screen
			self.screen.blit(text_surface,(555,245))

			input_rect.w = max(100,text_surface.get_width()+10)

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

			self.level.run()
			pygame.display.update()
			self.clock.tick(FPS)
	def run(self):
		self.screen.fill('black')
		self.main_menu()

if __name__ == '__main__':
	game = Game()
	game.run()