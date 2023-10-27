from .base import BaseState
from objects.level import Level

from icecream import ic
import sys
sys.path.append('../objects')

import pygame as pg


class GamePlay(BaseState):
    def __init__(self) -> None:
        super().__init__()
        self.current_level = 1
        self.level = Level()
        self.level.startup(self.current_level)
        ic('GAME START')

    # Get events from level instance, which in turn gets events from player instance(s)
    def get_event(self, event) -> None:
        self.level.get_event(event)
            
        # Quit
        if event.type == pg.QUIT:
            self.quit = True

    def update(self) -> None:
        self.level.update()

    def draw(self, surface) -> None:
        self.level.draw(surface)

        