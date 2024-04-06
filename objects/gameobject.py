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

    The class inherits from the Sprite class. Object is added to a sprite group, 
    which then is used for calling the draw(method)
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

        self.under_gravity = False

        self.alive = True  # type: ignore
        self.firing = False
        self.shielded = False
        self.exploding = False

        super().__init__()

    def spin(self, turning, ship_rotate_speed, slow_turn) -> None:
        # direction > 0 -> clockwise
        ship_rotate_speed = (
            int(ship_rotate_speed / 2) if slow_turn else ship_rotate_speed
        )
        self.heading += ship_rotate_speed * turning
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

    def _rotatesprite(
        self, image: pg.Surface, rect: pg.Rect, angle
    ) -> tuple[pg.Surface, pg.Rect]:
        """rotate an image while keeping its center"""
        rot_image = pg.transform.rotate(image, angle)
        rot_rect = rot_image.get_rect(center=rect.center)
        return rot_image, rot_rect

    @abstractmethod
    def update(self) -> None:
        print(f"Speed: {self.velocity}, rotation: {self.heading}")

    def draw(self) -> None:
        raise RuntimeError(
            "Never use draw method directly. Include in sprite group and call draw() on that instead"
        )
        exit(1)


class Obstacle(GameObject):
    def __init__(
        self, x_pos: int, y_pos: int, health: int, shield, destructible: bool
    ) -> None:
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
        self.rect: pg.rect.Rect
        self.rect = self.image.get_rect()

        self.rect.x = self.pos_x
        self.rect.y = self.pos_y

    def update(self) -> None:
        self.image: pg.Surface
        self.ticks += 1

        if self.ticks >= self.lifespan:
            self.kill()

        self.rect.x = self.pos_x
        self.rect.y = self.pos_y
        self.image.set_alpha(255 - self.ticks * 10)


class Projectile(GameObject):
    def __init__(
        self,
        type: str,
        x_pos: int,
        y_pos: int,
        health: int,
        shield: int,
        energy: int,
        recharge: int,
        fire_rate: int,
        explode: bool,
        damage: int,
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
        self.damage = damage

        self.ticks = 0

        self.type = type
        types = ["green shot", "missile"]
        if self.type in types:
            match self.type:
                case "green shot":
                    self.image = pg.image.load(
                        "assets/projectiles/green_shot.png"
                    ).convert_alpha()

                case "missile":
                    self.image = pg.image.load(
                        "assets/projectiles/missile.png"
                    ).convert_alpha()

        else:
            ValueError(f"{self.type} is not an allowed shot type")

        self.image: pg.Surface
        self.image_orig = self.image
        self.rect_orig = self.image.get_rect()

        self.rect = self.image.get_rect()

        # We set rotation and get our collision mask
        self.image, self.rect = self._rotatesprite(self.image, self.rect, heading)
        self.mask = pg.mask.from_surface(self.image)

    def fire(self, primary: bool) -> None:
        return super().fire(primary)

    def trigger_shield(self) -> None:
        return super().trigger_shield()

    def update(self, target) -> None:
        self.ticks += 1

        # Special behaviors
        if self.type == "missile":
            turning = 0
            if self.velocity < self.max_velocity:
                self.velocity += 1

            # Remember: 0 degrees is up, angle increases counter-clockwise
            target_angle_rad = (
                math.atan2(target.y_pos - self.y_pos, target.x_pos - self.x_pos)
                + math.pi / 2
            )
            # angle from projectile to target
            target_angle = 360 - math.degrees(
                (target_angle_rad + 2 * math.pi) % (2 * math.pi)
            )

            # We now know the attack angle, but we must consider obstacles and attitude
            # print(f'vector angle: {target_angle:.2f}, heading ai: {self.ai.heading:.1f}, heading player: {player.heading:.1f}')

            # find which direction turn in the shortest - clockwise (decreasing angle) or counter-clockwise (increasing angle)
            attack_angle = (
                target_angle - self.heading + 360
                if target_angle - self.heading < 0
                else target_angle - self.heading
            )

            if attack_angle > 5 and attack_angle < 360 - 5:
                turning = -1 if attack_angle > 180 else 1  # turn to target

            self.spin(turning, 5, True)
            # Rotation
            self.image, self.rect = self._rotatesprite(
                self.image_orig, self.rect_orig, self.heading
            )
            self.mask = pg.mask.from_surface(self.image)

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
        self.rect.center = (self.x_pos, self.y_pos)  # type: ignore


class Beam:
    def __init__(self, type: str, x_pos: int, y_pos: int, heading: int, energy:int, recharge:int, fire_rate: int, damage: int) -> None:
        pass

    def update(self) -> None:
        pass


class Planet(pg.sprite.Sprite):
    def __init__(self, planet_type, pos) -> None:
        super().__init__()
        self.image: pg.Surface
        if planet_type == 0 or planet_type == 1 or planet_type == 2:
            self.image = pg.image.load(
                "assets/planets/planet1small.png"
            ).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.center = pos

        mask = pg.mask.from_surface(self.image)
        (x, y) = mask.get_size()
        # scales to 80% to account for corners on ships
        self.mask = mask.scale((x * 0.9, y * 0.9))

        self.gravity = 1000
        self.influence_radius = self.rect.width * 5

    def update(
        self,
    ) -> None:
        pass
