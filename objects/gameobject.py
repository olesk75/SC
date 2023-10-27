from dataclasses import dataclass
from icecream import ic
import pygame as pg
import math


@dataclass(kw_only=True)
class GameObjectState:
    """Metaclass for all game objects, like enemies, player, bullets, powerups etc.

    Attributes:
        x_pos   : global x position
        y_pos   : global y position
        health  : remaining health
        shield  : remaining shield
        alive   : dead or alive?
    """

    x_pos: int
    y_pos: int
    health: int
    shield: int
    direction: int
    velocity: int
    heading: int
    max_velocity: int

    # Field witrh default values
    alive: bool = True  # always initialized alive
    firing: bool = False  # is the game object currently firing a projectile
    shielded: bool = False  # shield active on object
    exploding: bool = False  # if object is currently exploding


class GameObject(pg.sprite.Sprite):
    """Metaclass for all game objects, like enemies, player, bullets, powerups etc.

    The class inherits from the Sprite class. Object is added to a sprite group, which then is used for calling the draw(method)
    """

    def __init__(
        self, x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity
    ) -> None:
        self.state = GameObjectState(
            x_pos=x_pos,
            y_pos=y_pos,
            health=health,
            shield=shield,
            direction=direction,
            velocity=velocity,
            heading=heading,
            max_velocity=max_velocity,
        )
        super().__init__()

        self.rect = pg.Rect
        self.image = pg.Surface

    def accelerate(self, direction) -> None:
        # TODO: add acceleration factor depending on ship type
        ship_accelleration = 1
        ship_max_speed = 100
        ship_min_speed = -10
        self.speed += ship_accelleration * direction
        if self.speed > ship_max_speed:
            self.speed = ship_max_speed
        if self.speed < ship_min_speed:
            self.speed = ship_min_speed

    def spin(self, direction) -> None:
        ship_rotate_speed = 1
        self.state.heading += ship_rotate_speed * direction
        if self.state.heading >= 360:
            self.state.heading -= 360
        if self.state.heading < 0:
            self.state.heading += 360

    def fire(self, primary: bool) -> None:
        if primary:
            # firing primary weapon
            pass
        else:
            # firing secondary weapon
            pass

    def trigger_shield(self) -> None:
        pass

    def _rotate(self, image, rect, angle):
        """rotate an image while keeping its center"""
        rot_image = pg.transform.rotate(image, angle)
        rot_rect = rot_image.get_rect(center=rect.center)
        return rot_image, rot_rect

    def update(self) -> None:
        print(f"Speed: {self.speed}, rotation: {self.state.heading}")

    def draw(self) -> None:
        pass


class Ship(GameObject):
    def __init__(
        self,
        x_pos: int,
        y_pos: int,
        health: int,
        shield: int,
        direction: int,
        velocity: int,
        heading: int,
        max_velocity: int,
    ) -> None:
        super().__init__(x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity)


class Obstacle(GameObject):
    def __init__(self, x_pos: int, y_pos: int, health: int, shield, destructible: bool) -> None:
        super().__init__(
            x_pos, y_pos, health, shield, 0, 0, 0, 0
        )  # obstacles have no direction, velocity nor heading
        self.destructible = destructible


class Projectile(GameObject):
    def __init__(
        self,
        x_pos: int,
        y_pos: int,
        health: int,
        shield: int,
        direction: int,
        velocity: int,
        heading: int,
        max_velocity: int,
        expiry_time: int,
    ) -> None:
        super().__init__(x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity)
        self.expiry_time: int
        self.explode: bool
        self.explosion_size: int

        self.ticks = 0

        self.type = "placeholder"
        self.image = pg.image.load("assets/projectiles/green_shot.png").convert_alpha()
        self.rect = self.image.get_rect()

        # We set rotation
        self.image, self.rect = self._rotate(self.image, self.rect, heading)

        # Every projectile is different
        if self.type == "placeholder":
            self.expiry_time = 60  # 60 tics * 3 = 3 seconds
            self.explode = True
            self.explosion_size = 50

    def update(self):
        self.ticks += 1

        # If we're too old we die or explode
        if self.ticks >= self.expiry_time:
            if not self.explode:
                self.kill()
            else:
                # explode!
                pass
                self.kill()

        # Movement
        self.state.x_pos -= math.sin(math.radians(self.state.heading)) * self.state.velocity
        self.state.y_pos -= math.cos(math.radians(self.state.heading)) * self.state.velocity

        # Position
        self.rect.center = (self.state.x_pos, self.state.y_pos)
