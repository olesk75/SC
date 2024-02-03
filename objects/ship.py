from .gameobject import GameObject, Projectile, EngineTrail
from utility.ship_configs import configs


import pygame as pg
import time
import math
import random

from icecream import ic


class Ship(GameObject):
    """The Ship class inherits from GameObject, and based on ship type, provides custom
    attributes for each type of ship

    """
    ships = ["martian", "plutonian", "zapper", "rocket", "miner", "behemoth"]

    def __init__(self, x_pos:int , y_pos:int , direction:int , velocity:int , heading:int , ship_type:str, config) -> None:
        # Placeholders overridden by child objects
        self.projectiles = pg.sprite.Group()
        self.engine_trails = pg.sprite.Group()

        self.ship_type = ship_type
        self.config = config
        self.max_velocity = 10  # TODO: read from ship config
        self.min_velocity = -5  # TODO: read from ship config

        self.vel_x = 0  # We start with zero volicty in either direction
        self.vel_y = 0

        self.firing = False
        self.dead = False
        self.hit = False  # we use this to check if we should draw a hit indicator on the ship
        self.hit_pos = (int, int)
        self.last_fire = 0
        self.last_energy_tick = 0
        self.last_engine_trail = 0
        self.controllable = True  # mostly used for arrival anomation
        self.visible = True  # mostly used for arrival anomation

        self.accelleration = 0
        self.turning = 0
        self.slow_turn = False  # used for the AI to do slower turns

        self.teleporting = False  # used only for shiw which can teleport
        self.teleport_coords = (False, False)

        self.width = 80  # TODO: into game object
        self.height = 80    

        if self.ship_type in self.ships:
            self.ship_config = configs[self.ship_type]
        else:
            ValueError(f"{ship_type} is not an allowed ship type")

        # Setting sounds and volumes
        self.fire_sound = pg.mixer.Sound(self.ship_config['fire_sound'])
        self.fire_sound.set_volume(self.ship_config['fire_sound_volume'])
        self.special_sound = pg.mixer.Sound(self.ship_config['special_sound'])
        self.special_sound.set_volume(self.ship_config['special_sound_volume'])
        self.hit_other_sound = pg.mixer.Sound(self.ship_config['hit_other_sound'])
        self.hit_other_sound.set_volume(self.ship_config['hit_other_sound_volume'])
        self.explosion_sound = pg.mixer.Sound(self.ship_config['explosion_sound'])
        self.explosion_sound.set_volume(self.ship_config['explosion_sound_volume'])

        super().__init__(
            x_pos,
            y_pos,
            self.ship_config['health'],
            self.ship_config['shield'],
            self.ship_config['energy'],
            self.ship_config['recharge'],
            self.ship_config['fire_rate'],
            direction,
            velocity,
            heading,
            self.ship_config['max_velocity'],
        )
        self.image = pg.image.load(self.ship_config['image_ship']).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (self.x_pos, self.y_pos)

        # We need these for roations etc.
        self.image_orig = self.image
        self.rect_orig = self.rect

        ic(self.energy)

    def fire(self) -> None:
        now = pg.time.get_ticks()
        if now - self.last_fire > self.ship_config['fire_rate'] and self.ship_config['energy'] >= self.ship_config['projectile']['recharge']: 
            self.last_fire = now
            self.fire_sound.play()
            self.energy -= self.ship_config['projectile']['recharge']
            # firing primary weapon
            # TODO: placeholder data
            self.firing = True
            p_direction = self.heading

            self.p = Projectile(
                self.ship_config['projectile']['type'],
                self.x_pos,
                self.y_pos,
                self.ship_config['projectile']['health'],
                self.ship_config['projectile']['shield'],
                self.ship_config['projectile']['energy'],
                self.ship_config['projectile']['recharge'],
                self.ship_config['projectile']['fire_rate'],
                self.ship_config['projectile']['explode'],
                self.ship_config['projectile']['damage'],
                p_direction,
                self.ship_config['projectile']['velocity'],
                p_direction,
                self.ship_config['projectile']['max_velocity'],
                self.ship_config['projectile']['expiry_time']
            )
            self.projectiles.add(self.p)

    # TODO: placeholder
    def trigger_shield(self) -> None:
        return super().trigger_shield()

    def fire_special(self) -> None:
        if not self.dead and self.controllable:
            match self.ship_type:
                case "martian":  # Teleport
                    if self.energy > self.ship_config['special_energy']:
                        self.x_pos = random.randint(100, self.config.window_size_xy - 100)
                        self.y_pos = random.randint(100, self.config.window_size_xy - 100)
                        self.teleporting = True
                        self.teleport_coords = (self.x_pos, self.y_pos)
                        self.special_sound.play()
                        self.energy -= self.ship_config['special_energy']




    def update(self) -> None:
        # Inertia and space friction(!)
        inertia = abs(self.vel_x) * 0.01  # 10% speed reduction per tick
        sign = (self.vel_x > 0) - (self.vel_x < 0)
        self.vel_x = sign * (abs(self.vel_x) - inertia)

        inertia = abs(self.vel_y) * 0.01  # 10% speed reduction per tick
        sign = (self.vel_y > 0) - (self.vel_y < 0)
        self.vel_y = sign * (abs(self.vel_y) - inertia)

        
        # Accellerating the ship
        if self.accelleration > 0 and not self.dead and self.controllable:  # the ship is accelerating in the direciton of its heading
            # The accelleration happens in the direction of the self.heading
            x_accel = y_accel = 0
            if self.vel_x < self.ship_config['max_velocity']:
                x_accel = -math.sin(math.radians(self.heading)) * self.accelleration
            if self.vel_y < self.max_velocity:
                y_accel = -math.cos(math.radians(self.heading)) * self.accelleration

            # We only allow accelleration which leads to a total speed of self.max_velocity or less,
            # or anmything that slows us down 

            vel_old = math.sqrt(self.vel_x**2 + self.vel_y**2)
            vel_new = math.sqrt((self.vel_x + x_accel)**2 + (self.vel_y + y_accel)**2)

            # We only allow accelleration if we're under under max speed or player wants to net slow down
            if vel_new <= self.max_velocity or vel_new < vel_old:
                self.vel_x += x_accel
                self.vel_y += y_accel


        # If we're accelerating...
        if self.accelleration > 0 and self.controllable: 
            # Add engine trails 
            if time.time() - self.last_engine_trail > 0.1:
                et = EngineTrail(self.x_pos, self.y_pos, "regular")
                self.engine_trails.add(et)
                self.last_engine_trail = time.time()
                self.image_orig = pg.image.load(self.ship_config['image_engines']).convert_alpha()
                self.rect_orig = self.image_orig.get_rect()  # TODO: every update????
        else:
            # Image / animation of ship without engine fire
            self.image_orig = pg.image.load(self.ship_config['image_ship']).convert_alpha()
            self.rect_orig = self.image_orig.get_rect()  # TODO: every update????
                   

        if not self.dead and self.controllable:
            self.spin(self.turning, self.ship_config['turn_speed'], self.slow_turn)


        # Rotation
        self.image, self.rect = self._rotatesprite(self.image_orig, self.rect_orig, self.heading)
        self.mask = pg.mask.from_surface(self.image)

        # Movement
        self.x_pos += self.vel_x / 3
        self.y_pos += self.vel_y / 3
        
        # We show up on the other side if we hit the edges
        if self.vel_x > 0 and self.x_pos >= self.config.window_size_xy: 
            self.x_pos -= self.config.window_size_xy
            
        if self.vel_x < 0 and self.x_pos <= 0: 
            self.x_pos += self.config.window_size_xy
       
        if self.vel_y > 0 and self.y_pos >= self.config.window_size_xy: 
            self.y_pos -= self.config.window_size_xy
            
        if self.vel_y < 0 and self.y_pos <= 0: 
            self.y_pos += self.config.window_size_xy
        

        # Position 
        self.rect.center = (self.x_pos, self.y_pos)

        # Energy recharge
        now = pg.time.get_ticks()
        if (
            now - self.last_energy_tick > 1000 and self.energy < self.ship_config['max_energy']
        ):  # hardcoded ignoring max values
            self.last_energy_tick = now
            self.energy += self.ship_config['recharge']
            if self.energy > self.ship_config['max_energy']:
                self.energy = self.ship_config['max_energy']

        # Self firing
        if self.firing and not self.dead and self.controllable:
            self.fire()

