from .base import BaseState

import pygame as pg
import time


class Splash(BaseState):
    def __init__(self) -> None:
        super().__init__()

        self.start_time = time.time()
        self.next_state = "MENU"
        self.title = self.font.render("Shclorg's Conundrum - a pygame Star Control clone", True, pg.Color("blue"))
        
    def draw(self, surface, _) -> None:
        self.title_rect = self.title.get_rect(center=surface.get_rect().center)
        surface.fill((0,0,0,0))
        surface.blit(self.title, self.title_rect)

        if time.time() > self.start_time + 1:
            self.done = True
