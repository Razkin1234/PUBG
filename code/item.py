import pygame

class Item:
    def __init__(self):
        self.plus_health = self.plus_health
    def plus_health(self,heel,player):
        """
        gets how much to heel the player (player.health + heel) and the player
        heel the player.health by the heel parameter we got
        """
        if player.health+heel >= 100:
            player.health = 100
        else: player.health += heel