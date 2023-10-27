from .gameobject import Ship

import pygame as pg


class EnemyPlayer(Ship):
    def __init__(self, x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity) -> None:
        super().__init__(x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity)


class EnemyAI(Ship):
    def __init__(self, x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity,skill) -> None:
        super().__init__(x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity)
        self.skill = skill

    def update(self) -> None:
        pass

    def draw(self, surface) -> None:
        pass


class Player(Ship):
    def __init__(self, x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity) -> None:
        super().__init__(x_pos, y_pos, health, shield, direction, velocity, heading, max_velocity)
        
        self.max_velocity = 100  # TODO: read from ship config 
        self.min_velocity = -10  # TODO: read from ship config 

        self.accelleration = 0
    
        self.width = 80  # TODO: into game object
        self.height = 80

        self.image = pg.image.load('assets/ships/earthling.png').convert_alpha()
        self.rect = self.image.get_rect()

    def get_event(self, event) -> None:
        # Checking if a new key is pressed down
        if event.type == pg.KEYDOWN:
            match event.key:
                # Accelleration and decelleration
                case pg.K_UP: self.accelleration += 1
                case pg.K_DOWN: self.accelleration -= 1
                # Turning
                case pg.K_LEFT: self.state.heading -= 1
                case pg.K_RIGHT: self.state.heading += 1
                # Firing
                case pg.K_SPACE: self.firing(firing=True, main_gun=True)
                case pg.K_SPACE: self.firing(firing=True, main_gun=False)
                # Quitting
                case pg.K_ESCAPE: pg.event.post(pg.event.Event(pg.QUIT))

        # Checking if a previously pressed key is being released
        if event.type == pg.KEYUP:
            match event.key:
                # We have stopped accellerating or decellerating
                case pg.K_UP: self.accelleration = 0
                case pg.K_DOWN: self.accelleration = 0

    def update(self) -> None:
        # TODO: stupid placeholder
        self.state.velocity += self.accelleration
        self.state.x_pos += self.state.velocity

        self.rect.center = (self.state.x_pos, self.state.y_pos)


