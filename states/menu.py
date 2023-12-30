from .base import BaseState

import pygame as pg


class Menu(BaseState):
    def __init__(self) -> None:
        super().__init__()
        self.active_index = 0
        self.options = ["Start Game Player vs AI", "Start Game Player vs Player", "Quit Game"]
        self.name = "MENU"
        self.next_state = "GAMEPLAY"

    def render_text(self, index):
        color = pg.Color("red") if index == self.active_index else pg.Color("white")
        return self.font.render(self.options[index], True, color)

    def get_text_position(self, text, index, surface) -> pg.Rect:
        screen_rect = surface.get_rect()
        center = (screen_rect.center[0], screen_rect.center[1] + (index * 50))
        return text.get_rect(center=center)

    def handle_action(self) -> None:
        if self.active_index == 0:
            self.done = True
        elif self.active_index == 1:
            self.quit = True

    def get_event(self, event) -> None:
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_UP:
                self.active_index = 1 if self.active_index <= 0 else 0
            elif event.key == pg.K_DOWN:
                self.active_index = 0 if self.active_index >= 1 else 1
            elif event.key == pg.K_RETURN:
                self.handle_action()

    def draw(self, surface) -> None:
        surface.fill(pg.Color("black"))
        for index, option in enumerate(self.options):
            text_render = self.render_text(index)
            surface.blit(text_render, self.get_text_position(text_render, index, surface))
