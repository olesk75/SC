from .base import BaseState
from settings import SCREEN_HEIGHT, SCREEN_WIDTH


import pygame as pg


class GameOver(BaseState):
    def __init__(self) -> None:
        super().__init__()
        self.active_index = 0
        self.options = ["Start Game Player vs AI", "Start Game Player vs Player", "Quit Game"]
        self.name = "GAMEOVER"
        self.next_state = "GAMEPLAY"

    def render_text(self, index) -> pg.Surface:
        color = pg.Color("red") if index == self.active_index else pg.Color("white")
        return self.font.render(self.options[index], True, color)

    def get_text_position(self, text, index):
        self.screen_rect: pg.Rect
        center = (self.screen_rect.center[0], self.screen_rect.center[1] + (index * 50))
        return text.get_rect(center=center)

    def handle_action(self) -> None:
        if self.active_index == 0:
            self.done = True
        if self.active_index == 1:
            self.done = True
        elif self.active_index == 2:
            self.quit = True

    def get_event(self, event) -> None:
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_UP:
                self.active_index -= 1
            elif event.key == pg.K_DOWN:
                self.active_index += 1
            elif event.key == pg.K_RETURN:
                self.handle_action()

            if self.active_index < 0:
                self.active_index = 2
            if self.active_index > 2:
                self.active_index = 0

    def draw(self, surface) -> None:
        win_text = self.font.render(f"You WIN!", True, (255, 255, 255))
        surface.blit(win_text, ((int(SCREEN_WIDTH / 2) - 30, 100)))

        for index, _ in enumerate(self.options):
            text_render = self.render_text(index)
            surface.blit(text_render, self.get_text_position(text_render, index))
