from .gameobject import Projectile
from .ship import Ship

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
        self.skill = skill

    def think(self, player, player_projectiles) -> None:
        # Basic enemy AI, simulating inputs

        # Turn AI towards player
        # Assuming you have two sprite objects with their positions

        # Calculate the vector to Player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        # Calculate the angle in radians
        angle = math.atan2(-dx, -dy)
        angle %= 2 * math.pi
        angle = math.degrees(angle)

        # Perfect following: self.state.heading = angle
        angle_delta = angle - self.state.heading
        if angle_delta < 0:
            angle_delta += 360

        self.turning = 0

        if angle_delta > self.turn_speed:
            if angle_delta >= 180:
                self.turning = -1
            elif angle_delta > 0:
                self.turning = 1

        else:
            self.fire(firing=True, primary=True)


class Player(Ship):
    def __init__(self, x_pos, y_pos, heading, ship_type) -> None:
        velocity = 0
        direction = 0
        super().__init__(x_pos, y_pos, direction, velocity, heading, ship_type)
        self.projectiles = pg.sprite.Group()

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
                case pg.K_SPACE:
                    self.fire(firing=True, primary=True)
                case pg.K_SPACE:
                    self.fire(firing=True, primary=False)
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
