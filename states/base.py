import pygame as pg
from icecream import ic
from abc import ABC, abstractmethod


class BaseState:
    def __init__(self) -> None:
        self.config = None  # Updated in update() functions
        self.fight_status = None  # Updated in update() functions
        self.done = False
        self.quit = False
        self.next_state = None
        self.persist = {}
        self.font = pg.font.Font(None, 24)
        self.active_effect = 0  # all states can have active effects (GLSL shader effects)
        self.effect_coords = (0,0)
        self.zoom = 3  # default
        self.zoom_x = 0  # zoom coords, used for zoom lvl 1 and 2
        self.zoom_y = 0

    def get_joysticks(self) -> None:
        self.level_current = 1

        # Checking for controllers/joysticks
        joysticks = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]

        if joysticks:
            ic(f"Found {pg.joystick.get_count()} available game controllers: {joysticks}")
            for n in range(pg.joystick.get_count()):
                joys = pg.joystick.Joystick(n)
                ic(joys.get_name())
                ic(joys.get_numaxes())
                ic(joys.get_numhats())
                ic(joys.get_numbuttons())
        else:
            ic("No game controllers found")

    @abstractmethod
    def get_event(self, event) -> None:
        """Placeholder to be overwritten in each state class"""
        pass

    @abstractmethod
    def startup(self, fight_state, config) -> None:
        pass


    @abstractmethod
    def draw(self, surface) -> None:
        """Placeholder to be overwritten in each state class"""
        pass

    # We update the config and the fight status for all states - do NOT overwrite!
    def update(self, fight_status, config) -> None:
        self.config = config
        self.fight_status = fight_status