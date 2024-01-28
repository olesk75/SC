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
        self.arriving = True  # ships are arriving when we start a new lvl
        self.big_boom_size = 1  # start at 1 to avoid divide by zero
        self.start_fadeout = False
        self.teleport_triggered = False  # used to track GLSL effects for teleports
        self.teleport_coords: tuple

        self.zoom = 0  # zoom, 1 is closest, 3 furthest out
        self.zoom_x = 0  # zoom coordinates
        self.zoom_y = 0

        self.framecounter = 0  # keeps track of iterations to reduce operations each frame

    def _get_distance(self) -> int:
        '''
        Return distance between players
        '''
        return int(math.sqrt((self.player.rect.centerx - self.enemy.rect.centerx)**2 + (self.player.rect.centery - self.enemy.rect.centery)**2))  # type: ignore
    
    def _random_location(self, number) -> list[tuple]:
        '''
        Return  random locations in a list of locations with a minumum separation 
        '''
        locations = []
        
        min_distance = 150  # pixels minumum separation
        while len(locations) < number:
            x = random.randint(int(SCREEN_WIDTH * 0.1), int(SCREEN_WIDTH * 0.9))  # avoiding the edges
            y = random.randint(int(SCREEN_HEIGHT * 0.1), int(SCREEN_HEIGHT * 0.9))

            distance = lambda x1, y1, x2, y2: ((x1 - x2)**2 + (y1 - y2)**2)**0.5
        
            # Check if the new point is at least min_distance away from existing points
            if all(distance(x, y, cx, cy) >= min_distance for cx, cy in locations):
                locations.append((x, y))
        return locations
    
    def _set_zoom(self, zoom) -> tuple[int, int, int]:
        distance = math.sqrt((self.player.rect.centerx - self.enemy.rect.centerx)**2 + (self.player.rect.centery - self.enemy.rect.centery)**2) # type: ignore
        if distance > SCREEN_WIDTH/3:
            if zoom != 3:
                zoom = 3
        elif distance > SCREEN_WIDTH/5.8:
            if zoom != 2:
                zoom = 2
        else:
            if zoom != 1:
                zoom = 1

        zoom_x = int((self.player.rect.centerx + self.enemy.rect.centerx) / 2)  # type: ignore
        zoom_y = int((self.player.rect.centery + self.enemy.rect.centery) / 2)  # type: ignore

        return (zoom, zoom_x, zoom_y)

     
    def startup(self, number) -> None:
        '''
        Set up players and all sprite groups
        '''
        self.game_info = GameInfo()

        random_locations = self._random_location(10)  # generate 10 random locations, more than 100 pixels apart

        self.player = Player(
            random_locations.pop(),
            heading=random.random() * 359,
            ship_type="martian",
        )

        self.enemy = EnemyAI(
            random_locations.pop(),
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
            planet = Planet(celest, random_locations.pop(),)
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
        self.player.update()
        (self.zoom, self.zoom_x, self.zoom_y) = self._set_zoom(self.zoom)

        # Updates the players's projectile sprites
        self.player.projectiles.update()
        self.player.engine_trails.update()

        # Update enemies and their projectiles
        self.enemy.update()

        self.enemy.projectiles.update()
        self.enemy.engine_trails.update()

        self.enemy.ai.update(self.player, self.celestials)

        # Update effect of celestial objects
        for celestial in self.celestials:  # for each planet
            for ship in [self.player, self.enemy]:  # for each ship
                if not ship.dead:
                    # Check if we're in range
                    distance = math.sqrt((ship.rect.centerx - celestial.rect.centerx)**2 + (ship.rect.centery - celestial.rect.centery)**2)
                    if  distance < celestial.influence_radius:
                        # Distance between ship and celestial:
                        acceleration = celestial.gravity / (distance ** 2)

                        angle_radians = math.atan2(ship.rect.centery - celestial.rect.centery, ship.rect.centerx - celestial.rect.centerx)

                        dx = math.cos(angle_radians) * acceleration
                        dy = math.sin(angle_radians) * acceleration

                        # print(f'accel: {acceleration:.2f}, dx: {dx:.2f}, dy: {dy:.2f}')  # for debugging

                        # Impact of gravity is the gravitationaly force divided by the square of the distance
                        ship.vel_x -= dx
                        ship.vel_y -= dy
  

        # Check collisions
        if self.state == 'run':

            # Celestial collision - we use masks for precision, they are fatal
            for celestial in self.celestials:
                pg.sprite.spritecollide(celestial, self.player.projectiles, True, pg.sprite.collide_mask)  # type: ignore
                pg.sprite.spritecollide(celestial, self.enemy.projectiles, True, pg.sprite.collide_mask)  # type: ignore
                if pg.sprite.spritecollide(celestial, self.enemy_ai_sprites, False, pg.sprite.collide_mask):  # type: ignore
                    self.enemy.health = 0
                    self.enemy.vel_x = self.enemy.vel_y = 0  # if we hit a planet, we stop
                if pg.sprite.spritecollide(celestial, self.player_sprites, False, pg.sprite.collide_mask):  # type: ignore
                    self.player.health = 0
                    self.player.vel_x = self.player.vel_y = 0  # if we hit a planet, we stop

            # Ship + projectile collisions - damage depends on projectile
            projectile_hit = pg.sprite.spritecollide(self.enemy, self.player.projectiles, False, pg.sprite.collide_mask)  # type: ignore
            if projectile_hit:
                projectile = projectile_hit.pop()
                self.enemy.hit_pos = projectile.rect.center
                self.enemy.hit = True
                projectile.kill()  # we remove the projectile
                self.enemy.health -= self.player.p.damage 
                self.player.hit_other_sound.play()

            # Player                
            projectile_hit = pg.sprite.spritecollide(self.player, self.enemy.projectiles, False, pg.sprite.collide_mask)  # type: ignore
            if projectile_hit:
                projectile = projectile_hit.pop()
                self.player.hit_pos = projectile.rect.center
                self.player.hit = True
            
                projectile.kill()  # we remove the projectile
                self.player.health -= self.enemy.p.damage 
                self.enemy.hit_other_sound.play()
                
            

            # Ship + ship collisions: bounce-back (with small damage?)
            if pg.sprite.spritecollide(self.enemy, self.player_sprites, False, pg.sprite.collide_mask):  # type: ignore    
                (x, y) = self.player.vel_x, self.player.vel_y
                (self.player.vel_x, self.player.vel_y) = (self.enemy.vel_x, self.enemy.vel_y)  # we swap velocities 
                (self.enemy.vel_x, self.enemy.vel_y) = (x, y)
                self.enemy.health -= 100
                self.player.health -= 100


            # Enemy dead (health zub zero)
            if self.enemy.health <= 0:
                self.enemy.dead = True

                self.state = "win"
                pg.mixer.stop()

                self.explosion = True
                self.exploder = self.enemy
                self.start_time = pg.time.get_ticks()

                self.explosion_x = self.enemy.x_pos
                self.explosion_y = self.enemy.y_pos
                self.enemy.explosion_sound.play()
                self.sound_win.play()

            # Player dead (health zub zero)
            if self.player.health <= 0:
                self.player.dead = True

                self.state = "loss"
                pg.mixer.stop()

                self.explosion = True
                self.exploder = self.player
                self.start_time = pg.time.get_ticks()
                self.explosion_x = self.player.x_pos
                self.explosion_y = self.player.y_pos
                self.player.explosion_sound.play()
                self.sound_loss.play()

        if self.player.teleporting or self.enemy.teleporting:
            self.teleport_triggered = True
            if self.player.teleporting:
                self.teleport_coords = self.player.teleport_coords
            else: 
                self.teleport_coords = self.enemy.teleport_coords
            self.player.teleporting = self.enemy.teleporting = False

    # Draw all sprite groups + background
    def draw(self, surface, overlay) -> None:
        # DEBUG SECTION
        #message = f'vel_x: {self.player.vel_x:.2f}, vel_y: {self.player.vel_y:.2f}, accel: {self.player.accelleration:.2f}'
        message = f'AI attitude: {self.enemy.ai.attitude}'
        debug(message, x=20, y=20, surface=overlay, color="#ffff00")

        '''
        Draw player information
        '''
        self.game_info.draw(overlay,
            "Player 1", self.player.health, self.player.energy,
            "Enemy AI", self.enemy.health, self.enemy.energy,
        )

        '''
        Draw celestial objects
        '''
        self.celestial_sprites.draw(surface)

        '''
        Draw all player-related sprites (mind the order!)
        '''
        self.player.engine_trails.draw(surface)
        self.player_sprites.draw(surface)
        self.player.projectiles.draw(surface)

        # Hit indicators
        for ship in [self.player, self.enemy]:
            if ship.hit:
                pg.draw.circle(surface, '#ffff00', ship.hit_pos, radius=15, width=15)
                ship.hit = False

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
            x = self.explosion_x + random.randint(-30, 30)
            y = self.explosion_y + random.randint(-30, 30)
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

                        pg.draw.circle(surface, color, (self.explosion_x, self.explosion_y), radius=radius + n * 2, width=3)
                    self.big_boom_size += 5
                else:
                    self.explosion = False
            
            if pg.time.get_ticks() > 1000:  # we start fading at the end
                self.start_fadeout = True

        self.framecounter += 1  # this is the last thing to happen in this module for each new frame
        if self.framecounter == settings.FPS:
            self.framecounter = 0
                     

