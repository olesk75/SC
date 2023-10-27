import settings
import pygame as pg
from icecream import ic

class Game:
    """
    Class which mostly calls the same methods for whatever state is currently active,
    including GAMEPLAY.

    The run() method is looping until the game exits
    """

    def __init__(self, _screen, states, start_state, FPS) -> None:
        self.done = False
        self._screen = _screen
        self.clock = pg.time.Clock()
        self.FPS = FPS
        self.states = states
        self.state_name = start_state
        self.state = self.states[self.state_name]
        self.game_surface = pg.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.font = pg.font.Font('freesansbold.ttf', 32)


    def event_loop(self) -> None:
        for event in pg.event.get():
            self.state.get_event(event)


    def flip_state(self) -> None:
        current_state = self.state_name
        next_state = self.state.next_state
        ic('State transition:', current_state, next_state)
        self.state.done = False
        self.state_name = next_state
        persistent = self.state.persist
        self.state = self.states[self.state_name]
        self.state.startup(persistent)

    def update(self) -> None:
        if self.state.quit:
            self.done = True
            ic('Player terminated game')
        elif self.state.done:
            self.flip_state()
        self.state.update()  # call the update function in active state

    def draw(self) -> None:
        self.state.draw(self.game_surface)  # call the update function in active state (on game_surface, not the screen)

        if settings.SHOW_FPS:
            fps_text = self.font.render(f'FPS: {self.clock.get_fps():.2f}', True, (255, 255, 0))
            self.game_surface.blit(fps_text, (10, 100))

        #screen.blit(pg.transform.scale(game_surface, (width, height)), (0, 0))
        self._screen.blit(self.game_surface, (0, 0))

        pg.display.update()
        self.clock.tick(self.FPS)

        self._screen.blit(self.game_surface, (0, 0))

    def run(self) -> None:
        while not self.done:
            self.clock.tick(self.FPS)
            self.event_loop()
            self.update()
            self.draw()
