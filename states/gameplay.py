from .base import BaseState
from objects.players import Player, EnemyAI
from objects.level import Level

from icecream import ic
import sys
sys.path.append('../objects')

import pygame as pg


class GamePlay(BaseState):
    def __init__(self) -> None:
        super().__init__()

        self.current_level = 1
        self.enemyAI_difficulty = 1

        self.player = Player(x_pos=100, y_pos=100, health=1000, shield=1000, \
                             direction=90, velocity=0, heading=10, max_velocity=100)
        self.enemy = EnemyAI(x_pos=100, y_pos=100, health=1000, shield=1000, \
                             direction=90, velocity=0, heading=10, \
                                skill=self.enemyAI_difficulty, max_velocity=100)
        self.level = Level(self.current_level)

        ic('GAME START')
    

    def get_event(self, event) -> None:
        # Checking if a new key is pressed down
        if event.type == pg.KEYDOWN:
            match event.key:
                # Accelleration and decelleration
                case pg.K_UP: self.player.accelleration += 1
                case pg.K_DOWN: self.player.accelleration -= 1
                # Turning
                case pg.K_LEFT: self.player.state.heading -= 1
                case pg.K_RIGHT: self.player.state.heading += 1
                # Firing
                case pg.K_SPACE: self.player.firing(firing=True, main_gun=True)
                case pg.K_SPACE: self.player.firing(firing=True, main_gun=False)
                # Quitting
                case pg.K_ESCAPE: self.quit = True

        # Checking if a previously pressed key is being released
        if event.type == pg.KEYUP:
            match event.key:
                # We have stopped accellerating or decellerating
                case pg.K_UP: self.player.accelleration = 0
                case pg.K_DOWN: self.player.accelleration = 0
            
        
        # Quit
        if event.type == pg.QUIT:
            self.quit = True


    def update(self) -> None:
        self.player.update()
        self.enemy.update()
        self.level.update()


    def draw(self, surface) -> None:
        self.level.draw(surface)
        self.enemy.draw(surface)
        self.player.draw(surface)
        