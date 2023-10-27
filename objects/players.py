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
        self.min_velocity = 100  # TODO: read from ship config 

        self.rect = pg.Rect((self.state.x_pos, self.state.y_pos), (80, 80))
        self.accelleration = 0

    def get_event(self, event) -> None:
        pass

    def update(self) -> None:
        # TODO: stupid placeholder
        self.state.velocity += self.accelleration
        self.state.x_pos += self.state.velocity

    def draw(self, surface) -> None:
        ship_sprite_rect = pg.Rect((self.state.x_pos, self.state.y_pos), (80, 80))
        
        
        pg.draw.rect(surface, pg.Color("blue"), ship_sprite_rect)