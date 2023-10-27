from .gameobject import Ship

import pygame as pg
from icecream import ic

import math

class EnemyPlayer(Ship):
    def __init__(self, x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity) -> None:
        super().__init__(x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity)


class EnemyAI(Ship):
    def __init__(self, x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity,skill) -> None:
        super().__init__(x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity)
        self.skill = skill

    def update(self) -> None:
        pass

    def draw(self, surface) -> None:
        pass


class Player(Ship):
    def __init__(self, x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity) -> None:
        super().__init__(x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity)
        
        self.max_velocity = 10  # TODO: read from ship config 
        self.min_velocity = -5  # TODO: read from ship config 

        self.accelleration = 0
        self.slowing = 10

        self.turning = 0
        self.turn_speed = 4

        self.width = 80  # TODO: into game object
        self.height = 80

        self.image = pg.image.load('assets/ships/earthling.png').convert_alpha()
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        self.orig_rect = self.rect

    def get_event(self, event) -> None:
        # Checking if a new key is pressed down
        if event.type == pg.KEYDOWN:
            match event.key:
                # Accelleration and decelleration
                case pg.K_UP: self.accelleration += 1
                case pg.K_DOWN: self.accelleration -= 1
                # Turning
                case pg.K_LEFT: self.turning = 1
                case pg.K_RIGHT: self.turning = -1
                # Firing
                case pg.K_SPACE: self.firing(firing=True, main_gun=True)
                case pg.K_SPACE: self.firing(firing=True, main_gun=False)
                # Quitting
                case pg.K_ESCAPE: pg.event.post(pg.event.Event(pg.QUIT))

        # Checking if a previously pressed key is being released
        if event.type == pg.KEYUP:
            match event.key:
                # We have stopped accellerating or decellerating
                case pg.K_UP: self.accelleration = 0
                case pg.K_DOWN: self.accelleration = 0
                case pg.K_LEFT: self.turning = 0
                case pg.K_RIGHT: self.turning = 0

    

    def update(self) -> None:
        # From accelleration to speed to coordinates
        if (self.state.velocity < self.max_velocity and self.state.velocity > 0) or \
            (self.state.velocity > self.min_velocity and self.state.velocity <= 0):
            self.state.velocity += self.accelleration

        # We make the speed drop off slowly - we have 60 FPS, so this gets run 60
        self.slowing -= 1
        if self.slowing == 0:
            self.slowing = 10
            if self.state.velocity != 0:
                if self.state.velocity < 0:
                    self.state.velocity += 1
                else:
                    self.state.velocity -= 1
    
            
        # Determining the heading 
        self.state.heading += self.turning * self.turn_speed
        
        # Rotation
        self.image, self.rect = self._rotate(self.orig_image, self.orig_rect, self.state.heading)

        # Movement
        self.state.x_pos -= math.sin(math.radians(self.state.heading)) * self.state.velocity
        self.state.y_pos -= math.cos(math.radians(self.state.heading)) * self.state.velocity
        
        # Position
        self.rect.center = (self.state.x_pos, self.state.y_pos)


