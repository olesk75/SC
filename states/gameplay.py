import pygame as pg
import sys

from .base import BaseState
from objects.level import Level
from time import perf_counter

sys.path.append("../objects")


class GamePlay(BaseState):
    '''
    GamePlay class is mostly just an abstract class to be subclassed
    However, it does keep track of triggered GLSL effects and manage their timing
    '''
    def __init__(self, ) -> None:
        super().__init__()

    def startup(self, fight_status, config) -> None:
        self.fight_status = fight_status
        self.config = config
        self.current_level = 1
        self.level = Level(self.config)
        self.level.startup(self.current_level, self.fight_status)
        self.name = "GAMEPLAY"
        self.next_state = "READY"
        self.effect_timer = 0
        
    # Get events from level instance, which in turn gets events from player instance(s)
    def get_event(self, event) -> None:
        self.level.get_event(event)

        # Quit
        if event.type == pg.QUIT:
            self.quit = True

    # The only state which overwrites the parent update() function
    def update(self, fight_status, config) -> None:
        self.fight_status = fight_status
        self.config = config
        
        self.level.update()
        self.zoom = self.level.zoom
        self.zoom_x = self.level.zoom_x
        self.zoom_y = self.level.zoom_y
        if self.level.teleport_triggered:
            self.level.teleport_triggered = False  # resetting
            self.effect_coords = self.level.teleport_coords
            self.active_effect = 8  # triggering teleport, will be disabled by timer

            self.effect_timer = perf_counter()

        if self.level.start_fadeout:
            self.active_effect = 3  # triggering fader
            self.level.start_fadeout = False

        if self.level.state == "win" and not self.level.explosion:
            self.active_effect = 0  # disabling effects manually
            self.done = True
            self.fight_status.win = True
            self.fight_status.p1_wins += 1
            print("WIN")
        if self.level.state == "loss" and not self.level.explosion:
            self.active_effect = 0  # disabling effects manually
            self.fight_status.win = False
            self.done = True
            self.fight_status.ai_wins += 1
            print("LOSS")

        # Timeouts for effects
        match self.active_effect:
            case 8:  # teleport
                if perf_counter() - self.effect_timer > 0.1:  # we reset the effect based on time
                    self.active_effect = 0


    def draw(self, surface, overlay) -> None:
        self.level.draw(surface, overlay)
