from objects.players import Player, EnemyAI
from objects.gameinfo import GameInfo
from objects.gameobject import Planet
from settings import SCREEN_HEIGHT, SCREEN_WIDTH

from utility.debug import debug

import pygame as pg
import math
from icecream import ic
import random
import settings


class Level:
    def __init__(self) -> None:
        self.number: int
        self.state = "run"  # alternatives "win" and "loss"
        self.enemyAI_difficulty = 0.5  # float between 0 and 1

        self.projectiles_live = 0
        self.explosion = False  # nothing starts out exploding
        self.big_boom_size = 1  # start at 1 to avoid divide by zero
        self.start_fadeout = False
        self.teleport_triggered = False  # used to track GLSL effects for teleports
        self.teleport_coords: tuple

        self.zoom = 3  # zoom, 1 is closest, 3 furthest out
        self.framecounter = 0  # keeps track of iterations to reduce operations each frame

        self.h_scroll = 0  # tracks camera position, which is added to all objects in the game
        self.v_scroll = 0  # updates when the center of the midpoint touches edges of square in the center of the screen

    def _get_distance(self) -> int:
        return int(math.sqrt((self.player.rect.centerx - self.enemy.rect.centerx)**2 + (self.player.rect.centery - self.enemy.rect.centery)**2))  # type: ignore

    # Set up players and all sprite groups
    def startup(self, number) -> None:
        self.game_info = GameInfo()

        self.player = Player(
            x_pos=random.randint(100, SCREEN_WIDTH - 100),
            y_pos=random.randint(100, SCREEN_HEIGHT - 100),
            heading=random.random() * 359,
            ship_type="martian",
        )

        self.enemy = EnemyAI(
            x_pos=random.randint(100, SCREEN_WIDTH - 100),
            y_pos=random.randint(100, SCREEN_HEIGHT - 100),
            heading=random.random() * 359,
            ship_type="plutonian",
            skill=self.enemyAI_difficulty,
        )


        ic("Instancing new level", number)
        self.number = number

        # Player sprite group
        self.player_sprites = pg.sprite.GroupSingle()
        self.player_sprites.add(self.player)

        # EnemyAI sprite group
        self.enemy_ai_sprites = pg.sprite.GroupSingle()
        self.enemy_ai_sprites.add(self.enemy)

        # Planets and start and black holes etc.
        self.celestial_sprites = pg.sprite.Group()

        # Randomizing locations and objects:
        self.celestials = []
        for celest in range(0, random.randint(1, 3)):
            planet = Planet(celest, random.randint(int(settings.SCREEN_WIDTH * 0.1), int(settings.SCREEN_WIDTH * 0.9)),
                            random.randint(int(settings.SCREEN_HEIGHT * 0.1), int(settings.SCREEN_HEIGHT * 0.9)))
            self.celestials.append(planet)
            self.celestial_sprites.add(planet)

        # Win and loss sounds
        self.sound_win = pg.mixer.Sound("assets/sounds/win_1.wav")
        self.sound_loss = pg.mixer.Sound("assets/sounds/lose_1.wav")

        self.sound_win.set_volume(0.5)
        self.sound_win.set_volume(0.5)

    def get_event(self, event) -> str | None:
        self.player.get_event(event)
        if self.state != "run":
            return self.state

    # Update all objects
    def update(self) -> None:
       
        #ic(self.zoom)
       
        # Setting the camera position to be directly between the players
        #(self.h_scroll, self.v_scroll) = self._get_midpoint()

        self.h_scroll, self.v_scroll = self.player.update(self.zoom, self.h_scroll, self.v_scroll)

        # Updates the players's projectile sprites
        self.player.projectiles.update(self.zoom, self.h_scroll, self.v_scroll)
        self.player.engine_trails.update(self.zoom, self.h_scroll, self.v_scroll)

        # Update enemies and their projectiles
        self.enemy.update(self.zoom, self.h_scroll, self.v_scroll)

        self.enemy.projectiles.update(self.zoom, self.h_scroll, self.v_scroll)
        self.enemy.engine_trails.update(self.zoom, self.h_scroll, self.v_scroll)

        self.enemy.ai.update(self.player, self.zoom, self.h_scroll, self.v_scroll)

        # Update effect of celestial objects
        for celestial in self.celestials:  # for each planet
            for ship in [self.player, self.enemy]:  # for each shpt
                # Check if we're in range
                if math.sqrt((ship.rect.centerx - celestial.rect.centerx)**2 + (ship.rect.centery - celestial.rect.centery)**2) < celestial.influence_radius:
                    # Distance between ship and celestial:        
                    dx = ship.rect.centerx - celestial.rect.centerx
                    dy = ship.rect.centery - celestial.rect.centery
                    ship.vel_x -= int(dx * celestial.gravity)
                    ship.vel_y -= int(dy * celestial.gravity)
     


        # Check collisions
        if self.state == 'run':
            enemy_hit = False
            player_hit = False

            # Celestial collision - we use masks for precision
            for celestial in self.celestials:
                pg.sprite.spritecollide(celestial, self.player.projectiles, True, pg.sprite.collide_mask)  # type: ignore
                pg.sprite.spritecollide(celestial, self.enemy.projectiles, True, pg.sprite.collide_mask)  # type: ignore
                if pg.sprite.spritecollide(celestial, self.enemy_ai_sprites, False, pg.sprite.collide_mask):  # type: ignore
                    enemy_hit = True
                if pg.sprite.spritecollide(celestial, self.player_sprites, False, pg.sprite.collide_mask):  # type: ignore
                    player_hit = True

            # Ship and projectile collisions
            if pg.sprite.spritecollide(self.enemy, self.player.projectiles, False, pg.sprite.collide_mask):  # type: ignore
                enemy_hit = True
            if pg.sprite.spritecollide(self.player, self.enemy.projectiles, False, pg.sprite.collide_mask):  # type: ignore
                player_hit = True    

            # Enemy collision
            if enemy_hit:
                self.enemy.dead = True

                self.state = "win"
                pg.mixer.stop()

                self.explosion = True
                self.exploder = self.enemy
                self.start_time = pg.time.get_ticks()

                self.explosion_x = self.enemy.x_pos
                self.explosion_y = self.enemy.y_pos
                self.sound_win.play()

            # Player collision
            if player_hit:
                self.player.dead = True

                self.state = "loss"
                pg.mixer.stop()

                self.explosion = True
                self.exploder = self.player
                self.start_time = pg.time.get_ticks()
                self.explosion_x = self.player.x_pos
                self.explosion_y = self.player.y_pos
                self.sound_loss.play()

        if self.player.teleporting or self.enemy.teleporting:
            self.teleport_triggered = True
            if self.player.teleporting:
                self.teleport_coords = self.player.teleport_coords
            else: 
                self.teleport_coords = self.enemy.teleport_coords
            self.player.teleporting = self.enemy.teleporting = False

    # Draw all sprite groups + background
    def draw(self, surface) -> None:
        # DEBUG SECTION
        message = ic(self.player.vel_x, self.player.vel_y, self.player.accelleration)
        debug(message, x=20, y=20, surface=surface, color="#ffff00")


        '''
        Draw player information
        '''
        self.game_info.draw(
            surface,
            "Player 1",
            self.player.health,
            self.player.energy,
            "Enemy AI",
            self.enemy.health,
            self.enemy.energy,
        )

        '''
        Draw celestial objects
        '''
        self.celestial_sprites.draw(surface)

        '''
        Draw all player-related sprites
        '''
        self.player_sprites.draw(surface)
        self.player.projectiles.draw(surface)
        self.player.engine_trails.draw(surface)

        '''
        Draw all enemy-related sprites
        '''
        self.enemy_ai_sprites.draw(surface)
        self.enemy.projectiles.draw(surface)
        self.enemy.engine_trails.draw(surface)

        '''
        Draw explosion
        '''
        if self.explosion:
            x = self.explosion_x + random.randint(-30, 30) + self.h_scroll
            y = self.explosion_y + random.randint(-30, 30) + self.v_scroll
            radius = random.randint(5, 25)
            red_green = random.randint(128, 255)
            color = pg.Color(red_green, 255 - red_green, 0, random.randint(0, 255))

            # Draw small explosions
            if pg.time.get_ticks() - self.start_time < 1000:
                pg.draw.circle(surface, color, (x, y), radius=radius, width=radius)

            # Draw large expanding explosion
            if pg.time.get_ticks() - self.start_time > 500:
                self.exploder.kill()
                if self.big_boom_size < 255:
                    
                    # 6 expanding circles of difference colors - red edges and orange in the middle
                    for n in range(6):
                        radius = self.big_boom_size
                        
                        match n:
                            case 0 | 5:
                                color = pg.Color(128, 0, 0)
                            case 1 | 4:
                                color = pg.Color(255, 128, 0)
                            case 3:
                                color = pg.Color(255, 255, 0)

                        pg.draw.circle(surface, color, (self.explosion_x + self.h_scroll, self.explosion_y + self.v_scroll), radius=radius + n * 2, width=3)

                    self.big_boom_size += 5
                else:
                    self.explosion = False
            
            if pg.time.get_ticks() > 1000:  # we start fading at the end
                self.start_fadeout = True

        self.framecounter += 1  # this is the last thing to happen in this module for each new frame
        if self.framecounter == settings.FPS:
            self.framecounter = 0
                     

