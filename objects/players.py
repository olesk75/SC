from .ship import Ship
from .ai import AI

import pygame as pg
from icecream import ic
import math


class EnemyPlayer(Ship):
    def __init__(self, x_pos, y_pos, direction, velocity, heading, ship_type) -> None:
        super().__init__(x_pos, y_pos, direction, velocity, heading, ship_type)
        pass


class EnemyAI(Ship):
    """
    Similar to Player() class, but with additional skill
    """

    def __init__(self, x_pos, y_pos, heading, ship_type, skill) -> None:
        velocity = 0
        direction = 0
        super().__init__(x_pos, y_pos, direction, velocity, heading, ship_type)
        self.projectiles = pg.sprite.Group()
        self.engine_trails = pg.sprite.Group()

        self.ai = AI(self, skill=skill, ship_type=ship_type)


class Player(Ship):
    def __init__(self, x_pos, y_pos, heading, ship_type) -> None:
        velocity = 0
        direction = 0
        super().__init__(x_pos, y_pos, direction, velocity, heading, ship_type)
        self.projectiles = pg.sprite.Group()
        self.engine_trails = pg.sprite.Group()

    def get_event(self, event) -> None:
        # Checking if a new key is pressed down
        if event.type == pg.KEYDOWN:
            match event.key:
                # Accelleration and decelleration
                case pg.K_UP:
                    self.accelleration += 1
                case pg.K_DOWN:
                    self.accelleration -= 1
                # Turning
                case pg.K_LEFT:
                    self.turning = 1
                case pg.K_RIGHT:
                    self.turning = -1
                # Firing
                case pg.K_LCTRL:
                    self.firing = True
                case pg.K_LSHIFT:
                    self.fire_special()
                # Quitting
                case pg.K_ESCAPE:
                    pg.event.post(pg.event.Event(pg.QUIT))

        # Checking if a previously pressed key is being released
        if event.type == pg.KEYUP:
            match event.key:
                # We have stopped accellerating or decellerating
                case pg.K_UP:
                    self.accelleration = 0
                case pg.K_DOWN:
                    self.accelleration = 0
                case pg.K_LEFT:
                    self.turning = 0
                case pg.K_RIGHT:
                    self.turning = 0
                case pg.K_LCTRL:
                    self.firing = False
