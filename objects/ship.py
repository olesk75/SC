from .gameobject import GameObject, Projectile
from settings import SCREEN_HEIGHT, SCREEN_WIDTH

import pygame as pg
from icecream import ic
import math
import random


class Ship(GameObject):
    """The Ship class inherits from GameObject, and based on ship type, provides custom
    attributes for each type of ship

    """

    def __init__(self, x_pos, y_pos, direction, velocity, heading, ship_type) -> None:
        self.ship_type = ship_type
        self.max_velocity = 10  # TODO: read from ship config
        self.min_velocity = -5  # TODO: read from ship config

        self.last_fire = 0
        self.last_energy_tick = 0

        self.accelleration = 0
        self.slowing = 10

        self.turning = 0

        self.width = 80  # TODO: into game object
        self.height = 80
        self.ships = ["martian", "plutonian"]

        match self.ship_type:
            case "martian":
                self.health = 1000
                self.shield = 1000
                self.energy = 1000
                self.recharge = 5
                self.fire_rate = 100  # lower is faster
                self.max_velocity = 10
                self.turn_speed = 5
                self.image = pg.image.load("assets/ships/martian.png").convert_alpha()
                self.image_engines = pg.image.load(
                    "assets/ships/martian-engines-full.png"
                ).convert_alpha()
                self.special = "teleport"
                self.fire_sound = pg.mixer.Sound("assets/sounds/shot_5.wav")
                self.special_sound = pg.mixer.Sound("assets/sounds/change_1.wav")
            case "plutonian":
                self.health = 2000
                self.shield = 500
                self.energy = 250
                self.recharge = 10
                self.fire_rate = 500
                self.max_velocity = 15
                self.turn_speed = 5
                self.image = pg.image.load("assets/ships/plutonian.png").convert_alpha()
                self.image_engines = pg.image.load(
                    "assets/ships/plutonian-engines-full.png"
                ).convert_alpha()
                self.special = "shield"
                self.fire_sound = pg.mixer.Sound("assets/sounds/fire_2.wav")
                self.special_sound = pg.mixer.Sound("assets/sounds/shot_5.wav")
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
            self.fire_rate,
            direction,
            velocity,
            heading,
            self.max_velocity,
        )

    def fire(self) -> None:
        now = pg.time.get_ticks()
        if now - self.last_fire > self.state.fire_rate and self.state.energy > 10:  # hardcoded
            self.last_fire = now
            self.fire_sound.play()
            self.state.energy -= 10  # hardcoded
            # firing primary weapon
            # TODO: placeholder data
            self.firing = True
            p_velocity = 20
            p_direction = self.state.heading
            p_health = 1000
            p_time = 10
            p_shield = 1000
            p_energy = 0
            p_recharge = 0
            p_fire_rate = 0
            p_explode = False
            p = Projectile(
                self.state.x_pos,
                self.state.y_pos,
                p_health,
                p_shield,
                p_energy,
                p_recharge,
                p_fire_rate,
                p_direction,
                p_velocity,
                p_direction,
                max_velocity=1000,
                expiry_time=p_time,
            )
            self.projectiles.add(p)

    def fire_special(self) -> None:
        match self.ship_type:
            case "martian":
                self.state.x_pos = random.randint(100, SCREEN_WIDTH - 100)
                self.state.y_pos = random.randint(100, SCREEN_HEIGHT - 100)
                self.special_sound.play()

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

        # Energy recharge
        now = pg.time.get_ticks()
        if (
            now - self.last_energy_tick > 1000 and self.state.energy < self.state.max_energy
        ):  # hardcoded ignoring max values
            self.last_energy_tick = now
            self.state.energy += self.recharge
            if self.state.energy > self.state.max_energy:
                self.state.energy = self.state.max_energy
