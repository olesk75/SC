import pygame as pg
from icecream import ic

class BaseState:
    def __init__(self) -> None:
        self.done = False
        self.quit = False
        self.next_state = None
        self.screen_rect = pg.display.get_surface().get_rect()
        self.persist = {}
        self.font = pg.font.Font(None, 24)


        # Redundant?
        """ 
        self.user_input = {
            'quit': False,
            'right': False,
            'left': False,
            'up': False,
            'down': False,
            'attack': False
        }
        """

    def get_joysticks(self) -> None:
        self.level_current = 1

        # Checking for controllers/joysticks
        joysticks = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]

        if joysticks:
            ic(f'Found {pg.joystick.get_count()} available game controllers: {joysticks}')
            for n in range(pg.joystick.get_count()):
                joys = pg.joystick.Joystick(n)
                ic(joys.get_name())
                ic(joys.get_numaxes())
                ic(joys.get_numhats())
                ic(joys.get_numbuttons())
        else:
            ic('No game controllers found')


    def get_event(self, event) -> None:
        """ Placeholder to be overwritten in each state class """
        pass

    def startup(self, persistent) -> None:
        self.persist = persistent

    def update(self) -> None:
        """ Placeholder to be overwritten in each state class """
        pass

    def draw(self, surface) -> None:
        """ Placeholder to be overwritten in each state class """
        pass