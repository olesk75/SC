from .gameobject import GameObject, Projectile, EngineTrail
from settings import SCREEN_HEIGHT, SCREEN_WIDTH

import pygame as pg
import time
from icecream import ic
import math
import random
import settings
from collections import namedtuple


# Create a namedtuple type, Point
Velocity = namedtuple("Velocity", "x_vel y_vel heading")

class Ship(GameObject):
    """The Ship class inherits from GameObject, and based on ship type, provides custom
    attributes for each type of ship

    """

    def __init__(self, x_pos, y_pos, direction, velocity, heading, ship_type) -> None:
        # Placeholders overridden by child objects
        self.projectiles = pg.sprite.Group()
        self.engine_trails = pg.sprite.Group()

        self.ship_type = ship_type
        self.max_velocity = 10  # TODO: read from ship config
        self.min_velocity = -5  # TODO: read from ship config

        self.firing = False
        self.last_fire = 0
        self.last_energy_tick = 0
        self.last_engine_trail = 0

        self.accelleration = 0
        self.velociyy = Velocity(x_vel = 0, y_vel = 0, heading = heading)
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
                self.max_energy = 1000
                self.turn_speed = 5
                self.image_zoom1 = pg.image.load("assets/ships/martian_1.png").convert_alpha()
                self.image_zoom1_engines = pg.image.load("assets/ships/martian_1-engines.png").convert_alpha()
                self.image_zoom2 = pg.image.load("assets/ships/martian_2.png").convert_alpha()
                self.image_zoom2_engines = pg.image.load("assets/ships/martian_2-engines.png").convert_alpha()
                self.image_zoom3 = pg.image.load("assets/ships/martian_3.png").convert_alpha()
                self.image_zoom3_engines = pg.image.load("assets/ships/martian_3-engines.png").convert_alpha()
                self.special = "teleport"
                self.fire_sound = pg.mixer.Sound("assets/sounds/shot_5.wav")
                self.fire_sound.set_volume(0.9)
                self.special_sound = pg.mixer.Sound("assets/sounds/change_1.wav")
                self.special_sound.set_volume(0.4)
            case "plutonian":
                self.health = 2000
                self.shield = 500
                self.energy = 250
                self.recharge = 10
                self.fire_rate = 500
                self.max_velocity = 15
                self.max_energy = 1000
                self.turn_speed = 5
                self.image_zoom1 = pg.image.load("assets/ships/plutonian_1.png").convert_alpha()
                self.image_zoom1_engines = pg.image.load("assets/ships/plutonian_1-engines.png").convert_alpha()
                self.image_zoom2 = pg.image.load("assets/ships/plutonian_2.png").convert_alpha()
                self.image_zoom2_engines = pg.image.load("assets/ships/plutonian_2-engines.png").convert_alpha()
                self.image_zoom3 = pg.image.load("assets/ships/plutonian_3.png").convert_alpha()
                self.image_zoom3_engines = pg.image.load("assets/ships/plutonian_3-engines.png").convert_alpha()
                self.special = "shield"
                self.fire_sound = pg.mixer.Sound("assets/sounds/fire_2.wav")
                self.fire_sound.set_volume(0.9)
                self.special_sound = pg.mixer.Sound("assets/sounds/shot_5.wav")
                self.special_sound.set_volume(0.5)
            case _:
                raise ValueError(f"{ship_type} is not an allowed ship type")

        

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

        self.image = self.image_zoom1  # we start with lowest zoom level
        self.rect = self.image.get_rect()

        # We need these for roations etc.
        self.image_orig = self.image
        self.rect_orig = self.rect

    def fire(self) -> None:
        now = pg.time.get_ticks()
        if now - self.last_fire > self.fire_rate and self.energy > 10:  # hardcoded
            self.last_fire = now
            self.fire_sound.play()
            self.energy -= 10  # hardcoded
            # firing primary weapon
            # TODO: placeholder data
            self.firing = True
            p_velocity = 20
            p_direction = self.heading
            p_health = 1000
            p_time = 10
            p_shield = 1000
            p_energy = 0
            p_recharge = 0
            p_fire_rate = 0
            p_explode = False
            p = Projectile(
                self.x_pos,
                self.y_pos,
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

    # TODO: placeholder
    def trigger_shield(self) -> None:
        return super().trigger_shield()

    def fire_special(self) -> None:
        match self.ship_type:
            case "martian":
                self.x_pos = random.randint(100, SCREEN_WIDTH - 100)
                self.y_pos = random.randint(100, SCREEN_HEIGHT - 100)
                self.special_sound.play()

    def update(self, zoom, h_scroll, v_scroll) -> tuple:
        # From accelleration to speed to coordinates
        if (self.velocity < self.max_velocity and self.velocity > 0) or (
            self.velocity > self.min_velocity and self.velocity <= 0
        ):
            self.velocity += self.accelleration
            
        # Add engine trails if we're accellerating
        if self.accelleration > 0 and time.time() - self.last_engine_trail > 0.1:
            et = EngineTrail(self.x_pos + h_scroll, self.y_pos + v_scroll, "regular")
            self.engine_trails.add(et)
            self.last_engine_trail = time.time()
                   

        self.spin(self.turning, self.turn_speed)

        # Zoom level
        if zoom == 1: self.image_orig = self.image_zoom1
        if zoom == 2: self.image_orig = self.image_zoom2
        if zoom == 3: self.image_orig = self.image_zoom3
        self.rect_orig = self.image_orig.get_rect()  # TODO: every update????

        # Rotation
        self.image, self.rect = self._rotatesprite(self.image_orig, self.rect_orig, self.heading)

        # TODO: rework this to have momentum

        # Movement
        dx = -int(math.sin(math.radians(self.heading)) * self.velocity / zoom)
        dy = -int(math.cos(math.radians(self.heading)) * self.velocity / zoom)

        self.x_pos += dx
        self.y_pos += dy
        
        # We show up on the other side if we hit the edges
        if dx > 0 and self.x_pos >= settings.SCREEN_WIDTH: 
            self.x_pos -= settings.SCREEN_WIDTH
            
        if dx < 0 and self.x_pos <= 0: 
            self.x_pos += settings.SCREEN_WIDTH
       
        if dy > 0 and self.y_pos >= settings.SCREEN_HEIGHT: 
            self.y_pos -= settings.SCREEN_HEIGHT
            
        if dy < 0 and self.y_pos <= 0: 
            self.y_pos += settings.SCREEN_HEIGHT

        #ic(dx, self.x_pos, self.rect.centerx, h_scroll)
        

        # Position 
        self.rect.center = (self.x_pos + h_scroll, self.y_pos + v_scroll)

        # Energy recharge
        now = pg.time.get_ticks()
        if (
            now - self.last_energy_tick > 1000 and self.energy < self.max_energy
        ):  # hardcoded ignoring max values
            self.last_energy_tick = now
            self.energy += self.recharge
            if self.energy > self.max_energy:
                self.energy = self.max_energy

        # Self firing
        if self.firing:
            self.fire()


        return h_scroll, v_scroll
