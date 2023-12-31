from objects.players import Player, EnemyAI
from objects.background import Background
from settings import SCREEN_HEIGHT, SCREEN_WIDTH

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

        self.zoom = 3  # zoom, 1 is closest, 3 furthest out
        self.framecounter = 0  # keeps track of iterations to reduce operations each frame

        self.h_scroll = 0  # tracks camera position, which is added to all objects in the game
        self.v_scroll = 0  # updates when the center of the midpoint touches edges of square in the center of the screen


    def _get_distance(self) -> int:
        return int(math.sqrt((self.player.rect.centerx - self.enemy.rect.centerx)**2 + (self.player.rect.centery - self.enemy.rect.centery)**2))
        

    # Set up players and all sprite groups
    def startup(self, number) -> None:
        self.background = Background()

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
        if not self.explosion:
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
            # Update obstacles

            # Check collisions
            if self.state == 'run':
                # Enemy collision
                gets_hit = pg.sprite.spritecollide(self.enemy, self.player.projectiles, True)
                for projectile_hit in gets_hit:
                    projectile_hit.kill()

                    self.state = "win"
                    pg.mixer.stop()

                    self.explosion = True
                    self.exploder = self.enemy
                    self.start_time = pg.time.get_ticks()

                    self.explosion_x = self.enemy.state.x_pos
                    self.explosion_y = self.enemy.state.y_pos
                    self.sound_win.play()

                # Player collision
                gets_hit = pg.sprite.spritecollide(self.player, self.enemy.projectiles, True)
                for projectile_hit in gets_hit:
                    projectile_hit.kill()

                    self.state = "loss"
                    pg.mixer.stop()

                    self.explosion = True
                    self.exploder = self.player
                    self.start_time = pg.time.get_ticks()
                    self.explosion_x = self.player.state.x_pos
                    self.explosion_y = self.player.state.y_pos
                    self.sound_loss.play()

                
            if self.framecounter % 5 == 0:  # every 5th frame
                current_zoom = self.zoom
                
                # Camera is at the midpoint, so zoom if the distance starts becoming height or width of screen 
                if (self._get_distance() > settings.SCREEN_WIDTH * 0.9) or (self._get_distance() > settings.SCREEN_HEIGHT * 0.9):
                    if current_zoom < 3:  # if we can still zoom out...
                        self.zoom += 1

                # Ditto for getting too close to each other
                if (self._get_distance() < settings.SCREEN_WIDTH * 0.1) or (self._get_distance() < settings.SCREEN_HEIGHT * 0.1):
                    if current_zoom > 1:  # if we can still zoom in...
                        self.zoom += 1        


                # Check for a change in zoom levels
                if current_zoom != self.zoom:
                    ic(self.player.state.x_pos)
                    # Adjust positions based on zoom change
                    scale_factor = 0.5 if current_zoom < self.zoom else 2 
                    buffer = 256 if current_zoom < self.zoom else -256

                    self.player.state.x_pos = int(self.player.state.x_pos * scale_factor + buffer)
                    self.player.state.y_pos = int(self.player.state.y_pos * scale_factor + buffer)
                    self.enemy.state.x_pos = int(self.enemy.state.x_pos * scale_factor + buffer)
                    self.enemy.state.x_pos = int(self.enemy.state.x_pos * scale_factor + buffer)
                    
                    self.h_scroll = self.v_scroll = 0  # TODO: suspicious


    # Draw all sprite groups + background
    def draw(self, surface) -> None:
        self.background.draw(
            surface,
            "Player 1",
            self.player.state.health,
            self.player.state.energy,
            "Enemy AI",
            self.enemy.state.health,
            self.enemy.state.energy,
        )

        self.player_sprites.draw(surface)
        self.player.projectiles.draw(surface)
        self.player.engine_trails.draw(surface)

        self.enemy_ai_sprites.draw(surface)
        self.enemy.projectiles.draw(surface)
        self.enemy.engine_trails.draw(surface)

        if self.explosion:
            x = self.explosion_x + random.randint(-30, 30) + self.h_scroll
            y = self.explosion_y + random.randint(-30, 30) + self.v_scroll
            radius = random.randint(5, 25)
            red_green = random.randint(128, 255)
            color = pg.Color(red_green, 255 - red_green, 0, random.randint(0, 255))

            if pg.time.get_ticks() - self.start_time < 1000:
                pg.draw.circle(surface, color, (x, y), radius=radius, width=radius)

            if pg.time.get_ticks() - self.start_time > 500:
                self.exploder.kill()
                if self.big_boom_size < 255:
                    
                    # 10 expanding circles of difference colors - red edges and orange in the middle
                    for n in range(6):
                        radius = self.big_boom_size
                        
                        match n:
                            case 0 | 5:
                                color = pg.Color(128,0,0)
                            case 1 | 4:
                                color = pg.Color(255,128,0)
                            case 3:
                                color = pg.Color(255,255,0)

                        pg.draw.circle(surface, color, (self.explosion_x + self.h_scroll, self.explosion_y + self.v_scroll), radius=radius + n*2 , width=3)

                    self.big_boom_size += 5
                else:
                    self.explosion = False

        self.framecounter += 1  # this is the last thing to happen in this module for each new frame
        if self.framecounter == settings.FPS:
            self.framecounter = 0
                     

