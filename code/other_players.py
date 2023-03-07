from support import *
class Players:
    def __init__(self, image, id, pos,groups): # add hiting
        # general setup
        super().__init__(groups)
        self.sprite_type = 'enemy'
        self.id = id
        # graphics setup
        self.import_graphics(image)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]


        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)

        # stats
        self.image = image
        player_info = image[self.image]  # the list that will give us the following information
        self.health = player_info['health']
        self.exp = player_info['exp']  # how much exp we will get from killing the monster
        self.speed = player_info['speed']
        self.attack_damage = player_info['damage']
        self.resistance = player_info['resistance']  # how does the monster takes a hit
        self.attack_radius = player_info['attack_radius']  # the radius that the monster will attack us
        self.notice_radius = player_info['notice_radius']  # the radius that the monster will aproach us
        self.attack_type = player_info['attack_type']  # the type of the monster's attack

        # player interaction
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400

        # invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': []}
        main_path = f'../graphics/ninjarobot/{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)  # gives me the correct monster image

    def get_damage(self, player, attack_type):
        """

        :param player: the player
        :param attack_type: if its close weapon attack or away wepon attack
        :return:nothing
        """
        if self.vulnerable:
            self.direction = self.get_player_distance_direction(player)[1]
            if attack_type == 'weapon':
                self.health -= player.get_full_weapon_damege()
            else:
                pass
                # away_damage
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def chack_death(self):
        """
        check if the enemy lost all of his health and kill him if so
        :return:
        """
        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(self.rect.center,self.monster_name)