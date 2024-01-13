from dataclasses import dataclass
from abc import ABC, abstractmethod
from icecream import ic
import pygame as pg
import math


@dataclass()
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
    energy: int
    recharge: int
    fire_rate: int
    direction: int
    velocity: int
    heading: int
    max_velocity: int

    # Derived values
    max_health: int
    max_energy: int

    # Field witrh default values
    alive: bool = True  # always initialized alive
    firing: bool = False  # is the game object currently firing a projectile
    shielded: bool = False  # shield active on object
    exploding: bool = False  # if object is currently exploding


class GameObject(pg.sprite.Sprite, ABC):
    """Metaclass for all game objects, like enemies, player, bullets, powerups etc.

    The class inherits from the Sprite class. Object is added to a sprite group, which then is used for calling the draw(method)
    """

    def __init__(
        self,
        x_pos,
        y_pos,
        health,
        shield,
        energy,
        recharge,
        fire_rate,
        direction,
        velocity,
        heading,
        max_velocity,
    ) -> None:
        self.state = GameObjectState(
            x_pos=x_pos,
            y_pos=y_pos,
            health=health,
            shield=shield,
            energy=energy,
            recharge=recharge,
            fire_rate=fire_rate,
            direction=direction,
            velocity=velocity,
            heading=heading,
            max_velocity=max_velocity,
            max_health=health,
            max_energy=energy,
        )
        super().__init__()

        self.rect = pg.Rect
        self.image = pg.Surface

    def accelerate(self, direction) -> None:
        # TODO: add acceleration factor depending on ship type
        ship_accelleration = 0.1
        ship_max_speed = 100
        ship_min_speed = -10
        self.speed += ship_accelleration * direction
        if self.speed > ship_max_speed:
            self.speed = ship_max_speed
        if self.speed < ship_min_speed:
            self.speed = ship_min_speed

    def spin(self, direction, ship_rotate_speed) -> None:
        self.state.heading += ship_rotate_speed * direction
        if self.state.heading >= 360:
            self.state.heading -= 360
        if self.state.heading < 0:
            self.state.heading += 360

    @abstractmethod
    def fire(self, primary: bool) -> None:
        if primary:
            # firing primary weapon
            pass
        else:
            # firing secondary weapon
            pass

    @abstractmethod
    def trigger_shield(self) -> None:
        pass

    def _rotatesprite(self, image:pg.Surface, rect:pg.Rect, angle) -> tuple[pg.Surface, pg.Rect]:
        """rotate an image while keeping its center"""
        rot_image = pg.transform.rotate(image, angle)
        rot_rect = rot_image.get_rect(center=rect.center)
        return rot_image, rot_rect

    @abstractmethod
    def update(self) -> None:
        print(f"Speed: {self.speed}, rotation: {self.state.heading}")

    def draw(self) -> None:
        raise RuntimeError("Never use draw method directly. Include in sprite group and call draw() on that instead")
        exit(1)


class Obstacle(GameObject):
    def __init__(self, x_pos: int, y_pos: int, health: int, shield, destructible: bool) -> None:
        super().__init__(
            x_pos, y_pos, health, shield, 0, 0, 0, 0, 0, 0, 0
        )  # obstacles have no direction, velocity nor heading
        self.destructible = destructible

    # TODO: missing compulsory functions


class EngineTrail(pg.sprite.Sprite):
    """EngineTrail helps see direction of travel for ships, as it leaves small blobs behind which slowly fade out"""

    def __init__(self, x, y, type) -> None:
        super().__init__()

        self.pos_x = x
        self.pos_y = y

        width = height = 5
        self.lifespan = 30
        self.ticks = 0

        self.color = pg.Color(255,255,0)  # we start yellow

        self.type = type
        if type == "regular":
            self.lifespan = 30
            width = height = 5

        self.image = pg.Surface([width, height])
        self.image.fill("#ffcc00")

        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y

    def update(self, zoom, h_scroll, v_scroll) -> None:
        self.ticks += 1

        if self.ticks >= self.lifespan:
            self.kill()

        self.rect.x = self.pos_x + h_scroll
        self.rect.y = self.pos_y + v_scroll

        #alpha = int((1 - (self.ticks / self.lifespan)) * 255)
    
        #self.color.g -= self.ticks
        #self.image.fill(self.color)
        #self.image.set_alpha(alpha)



class Projectile(GameObject):
    def __init__(
        self,
        x_pos: int,
        y_pos: int,
        health: int,
        shield: int,
        energy: int,
        recharge: int,
        fire_rate: int,
        direction: int,
        velocity: int,
        heading: int,
        max_velocity: int,
        expiry_time: int,
    ) -> None:
        super().__init__(
            x_pos,
            y_pos,
            health,
            shield,
            energy,
            recharge,
            fire_rate,
            direction,
            velocity,
            heading,
            max_velocity,
        )

        self.expiry_time = expiry_time
        self.explode: bool
        self.explosion_size: int

        self.ticks = 0

        self.type = "placeholder"
        self.image = pg.image.load("assets/projectiles/green_shot.png").convert_alpha()
        self.rect = self.image.get_rect()

        # We set rotation
        self.image, self.rect = self._rotatesprite(self.image, self.rect, heading)

        # Every projectile is different
        if self.type == "placeholder":
            self.expiry_time = 60  # 60 tics * 3 = 3 seconds
            self.explode = True
            self.explosion_size = 50

    def fire(self, primary: bool) -> None:
        return super().fire(primary)

    def trigger_shield(self) -> None:
        return super().trigger_shield()

    def update(self, zoom, h_scroll, v_scroll) -> None:
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
        self.state.x_pos -= int(math.sin(math.radians(self.state.heading)) * self.state.velocity)
        self.state.y_pos -= int(math.cos(math.radians(self.state.heading)) * self.state.velocity)

        # Position
        self.rect.center = (self.state.x_pos + h_scroll, self.state.y_pos + v_scroll)
