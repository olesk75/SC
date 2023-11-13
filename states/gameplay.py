from .base import BaseState
from objects.level import Level

from icecream import ic
import sys

sys.path.append("../objects")

import pygame as pg


class GamePlay(BaseState):
    def __init__(self) -> None:
        super().__init__()

    def startup(self, fight_status) -> None:
        self.fight_status = fight_status
        self.current_level = 1
        self.level = Level()
        self.level.startup(self.current_level)
        self.name = "GAMEPLAY"
        self.next_state = "READY"

    # Get events from level instance, which in turn gets events from player instance(s)
    def get_event(self, event) -> None:
        self.level.get_event(event)

        # Quit
        if event.type == pg.QUIT:
            self.quit = True

    def update(self) -> None:
        self.level.update()

        if self.level.state == "win":
            self.done = True
            self.fight_status.win = True
            self.fight_status.p1_wins += 1
            print("WIN")
        if self.level.state == "loss":
            self.fight_status.win = False
            self.done = True
            self.fight_status.ai_wins += 1
            print("LOSS")

    def draw(self, surface) -> None:
        self.level.draw(surface)
