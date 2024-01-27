from abc import ABC, abstractmethod
import pygame as pg
import math


class GameObject(pg.sprite.Sprite, ABC):
    """Metaclass for all game objects, like enemies, player, bullets, powerups etc.

        x_pos   : global x position
        y_pos   : global y position
        health  : remaining health
        shield  : remaining shield
        alive   : dead or alive?

    The class inherits from the Sprite class. Object is added to a sprite group, which then is used for calling the draw(method)
    """

    def __init__(self, x_pos, y_pos, health, shield, energy, recharge, fire_rate, direction, velocity, heading, max_velocity) -> None:
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.health = health
        self.shield = shield
        self.energy = energy
        self.recharge = recharge
        self.fire_rate = fire_rate
        self.direction = direction
        self.velocity = velocity
        self.heading = heading
        self.max_velocity = max_velocity

        self.alive = True   # type: ignore
        self.firing = False
        self.shielded = False
        self.exploding = False
       
        super().__init__()

    def spin(self, direction, ship_rotate_speed) -> None:
        self.heading += ship_rotate_speed * direction
        if self.heading >= 360:
            self.heading -= 360
        if self.heading < 0:
            self.heading += 360

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

    def _rotatesprite(self, image: pg.Surface, rect: pg.Rect, angle) -> tuple[pg.Surface, pg.Rect]:
        """rotate an image while keeping its center"""
        rot_image = pg.transform.rotate(image, angle)
        rot_rect = rot_image.get_rect(center=rect.center)
        return rot_image, rot_rect

    @abstractmethod
    def update(self) -> None:
        print(f"Speed: {self.velocity}, rotation: {self.heading}")

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

        self.color = pg.Color(255, 255, 0)  # we start yellow

        self.type = type
        if type == "regular":
            self.lifespan = 30
            width = height = 3

        self.image = pg.Surface([width, height], pg.SRCALPHA)
        self.image.fill("#ffcc00")

        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y

    def update(self, zoom, h_scroll, v_scroll) -> None:
        self.image: pg.Surface
        self.ticks += 1

        if self.ticks >= self.lifespan:
            self.kill()

        self.rect.x = self.pos_x + h_scroll  # type: ignore
        self.rect.y = self.pos_y + v_scroll  # type: ignore
        self.image.set_alpha(255 - self.ticks * 10)


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
        explode: bool,
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
        self.explode = explode
        self.explosion_size: int

        self.ticks = 0

        self.type = "placeholder"
        self.image = pg.image.load("assets/projectiles/green_shot.png").convert_alpha()
        self.rect = self.image.get_rect()

        # We set rotation
        self.image, self.rect = self._rotatesprite(self.image, self.rect, heading)

        self.mask = pg.mask.from_surface(self.image)

        # Every projectile is different
        if self.type == "placeholder":
            self.expiry_time = 60  # 60 tics * 3 = 3 seconds
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
        self.x_pos -= int(math.sin(math.radians(self.heading)) * self.velocity)
        self.y_pos -= int(math.cos(math.radians(self.heading)) * self.velocity)

        # Position
        self.rect.center = (self.x_pos + h_scroll, self.y_pos + v_scroll)  # type: ignore


class Planet(pg.sprite.Sprite):
    def __init__(self, planet_type, x, y) -> None:
        super().__init__()
        self.image: pg.Surface
        if planet_type == 0 or planet_type == 1 or planet_type == 2:
            self.image_zoom1 = pg.image.load("assets/planets/planet1large.png").convert_alpha()
            self.image_zoom2 = pg.image.load("assets/planets/planet1med.png").convert_alpha()
            self.image_zoom3 = pg.image.load("assets/planets/planet1small.png").convert_alpha()
            self.image = self.image_zoom3  # TODO: placeholder

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        mask = pg.mask.from_surface(self.image)
        (x, y) = mask.get_size()
        self.mask = mask.scale((x * 0.9, y * 0.9))  # scales to 80% to account for corners on ships

        self.gravity = 0.009
        self.influence_radius = self.rect.width * 5


    def update(self, zoom) -> None:
        zoom = zoom
        pass





