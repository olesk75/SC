from .gameobject import GameObject, Projectile

import pygame as pg
from icecream import ic
import math


class Ship(GameObject):
    """The Ship class inherits from GameObject, and based on ship type, provides custom
    attributes for each type of ship

    """

    def __init__(self, x_pos, y_pos, direction, velocity, heading, ship_type) -> None:
        self.ship_type = ship_type
        self.max_velocity = 10  # TODO: read from ship config
        self.min_velocity = -5  # TODO: read from ship config

        self.accelleration = 0
        self.slowing = 10

        self.turning = 0

        self.width = 80  # TODO: into game object
        self.height = 80

        match self.ship_type:
            case "martian":
                ic(self.ship_type)
                self.health = 1000
                self.shield = 1000
                self.energy = 1000
                self.recharge = 10
                self.max_velocity = 10
                self.turn_speed = 5
                self.image = pg.image.load("assets/ships/martian.png").convert_alpha()
                self.image_engines = pg.image.load(
                    "assets/ships/martian-engines-full.png"
                ).convert_alpha()
            case "plutonian":
                ic(self.ship_type)
                self.health = 2000
                self.shield = 500
                self.energy = 250
                self.recharge = 50
                self.max_velocity = 18
                self.turn_speed = 5
                self.image = pg.image.load("assets/ships/plutonian.png").convert_alpha()
                self.image_engines = pg.image.load(
                    "assets/ships/plutonian-engines-full.png"
                ).convert_alpha()
            case _:
                raise ValueError(f"{ship_type} is not an allowed ship type")

        self.rect = self.image.get_rect()

        # We need these for roations etc.
        self.image_orig = self.image
        self.rect_orig = self.rect

        super().__init__(
            x_pos,
            y_pos,
            self.health,
            self.shield,
            self.energy,
            self.recharge,
            direction,
            velocity,
            heading,
            self.max_velocity,
        )

    def fire(self, firing: bool, primary: bool) -> None:
        if primary:
            # firing primary weapon
            # TODO: placeholder data
            self.firing = firing
            p_velocity = 20
            p_direction = self.state.heading
            p_health = 1000
            p_time = 10
            p_shield = 1000
            p_energy = 0
            p_recharge = 0
            p_explode = False
            p = Projectile(
                self.state.x_pos,
                self.state.y_pos,
                p_health,
                p_shield,
                p_energy,
                p_recharge,
                p_direction,
                p_velocity,
                p_direction,
                max_velocity=1000,
                expiry_time=p_time,
            )
            self.projectiles.add(p)

        else:
            # firing secondary weapon
            pass

    def update(self) -> None:
        # From accelleration to speed to coordinates
        if (self.state.velocity < self.max_velocity and self.state.velocity > 0) or (
            self.state.velocity > self.min_velocity and self.state.velocity <= 0
        ):
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

        self.spin(self.turning, self.turn_speed)

        # Rotation
        self.image, self.rect = self._rotatesprite(
            self.image_orig, self.rect_orig, self.state.heading
        )

        # Movement
        self.state.x_pos -= int(math.sin(math.radians(self.state.heading)) * self.state.velocity)
        self.state.y_pos -= int(math.cos(math.radians(self.state.heading)) * self.state.velocity)

        # Position
        self.rect.center = (self.state.x_pos, self.state.y_pos)
